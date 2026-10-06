#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
« Le prix touche +1 R en 3 à 9 heures, revient à l'entrée, puis finit au stop » : est-ce fréquent, et plus
fréquent qu'au hasard ?

Trades testés : les trades d'Amirou publiés avant l'entrée (statut « annoncé »), en cours horaires
(depuis le 15/12/2023), avec entrée, stop et objectif (data/verification_trades.csv). Le trade démarre à la
première bougie horaire qui touche le prix d'entrée dans les 5 jours suivant la publication.
Témoin : pour chaque trade, 20 entrées au hasard sur la même paire (2024-2026), même sens, même distance de
stop et d'objectif, au prix d'ouverture d'une bougie horaire.

Chemin heure par heure (repère achat ; si une bougie touche deux niveaux, le pire est compté d'abord) :
- +1 R atteint avant le stop ? en combien d'heures ?
- après +1 R : retour au prix d'entrée ?
- après ce retour : stop, ou de nouveau +1 R ?
- issue finale sur 10 jours : objectif, stop ou rien.
Sortie : data/aller_retour_1r/chemins.csv, résumé à l'écran.
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_masterclass import pip  # noqa: E402

SORTIE = 'data/aller_retour_1r'
HORIZON = 240   # heures


def chemin(hh, ll, e, sl, tp):
    """hh, ll : bougies après l'entrée (repère achat). Renvoie un dict d'événements."""
    R = e - sl
    out = dict(h_1r=None, retour_entree=False, apres_retour='', issue='rien')
    etat, t1 = 0, None
    issue = None
    for i in range(min(len(hh), HORIZON)):
        if issue is None:
            if ll[i] <= sl:
                issue = 'stop'
            elif tp and hh[i] >= tp:
                issue = 'objectif'
        if etat == 0:
            if ll[i] <= sl:
                break
            if hh[i] >= e + R:
                etat, t1 = 1, i
                out['h_1r'] = i + 1
        elif etat == 1:
            if ll[i] <= e:
                etat = 2
                out['retour_entree'] = True
                if ll[i] <= sl:
                    out['apres_retour'] = 'stop'
                    break
        elif etat == 2:
            if ll[i] <= sl:
                out['apres_retour'] = 'stop'
                break
            if hh[i] >= e + R:
                out['apres_retour'] = 'de nouveau +1 R'
                break
        if issue is not None and etat != 2:
            break
    out['issue'] = issue or 'rien'
    return out


def charger(p):
    h = pd.read_csv(f'data/prix/yahoo/{p}_1h.csv', parse_dates=['date'])
    return h[h['date'].dt.weekday < 5].sort_values('date').drop_duplicates('date').reset_index(drop=True)


def main():
    v = pd.read_csv('data/verification_trades.csv', parse_dates=['date'])
    v = v[(v['resolution'] == 'horaire') & (v['statut_rejeu'] == 'annoncé') & v['entree'].notna() & v['stop'].notna()
          & v['sens'].isin(['achat', 'vente'])]
    rng = np.random.default_rng(1)
    lignes = []
    cache = {}
    for _, t in v.iterrows():
        p = t['paire']
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = cache.setdefault(p, charger(p))
        s = 1 if t['sens'] == 'achat' else -1
        e, sl = t['entree'] * s, t['stop'] * s
        tp = t['objectif'] * s if t['objectif'] == t['objectif'] else None
        if e - sl <= 0:
            continue
        H = (h['high'] if s > 0 else -h['low']).to_numpy()
        L = (h['low'] if s > 0 else -h['high']).to_numpy()
        O = (h['open'] * s).to_numpy()
        i0 = h['date'].searchsorted(t['date'].floor('h'))
        k = next((i for i in range(i0, min(i0 + 120, len(h))) if L[i] <= e <= H[i]), None)
        if k is None:
            continue
        c = chemin(H[k + 1:], L[k + 1:], e, sl, tp)
        lignes.append(dict(groupe='Amirou', paire=p, date=h['date'][k], tp_r=(tp - e) / (e - sl) if tp else np.nan, **c))
        for _ in range(20):
            j = int(rng.integers(0, len(h) - HORIZON))
            e2 = O[j]
            c = chemin(H[j + 1:], L[j + 1:], e2, e2 - (e - sl), e2 + (tp - e) if tp else None)
            lignes.append(dict(groupe='témoin', paire=p, date=h['date'][j], tp_r=(tp - e) / (e - sl) if tp else np.nan, **c))
    d = pd.DataFrame(lignes)
    d = d[d['tp_r'] > 1].copy()      # objectif au-delà de +1 R, sinon la comparaison n'a pas de sens
    a1 = d['h_1r'].notna()
    tp_avant_retour = a1 & ~d['retour_entree'] & (d['issue'] == 'objectif')
    d['r_plan'] = np.select([d['issue'] == 'objectif', d['issue'] == 'stop'], [d['tp_r'], -1.0], 0.0)
    d['r_sortie_1r'] = np.where(a1, 1.0, np.where(d['issue'] == 'stop', -1.0, 0.0))
    d['r_be_a_1r'] = np.where(a1, np.where(tp_avant_retour, d['tp_r'], 0.0), np.where(d['issue'] == 'stop', -1.0, 0.0))
    d['r_moitie_1r_puis_be'] = np.where(a1, 0.5 + 0.5 * np.where(tp_avant_retour, d['tp_r'], 0.0), d['r_be_a_1r'])
    os.makedirs(SORTIE, exist_ok=True)
    d.to_csv(f'{SORTIE}/chemins.csv', index=False)
    for g, x in d.groupby('groupe'):
        a1 = x[x['h_1r'].notna()]
        ret = a1[a1['retour_entree']]
        print(f"\n== {g} : {len(x)} trades")
        print(f"+1 R atteint avant le stop : {len(a1) / len(x):.0%}")
        print(f"  délai médian {a1['h_1r'].median():.0f} h ; entre 3 et 9 h : {a1['h_1r'].between(3, 9).mean():.0%}")
        print(f"  puis retour à l'entrée : {len(ret) / len(a1):.0%}")
        print(f"    puis stop : {(ret['apres_retour'] == 'stop').mean():.0%} ; de nouveau +1 R : "
              f"{(ret['apres_retour'] == 'de nouveau +1 R').mean():.0%}")
        st = x[x['issue'] == 'stop']
        print(f"Trades finis au stop : {len(st) / len(x):.0%} ; dont passés d'abord par +1 R : "
              f"{st['h_1r'].notna().mean():.0%}")
        print(f"Schéma complet (+1 R en 3-9 h, retour à l'entrée, stop) : "
              f"{((x['h_1r'].between(3, 9)) & x['retour_entree'] & (x['apres_retour'] == 'stop')).mean():.0%} des trades ; "
              f"toutes durées : {(x['h_1r'].notna() & x['retour_entree'] & (x['apres_retour'] == 'stop')).mean():.0%}")
        print('R moyen par trade :', {k: round(x[k].mean(), 2) for k in
                                       ['r_plan', 'r_sortie_1r', 'r_be_a_1r', 'r_moitie_1r_puis_be']},
              '; objectif moyen', round(x['tp_r'].median(), 1), 'R')


if __name__ == '__main__':
    main()
