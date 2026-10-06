#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
« Trois barres » lundi-mardi-mercredi (T2 de scripts/tester_masterclass.py) : peut-on améliorer l'entrée ?

Signal, identique à T2, en vente (l'achat est symétrique) :
- lundi haussier « plein » (corps >= 60 % du range, clôture dans le quart haut) ;
- mardi rouge qui clôture sous la clôture du lundi ;
- stop 2 pips au-dessus du plus haut du mardi ; objectif = plus bas du lundi ; sortie à la clôture du vendredi ;
- filtre de la masterclass, calculé avec l'entrée à la clôture du mardi : distance >= 60 pips et RR >= 1,2.

Entrées comparées sur les mêmes signaux (stop et objectif inchangés, R recalculé depuis l'entrée réelle) :
- clôture du mardi (règle testée jusqu'ici) ;
- Londres : au marché à 07h UTC le mercredi ;
- repli 30 % : ordre limite à 30 % de la distance entrée-stop, valable le mercredi (24 h) ;
- FVG 4h du mardi : ordre limite au bord du FVG 4h le plus récent du mardi, non comblé, valable 24 h ;
- repli 30 % la nuit, sinon Londres ; FVG 4h la nuit, sinon Londres (aucun signal raté) ;
- ordre stop au-delà de l'extrême du mardi (vente : sous le plus bas), valable le mercredi ;
- confirmation 1h : clôture de la première bougie 1h (mercredi ou jeudi) au-delà de l'extrême du mardi.

Rejeu horaire (Yahoo, depuis le 15/12/2023, 22 paires) ; stop prioritaire dans une même heure ; dans l'heure
d'exécution d'un ordre, seul le stop compte ; spread déduit. Ordre non exécuté = 0 R.
Sortie : data/lmm_entrees/trades.csv, data/lmm_entrees/resultats.csv
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO, charger, fvgs  # noqa: E402
from tester_entrees_englobante import suivre  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

SORTIE = 'data/lmm_entrees'
VARIANTES = ['clôture du mardi', 'Londres 07h', 'repli 30 % (24 h)', 'FVG 4h du mardi (24 h)',
             'repli 30 % la nuit, sinon Londres', 'FVG 4h la nuit, sinon Londres', 'ordre stop au-delà du mardi',
             'confirmation 1h']


def signaux(p):
    h = charger(p)
    h['dt'] = pd.to_datetime(h['jour'])
    jours = sorted(h['jour'].unique())
    par_jour = {j: g for j, g in h.groupby('jour')}
    pp, sp = pip(p), spread(p)
    lignes = []
    for i in range(len(jours) - 2):
        lun, mar = pd.Timestamp(jours[i]), pd.Timestamp(jours[i + 1])
        if lun.weekday() != 0 or mar - lun != pd.Timedelta(days=1):
            continue
        g1, g2 = par_jour[jours[i]], par_jour[jours[i + 1]]
        if len(g1) < 18 or len(g2) < 18:
            continue
        semaine = [j for j in jours[i + 2:i + 5] if pd.Timestamp(j) - lun < pd.Timedelta(days=5)]
        if not semaine or pd.Timestamp(semaine[0]).weekday() != 2:
            continue
        o, hi, lo, c = g1['open'].iloc[0], g1['high'].max(), g1['low'].min(), g1['close'].iloc[-1]
        o2, c2 = g2['open'].iloc[0], g2['close'].iloc[-1]
        rng = hi - lo
        if rng <= 0 or abs(c - o) < 0.6 * rng:
            continue
        if c > o and c >= hi - 0.25 * rng and c2 < o2 and c2 < c:
            sens = -1
        elif c < o and c <= lo + 0.25 * rng and c2 > o2 and c2 > c:
            sens = 1
        else:
            continue
        apres = pd.concat([par_jour[j] for j in semaine])
        n24 = len(par_jour[semaine[0]])
        n48 = n24 + (len(par_jour[semaine[1]]) if len(semaine) > 1 else 0)
        heure = apres['date'].dt.hour.to_numpy()
        if sens == 1:
            ao, ah, al, ac = (apres[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
            mh, ml = g2['high'].to_numpy(), g2['low'].to_numpy()
            tp = hi
        else:
            ao, ah, al, ac = -apres['open'].to_numpy(), -apres['low'].to_numpy(), -apres['high'].to_numpy(), \
                -apres['close'].to_numpy()
            mh, ml = -g2['low'].to_numpy(), -g2['high'].to_numpy()
            tp = -lo
        sl = ml.min() - 2 * pp                     # repère achat : stop sous l'extrême du mardi
        e0 = c2 * sens
        risque0, dist0 = e0 - sl, tp - e0
        if risque0 <= 0 or dist0 <= 0:
            continue
        filtre = dist0 >= 60 * pp and dist0 / risque0 >= 1.2
        base = dict(paire=p, date=semaine[0], sens='achat' if sens == 1 else 'vente', filtre=filtre,
                    rr=round(dist0 / risque0, 2))
        i07 = next((k for k in range(n24) if heure[k] >= 7), 0)

        def trade(i0, e):
            """Position ouverte à la bougie i0 (incluse) au prix e."""
            if e <= sl:
                return -1.0 - sp / risque0
            if e >= tp:
                return 0.0
            return suivre(ah, al, ac, i0, e, sl, tp) - sp / (e - sl)

        def limite(L, n, puis_londres):
            if sl < L < e0:
                for k in range(n):
                    if al[k] <= L:
                        e = min(L, ao[k])
                        if al[k] <= sl or e <= sl:
                            return -1.0 - sp / max(e - sl, pp)
                        return trade(k + 1, e)
            return res['Londres 07h'] if puis_londres else 0.0

        res = {'clôture du mardi': trade(0, e0), 'Londres 07h': trade(i07, ao[i07])}
        L30 = e0 - 0.3 * risque0
        b = g2.assign(bloc=g2['date'].dt.hour // 4).groupby('bloc')
        if sens == 1:
            h4 = b.agg(high=('high', 'max'), low=('low', 'min'))
            zones = fvgs(None, h4['high'].to_numpy(), h4['low'].to_numpy(), None)
        else:
            h4 = b.agg(high=('low', 'min'), low=('high', 'max'))
            zones = fvgs(None, -h4['high'].to_numpy(), -h4['low'].to_numpy(), None)
        zones = [z for z in zones if z[1] < e0]
        Lf = max(z[1] for z in zones) if zones else None
        res['repli 30 % (24 h)'] = limite(L30, n24, False)
        res['FVG 4h du mardi (24 h)'] = limite(Lf, n24, False) if Lf else 0.0
        res['repli 30 % la nuit, sinon Londres'] = limite(L30, i07, True)
        res['FVG 4h la nuit, sinon Londres'] = limite(Lf, i07, True) if Lf else res['Londres 07h']
        niveau, r = mh.max() + pp, 0.0
        for k in range(n24):
            if ah[k] >= niveau:
                e = max(niveau, ao[k])
                r = (-1.0 - sp / (e - sl)) if al[k] <= sl else trade(k + 1, e)
                break
        res['ordre stop au-delà du mardi'] = r
        r = 0.0
        for k in range(n48):
            if al[k] <= sl:
                break
            if ac[k] > mh.max():
                r = trade(k + 1, ac[k])
                break
        res['confirmation 1h'] = r
        for v in VARIANTES:
            lignes.append(dict(base, variante=v, r=round(res[v], 4)))
    return lignes


def main():
    lignes = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            lignes += signaux(p)
    t = pd.DataFrame(lignes)
    os.makedirs(SORTIE, exist_ok=True)
    t.to_csv(f'{SORTIE}/trades.csv', index=False)
    w = t.pivot_table(index=['paire', 'date', 'sens', 'filtre'], columns='variante', values='r').reset_index()
    res = []
    for nom, m in {'avec le filtre de la masterclass (60 pips, RR >= 1,2)': w['filtre'],
                   'toutes les configurations': w['filtre'] | ~w['filtre']}.items():
        s = w[m]
        for v in VARIANTES:
            d = s[v] - s['clôture du mardi']
            res.append(dict(sous_ensemble=nom, variante=v, signaux=len(s), trades=int((s[v] != 0).sum()),
                            gagnants=round(float((s.loc[s[v] != 0, v] > 0).mean()), 3),
                            r_par_signal=round(s[v].mean(), 3), erreur_type=round(s[v].std() / np.sqrt(len(s)), 3),
                            ecart_vs_cloture=round(d.mean(), 3), erreur_type_ecart=round(d.std() / np.sqrt(len(s)), 3)))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 220)
    for nom, g in r.groupby('sous_ensemble', sort=False):
        print('\n==', nom)
        print(g.drop(columns='sous_ensemble').to_string(index=False))
    f = w[w['filtre']]
    print('\nPar année (filtre), clôture du mardi :')
    print(f.groupby(f['date'].str[:4])['clôture du mardi'].agg(['count', 'mean']).round(3))


if __name__ == '__main__':
    main()
