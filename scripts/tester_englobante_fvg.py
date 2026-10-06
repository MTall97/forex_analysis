#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Englobante journalière : entrer sur un FVG (fair value gap) 1h ou 4h de la bougie englobante, au lieu
d'entrer à sa clôture, améliore-t-il le résultat ?

Signal (même règle que scripts/suivi_demo_englobante_mlq.py, achats et ventes) :
- bougie J qui englobe le corps de J-1 de couleur opposée (corps de J >= corps de J-1) ;
- stop à 2 pips au-delà de l'extrême de J ; sortie au stop, à l'objectif, sinon à la clôture de J+3 ;
- sous-ensemble « MLQ » : l'extrême de J est à 25 pips ou moins d'un multiple de 250 pips.

Entrées comparées :
- « clôture » : à la clôture de J, objectif 2 R (la règle actuelle) ;
- « FVG 1h » / « FVG 4h » : ordre limite sur un FVG formé pendant J et pas encore comblé à la clôture de J
  (achat : plus haut de la bougie k-1 < plus bas de la bougie k+1), au haut du FVG ou en son milieu ; le FVG
  le plus proche du prix (« récent ») ou le plus éloigné (« profond ») ; ordre valable 24 h (ou 48 h) ;
  objectif 2 R depuis la nouvelle entrée, ou objectif inchangé (même prix que l'entrée à la clôture) ;
- témoin « repli fixe » : ordre limite à une fraction fixe de la distance clôture-stop, pour tous les
  signaux. Si le FVG n'apporte rien de plus qu'« acheter plus bas », le témoin fait aussi bien.

Rejeu en horaire (Yahoo, depuis le 15/12/2023) ; dans une même heure, le stop passe avant l'objectif ; dans
l'heure où l'ordre limite est exécuté, seul le stop est vérifié ; spread déduit.
R par signal : les ordres non exécutés comptent 0 R (c'est ce que l'on gagne vraiment par signal).

Sortie : data/englobante_fvg/trades.csv, data/englobante_fvg/resultats.csv
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_masterclass import pip, spread  # noqa: E402

PAIRES_DEMO = ['AUDJPY', 'AUDUSD', 'EURJPY', 'EURNZD', 'EURUSD', 'GBPJPY', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDJPY']
PAIRES_AUTRES = ['AUDCAD', 'AUDNZD', 'EURAUD', 'EURCAD', 'EURGBP', 'GBPAUD', 'GBPCAD', 'NZDJPY', 'CADJPY', 'EURCHF',
                 'USDCHF', 'GBPNZD']
SORTIE = 'data/englobante_fvg'


def charger(p):
    h = pd.read_csv(f'data/prix/yahoo/{p}_1h.csv', parse_dates=['date'])
    h = h[h['date'].dt.weekday < 5].sort_values('date').drop_duplicates('date').reset_index(drop=True)
    h['jour'] = h['date'].dt.strftime('%Y-%m-%d')
    return h


def fvgs(o, hh, ll, c):
    """FVG haussiers (en repère « achat ») non comblés à la fin de la série : liste de (bas, haut)."""
    out = []
    for k in range(1, len(hh) - 1):
        bas, haut = hh[k - 1], ll[k + 1]
        if haut > bas and (k + 2 >= len(ll) or ll[k + 2:].min() > haut):
            out.append((bas, haut))
    return out


def rejouer(hh, ll, cc, n_valid, entree, sl, tp, limite):
    """hh, ll, cc : heures après J (repère achat). Renvoie (executé, R brut, issue)."""
    risque = entree - sl
    i0 = 0
    if limite:
        for i in range(min(n_valid, len(hh))):
            if ll[i] <= entree:
                if ll[i] <= sl:
                    return True, -1.0, 'stop'
                i0 = i + 1
                break
        else:
            return False, 0.0, 'non exécuté'
    for i in range(i0, len(hh)):
        if ll[i] <= sl:
            return True, -1.0, 'stop'
        if hh[i] >= tp:
            return True, (tp - entree) / risque, 'objectif'
    return True, (cc[-1] - entree) / risque, 'sortie J+3'


def signaux(p):
    h = charger(p)
    jours = sorted(h['jour'].unique())
    par_jour = {j: g for j, g in h.groupby('jour')}
    pp, sp = pip(p), spread(p)
    lignes = []
    for i in range(1, len(jours) - 3):
        g, g0 = par_jour[jours[i]], par_jour[jours[i - 1]]
        if len(g) < 18 or len(g0) < 18:
            continue
        O, C, O0, C0 = g['open'].iloc[0], g['close'].iloc[-1], g0['open'].iloc[0], g0['close'].iloc[-1]
        if abs(C - O) < abs(C0 - O0) or (C - O) * (C0 - O0) >= 0:
            continue
        sens = 1 if C > O else -1                  # 1 achat, -1 vente ; repère achat : prix * sens
        apres = pd.concat([par_jour[j] for j in jours[i + 1:i + 4]])
        n24 = len(par_jour[jours[i + 1]])
        n48 = n24 + len(par_jour[jours[i + 2]])
        if sens == 1:
            jh, jl, jo, jc = (g[k].to_numpy() for k in ['high', 'low', 'open', 'close'])
            ah, al, ac = apres['high'].to_numpy(), apres['low'].to_numpy(), apres['close'].to_numpy()
        else:
            jh, jl, jo, jc = (-g[k].to_numpy() for k in ['low', 'high', 'open', 'close'])
            ah, al, ac = -apres['low'].to_numpy(), -apres['high'].to_numpy(), -apres['close'].to_numpy()
        extreme = jl.min()
        sl = extreme - 2 * pp
        entree0 = jc[-1]
        risque0 = entree0 - sl
        if risque0 < 5 * pp:
            continue
        tp0 = entree0 + 2 * risque0
        pas = 250 * pp
        mlq = abs(abs(extreme) - round(abs(extreme) / pas) * pas) <= 25 * pp
        base = dict(paire=p, date=jours[i], sens='achat' if sens == 1 else 'vente', mlq=mlq,
                    risque_pips=round(risque0 / pp, 1))

        def ajouter(variante, entree, tp, limite, n_valid, profondeur=np.nan):
            ex, r, issue = rejouer(ah, al, ac, n_valid, entree, sl, tp, limite)
            r_net = r - sp / (entree - sl) if ex else 0.0
            lignes.append(dict(base, variante=variante, execute=ex, issue=issue, r=round(r_net, 4),
                               profondeur=round(profondeur, 3) if profondeur == profondeur else np.nan))

        ajouter('clôture', entree0, tp0, False, 0)
        # 4h : blocs 00-04, 04-08… de la journée J
        b = g.assign(bloc=g['date'].dt.hour // 4).groupby('bloc')
        if sens == 1:
            h4 = b.agg(high=('high', 'max'), low=('low', 'min'))
            q4h, q4l = h4['high'].to_numpy(), h4['low'].to_numpy()
        else:
            h4 = b.agg(high=('low', 'min'), low=('high', 'max'))
            q4h, q4l = -h4['high'].to_numpy(), -h4['low'].to_numpy()
        def rien(tf, choix, niveau, issue):
            for suffixe in ['2R 24h', 'objectif inchangé 24h', '2R 48h']:
                lignes.append(dict(base, variante=f'FVG {tf} {choix} {niveau} {suffixe}', execute=False,
                                   issue=issue, r=0.0, profondeur=np.nan))

        for tf, zones in [('1h', fvgs(jo, jh, jl, jc)), ('4h', fvgs(None, q4h, q4l, None))]:
            zones = [z for z in zones if z[1] < entree0]
            if not zones:
                for choix in ['récent', 'profond']:
                    for niveau in ['haut', 'milieu']:
                        rien(tf, choix, niveau, 'pas de FVG')
                continue
            for choix, z in [('récent', max(zones, key=lambda z: z[1])), ('profond', min(zones, key=lambda z: z[0]))]:
                for niveau, e in [('haut', z[1]), ('milieu', (z[0] + z[1]) / 2)]:
                    if e - sl < 3 * pp:
                        rien(tf, choix, niveau, 'FVG collé au stop')
                        continue
                    prof = (entree0 - e) / risque0
                    for obj, tp in [('2R', e + 2 * (e - sl)), ('objectif inchangé', tp0)]:
                        ajouter(f'FVG {tf} {choix} {niveau} {obj} 24h', e, tp, True, n24, prof)
                    ajouter(f'FVG {tf} {choix} {niveau} 2R 48h', e, e + 2 * (e - sl), True, n48, prof)
        for f in [0.2, 0.3, 0.4, 0.5]:
            e = entree0 - f * risque0
            ajouter(f'témoin repli {int(f * 100)} % 2R 24h', e, e + 2 * (e - sl), True, n24, f)
            ajouter(f'témoin repli {int(f * 100)} % objectif inchangé 24h', e, tp0, True, n24, f)
    return lignes


def bilan(t):
    ex = t[t['execute']]
    return pd.Series({
        'signaux': len(t), 'executes': len(ex), 'taux_execution': round(len(ex) / len(t), 3) if len(t) else np.nan,
        'objectifs': round((ex['issue'] == 'objectif').mean(), 3) if len(ex) else np.nan,
        'r_par_trade': round(ex['r'].mean(), 3) if len(ex) else np.nan,
        'r_par_signal': round(t['r'].mean(), 3), 'erreur_type': round(t['r'].std() / np.sqrt(len(t)), 3),
        'r_total': round(t['r'].sum(), 1)})


def main():
    lignes = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            lignes += signaux(p)
    t = pd.DataFrame(lignes)
    t['groupe'] = np.where(t['paire'].isin(PAIRES_DEMO), '10 paires', 'autres paires')
    os.makedirs(SORTIE, exist_ok=True)
    t.to_csv(f'{SORTIE}/trades.csv', index=False)
    res = []
    sous = {'achats MLQ (règle suivie en démo), 10 paires': (t['sens'] == 'achat') & t['mlq'] & (t['groupe'] == '10 paires'),
            'achats MLQ, autres paires': (t['sens'] == 'achat') & t['mlq'] & (t['groupe'] == 'autres paires'),
            'toutes englobantes, 10 paires': t['groupe'] == '10 paires',
            'toutes englobantes, autres paires': t['groupe'] == 'autres paires'}
    for nom, m in sous.items():
        for v, g in t[m].groupby('variante'):
            res.append(dict(sous_ensemble=nom, variante=v, **bilan(g)))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 250)
    for nom in sous:
        print('\n==', nom)
        print(r[r['sous_ensemble'] == nom].drop(columns='sous_ensemble').sort_values('r_par_signal', ascending=False)
              .to_string(index=False))


if __name__ == '__main__':
    main()
