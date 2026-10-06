#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suivi de tendance « cassure du plus haut ou du plus bas de la veille dans le sens des 5 derniers jours », avec des
objectifs de 1 R (et 2 R, 3 R pour comparer).

Règle (vente ; l'achat est symétrique) :
- tendance : clôture de J-1 inférieure d'au moins 1 ATR(14) journalier à la clôture de J-6 (variante : 2 ATR) ;
- déclencheur pendant J, entre 07h et 17h UTC (Londres et New York) :
  - « cassure » : le prix passe sous le plus bas de la veille -> vente 1 pip sous ce plus bas (ordre stop ;
    au prix d'ouverture de l'heure si elle ouvre déjà en dessous) ;
  - « faux dépassement » : le prix passe d'abord au-dessus du plus haut de la veille, puis une bougie 1h clôture
    de nouveau sous ce plus haut -> vente à cette clôture (comme le GBPUSD du 22/06/2026) ;
- stop à 0,25 ATR(14) de l'entrée (environ 15-25 pips sur les paires majeures ; variante 0,5 ATR) ;
- objectif 1 R (2 R, 3 R pour comparer) ;
- sortie à 20h UTC le jour même si rien n'est touché, avant le rollover de 21h (variante : 20h le lendemain) ;
- un trade par paire et par jour au plus ; suivi à partir de l'heure qui suit l'entrée ; si une même heure touche
  le stop et l'objectif, on donne deux résultats : stop d'abord (pessimiste) et objectif d'abord (optimiste) ;
  spread déduit.
Témoins : la même cassure sans filtre de tendance, et à contre-tendance.
Cours : horaire Yahoo, 22 paires, 12/2023-10/2026 (jours 00h-24h UTC reconstruits depuis l'horaire).
Sortie : data/suivi_tendance/trades.csv, data/suivi_tendance/resultats.csv
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO, charger  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

SORTIE = 'data/suivi_tendance'


def simuler(hh, ll, cc, i0, e, R, k, fin):
    """Repère achat ; position ouverte pendant (cassure) ou à la fin (faux dépassement) de la bougie i0 ; suivi à
    partir de la bougie i0 + 1 (dans la bougie de la cassure, le plus bas s'est le plus souvent formé avant
    l'entrée) ; sortie à la clôture de la bougie fin.
    Renvoie (R pessimiste, R optimiste) : si une même heure touche le stop et l'objectif, le stop d'abord, ou
    l'objectif d'abord."""
    sl, tp = e - R, e + k * R
    for i in range(i0 + 1, fin + 1):
        stop, obj = ll[i] <= sl, hh[i] >= tp
        if stop and obj:
            return -1.0, float(k)
        if stop:
            return -1.0, -1.0
        if obj:
            return float(k), float(k)
    r = (cc[fin] - e) / R
    return r, r


def paire(p):
    h = charger(p)
    pp, sp = pip(p), spread(p)
    jours = sorted(h['jour'].unique())
    idx = {j: np.where(h['jour'].to_numpy() == j)[0] for j in jours}
    d = pd.DataFrame([dict(jour=j, high=h['high'].to_numpy()[ix].max(), low=h['low'].to_numpy()[ix].min(),
                           close=h['close'].to_numpy()[ix[-1]], n=len(ix)) for j, ix in idx.items()])
    tr = np.maximum(d['high'] - d['low'], np.maximum(abs(d['high'] - d['close'].shift()), abs(d['low'] - d['close'].shift())))
    d['atr'] = tr.rolling(14).mean().shift(1)          # connu à l'ouverture de J
    heure = h['date'].dt.hour.to_numpy()
    O, H, L, C = (h[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    lignes = []
    for i in range(15, len(d) - 1):
        if d['n'][i] < 18 or d['n'][i - 1] < 18 or np.isnan(d['atr'][i]):
            continue
        atr = d['atr'][i]
        mouvement = (d['close'][i - 1] - d['close'][i - 6]) / atr
        pdh, pdl = d['high'][i - 1], d['low'][i - 1]
        ix = idx[d['jour'][i]]
        ix2 = idx[d['jour'][i + 1]]
        fin_j = next((k for k in ix if heure[k] == 20), ix[-1])
        fin_j1 = next((k for k in ix2 if heure[k] == 20), ix2[-1])
        fen = [k for k in ix if 7 <= heure[k] < 17]
        for s in (1, -1):
            # repère achat : s=1 achat (cassure du plus haut), s=-1 vente (cassure du plus bas)
            hh, ll, cc, oo = (H, L, C, O) if s > 0 else (-L, -H, -C, -O)
            niveau_cassure = (pdh if s > 0 else -pdl) + pp
            niveau_oppose = pdl if s > 0 else -pdh       # extrême opposé de la veille, en repère achat
            tendance = mouvement * s
            for declencheur in ['cassure', 'faux dépassement']:
                entree = None
                if declencheur == 'cassure':
                    for k in fen:
                        if hh[k] >= niveau_cassure:
                            entree = (k, max(niveau_cassure, oo[k]))
                            break
                else:
                    passe = False
                    for k in fen:
                        if ll[k] < niveau_oppose:
                            passe = True
                        if passe and cc[k] > niveau_oppose:
                            entree = (k + 1, cc[k]) if k + 1 <= fin_j else None
                            break
                if entree is None:
                    continue
                k0, e = entree
                if declencheur == 'faux dépassement':
                    k0 -= 1                               # entrée à la clôture de la bougie k0 : suivi dès k0 + 1
                for m_stop in (0.25, 0.5):
                    R = m_stop * atr
                    for obj in (1, 2, 3):
                        for duree, fin in [('jour', fin_j), ('48 h', fin_j1)]:
                            if fin <= k0:
                                continue
                            rp, ro = simuler(hh, ll, cc, k0, e, R, obj, fin)
                            r, r_opt = rp - sp / R, ro - sp / R
                            lignes.append(dict(paire=p, date=d['jour'][i], sens='achat' if s > 0 else 'vente',
                                               declencheur=declencheur, tendance_atr=round(tendance, 2),
                                               stop_atr=m_stop, objectif=obj, duree=duree,
                                               risque_pips=round(R / pp, 1), r=round(r, 4),
                                               r_optimiste=round(r_opt, 4)))
    return lignes


def main():
    lignes = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            lignes += paire(p)
    t = pd.DataFrame(lignes)
    os.makedirs(SORTIE, exist_ok=True)
    t.to_csv(f'{SORTIE}/trades.csv.gz', index=False)
    t['filtre'] = np.select([t['tendance_atr'] >= 2, t['tendance_atr'] >= 1, t['tendance_atr'] <= -1],
                            ['tendance >= 2 ATR', 'tendance 1-2 ATR', 'contre-tendance <= -1 ATR'], 'sans tendance nette')
    res = []
    for cle, g in t.groupby(['declencheur', 'stop_atr', 'duree', 'objectif']):
        groupes = {'tendance >= 1 ATR (règle)': g['tendance_atr'] >= 1, 'tendance >= 2 ATR': g['tendance_atr'] >= 2,
                   'toutes les cassures (témoin)': g['tendance_atr'] > -99,
                   'contre-tendance <= -1 ATR (témoin)': g['tendance_atr'] <= -1}
        for nom, m in groupes.items():
            x = g[m]
            res.append(dict(declencheur=cle[0], stop=f'{cle[1]} ATR', sortie=cle[2], objectif=f'{cle[3]} R', groupe=nom,
                            trades=len(x), gagnants=round((x['r'] > 0).mean(), 3), r_moyen=round(x['r'].mean(), 3),
                            r_moyen_optimiste=round(x['r_optimiste'].mean(), 3),
                            erreur_type=round(x['r'].std() / np.sqrt(len(x)), 3)))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 220)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
