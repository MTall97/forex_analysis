#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contrôle de la seule combinaison positive sur 2020-2026 : « englobante + MLQ » (strategie_combinee.py).

On refait le même trade (entrée à la clôture de l'englobante, stop à l'autre extrême + 2 pips,
objectif 2 R ou clôture du 3e jour, spread déduit) en remplaçant les vrais niveaux MLQ (multiples de
250 pips) par des niveaux décalés de 50, 100, 125, 175 et 200 pips. Si les niveaux décalés font aussi
bien, l'avantage ne vient pas du MLQ. On sépare aussi achats et ventes, et 2012-2019 / 2020-2026.

Sortie : data/masterclass_2020_2026/controle_englobante_mlq.csv
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_dukascopy_journalier as dk  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

DECALAGES = [0, 50, 100, 125, 175, 200]


def occurrences(p, d):
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    pp = pip(p)
    pas = 250 * pp
    lignes = []
    for i in range(2, len(d) - 4):
        s = int(np.sign(c[i] - o[i]))
        if s == 0:
            continue
        if not (s == -np.sign(c[i - 1] - o[i - 1]) and abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1])):
            continue
        extreme = h[i] if s < 0 else l[i]
        sl = (h[i] + 2 * pp) if s < 0 else (l[i] - 2 * pp)
        risque = abs(c[i] - sl)
        if risque < 5 * pp:
            continue
        res = {}
        for g, rr in {'2R': 2.0, '3 jours': None}.items():
            r = None
            for j in range(i + 1, i + 4):
                if (h[j] >= sl) if s < 0 else (l[j] <= sl):
                    r = -1.0
                    break
                if rr is not None and ((l[j] <= c[i] - rr * risque) if s < 0 else (h[j] >= c[i] + rr * risque)):
                    r = rr
                    break
            if r is None:
                r = (c[i + 3] - c[i]) * s / risque
            res[g] = r - spread(p) / risque
        proche = {dec: abs(extreme - dec * pp - round((extreme - dec * pp) / pas) * pas) <= 25 * pp
                  for dec in DECALAGES}
        lignes.append(dict(paire=p, date=d.date.iat[i], sens='achat' if s > 0 else 'vente',
                           **res, **{f'M{dec}': v for dec, v in proche.items()}))
    return lignes


def main():
    jd = dk.charger()
    jd = jd[(jd.date >= '2012-01-01') & (jd.paire != 'XAUUSD')]
    x = pd.DataFrame([l for p, d in jd.groupby('paire') for l in occurrences(p, d.reset_index(drop=True))])
    x['periode'] = np.where(x.date.dt.year <= 2019, '2012-2019', '2020-2026')
    res = []
    for dec in DECALAGES:
        for per in ['2012-2019', '2020-2026']:
            for sens in ['tous', 'achat', 'vente']:
                g = x[x[f'M{dec}'] & (x.periode == per) & ((x.sens == sens) | (sens == 'tous'))]
                for gest in ['2R', '3 jours']:
                    r = g[gest]
                    t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 else np.nan
                    res.append(dict(niveaux='MLQ réels' if dec == 0 else f'décalés de {dec} pips', periode=per,
                                    sens=sens, gestion=gest, n=len(r), gagnants_pct=round((r > 0).mean() * 100, 1),
                                    r_moyen=round(r.mean(), 3), t=round(t, 2)))
        # témoin : toutes les englobantes, sans condition de niveau
    for per in ['2012-2019', '2020-2026']:
        for sens in ['tous', 'achat', 'vente']:
            g = x[(x.periode == per) & ((x.sens == sens) | (sens == 'tous'))]
            for gest in ['2R', '3 jours']:
                r = g[gest]
                res.append(dict(niveaux='toute englobante (témoin)', periode=per, sens=sens, gestion=gest, n=len(r),
                                gagnants_pct=round((r > 0).mean() * 100, 1), r_moyen=round(r.mean(), 3),
                                t=round(r.mean() / (r.std(ddof=1) / np.sqrt(len(r))), 2)))
    df = pd.DataFrame(res)
    os.makedirs('data/masterclass_2020_2026', exist_ok=True)
    df.to_csv('data/masterclass_2020_2026/controle_englobante_mlq.csv', index=False)
    pd.set_option('display.width', 200)
    print(df[(df.gestion == '2R')].pivot_table(index=['niveaux'], columns=['periode', 'sens'],
                                                 values='r_moyen').round(3).to_string())
    print(df[(df.gestion == '2R')].pivot_table(index=['niveaux'], columns=['periode', 'sens'],
                                                 values='n').to_string())


if __name__ == '__main__':
    main()
