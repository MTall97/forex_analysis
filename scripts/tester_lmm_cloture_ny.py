#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lundi-mardi-mercredi avec des journées qui finissent à 17h New York (21h UTC l'été, 22h l'hiver), comme les
graphiques journaliers d'OANDA / TradingView, au lieu de minuit UTC.

Règles inchangées (construire_page_strategies.lmm) : lundi plein (corps >= 60 % du range, clôture dans le quart
extrême), mardi contraire (clôture contre l'ouverture et contre la clôture du lundi) ; vente/achat à la clôture du
mardi, stop 2 pips au-delà du mardi, objectif au plus bas/haut du lundi ; filtre de la masterclass : objectif >= 60 pips
et >= 1,2 R ; sortie à la clôture du vendredi ; stop prioritaire dans une même bougie ; spread déduit.
Seule la frontière des journées change. Horaire Yahoo 2024-2026.
Sortie : data/lmm_cloture_ny/{trades.csv, resultats.csv}
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from construire_page_strategies import horaire  # noqa: E402
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402


def cle_jour(idx, mode):
    if mode == 'minuit UTC':
        return idx.strftime('%Y-%m-%d')
    ny = idx.tz_localize('UTC').tz_convert('America/New_York') + pd.Timedelta(hours=7)   # 17h NY -> minuit
    return ny.strftime('%Y-%m-%d')


def lmm(p, mode):
    h = horaire(p)
    pp, sp = pip(p), spread(p)
    cle = cle_jour(h.index, mode)
    pj = {j: g for j, g in h.groupby(cle)}
    jours = sorted(pj)
    out = []
    for i in range(len(jours) - 2):
        lun, mar = pd.Timestamp(jours[i]), pd.Timestamp(jours[i + 1])
        if lun.weekday() != 0 or mar - lun != pd.Timedelta(days=1):
            continue
        g1, g2 = pj[jours[i]], pj[jours[i + 1]]
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
            s = -1
        elif c < o and c <= lo + 0.25 * rng and c2 > o2 and c2 > c:
            s = 1
        else:
            continue
        e = c2
        sl = (g2['low'].min() - 2 * pp) if s > 0 else (g2['high'].max() + 2 * pp)
        tp = hi if s > 0 else lo
        R, dist = (e - sl) * s, (tp - e) * s
        if R <= 0 or dist <= 0:
            continue
        a = pd.concat([pj[j] for j in semaine])
        res, motif, tx = None, 'échéance', a.index[-1]
        for t, r_ in a.iterrows():
            if (r_['low'] <= sl) if s > 0 else (r_['high'] >= sl):
                res, motif, tx = -1.0, 'stop', t
                break
            if (r_['high'] >= tp) if s > 0 else (r_['low'] <= tp):
                res, motif, tx = dist / R, 'objectif', t
                break
        if res is None:
            res = (a['close'].iloc[-1] - e) * s / R
        out.append(dict(journee=mode, paire=p, lundi=jours[i], sens='achat' if s > 0 else 'vente', entree=round(e, 5),
                        stop=round(sl, 5), objectif=round(tp, 5), objectif_pips=round(dist / pp, 1),
                        ratio=round(dist / R, 2), filtre=bool(dist >= 60 * pp and dist / R >= 1.2),
                        corps_mardi_pips=round((c2 - o2) / pp, 1), sortie=str(tx)[:16], motif=motif,
                        r=round(res - sp / R, 3)))
    return out


def main():
    L = []
    for mode in ['minuit UTC', '17h New York']:
        for p in PAIRES_DEMO + PAIRES_AUTRES:
            if os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
                L += lmm(p, mode)
    t = pd.DataFrame(L)
    os.makedirs('data/lmm_cloture_ny', exist_ok=True)
    t.to_csv('data/lmm_cloture_ny/trades.csv', index=False)
    res = []
    for (mode, f), g in t.groupby(['journee', 'filtre'], sort=False):
        for nom, x in [('toute la période', g), ('1re moitié', g[g['lundi'] < '2025-05-01']),
                       ('2e moitié', g[g['lundi'] >= '2025-05-01'])]:
            res.append(dict(journee=mode, filtre_masterclass='avec' if f else 'sans (écartés)', periode=nom,
                            trades=len(x), gagnants=round((x['r'] > 0).mean(), 3), r_moyen=round(x['r'].mean(), 3),
                            erreur_type=round(x['r'].std() / np.sqrt(len(x)), 3)))
    r = pd.DataFrame(res)
    r.to_csv('data/lmm_cloture_ny/resultats.csv', index=False)
    pd.set_option('display.width', 200)
    print(r.to_string(index=False))
    a = t[t['filtre'] & (t['journee'] == 'minuit UTC')].set_index(['paire', 'lundi'])
    b = t[t['filtre'] & (t['journee'] == '17h New York')].set_index(['paire', 'lundi'])
    print(f"\nTrades filtrés communs : {len(a.index.intersection(b.index))} ; seulement minuit UTC : "
          f"{len(a.index.difference(b.index))} ; seulement 17h NY : {len(b.index.difference(a.index))}")


if __name__ == '__main__':
    main()
