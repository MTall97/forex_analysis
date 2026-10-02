#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La saisonnalité mensuelle prévoit-elle l'année suivante ?

Pour chaque paire, chaque mois et chaque année A, on calcule le biais du mois sur les N années
précédentes (N = 6, comme les PDF d'Antigravity 2020-2025, ou N = 10), sans jamais utiliser l'année A,
puis on regarde si le mois de l'année A a pris le sens prévu.
Biais « fort » : au moins 80 % des années dans le même sens (5 ou 6 sur 6, 8 sur 10...).

Données : data/rendements_mensuels.csv (Fed H.10, 2009-2026, 28 paires).
Sortie : data/persistance_saisonnalite.csv, résumé à l'écran.
"""

import numpy as np
import pandas as pd


def main():
    r = pd.read_csv('data/rendements_mensuels.csv')
    r['an'] = r.mois.str[:4].astype(int)
    r['m'] = r.mois.str[5:].astype(int)
    lignes = []
    for (p, m), g in r.groupby(['paire', 'm']):
        g = g.set_index('an').rendement_pct
        for a in g.index:
            for n in (6, 10):
                passe = g[(g.index < a) & (g.index >= a - n)]
                if len(passe) < n:
                    continue
                lignes.append(dict(fenetre=n, paire=p, mois=m, an=a, moyenne_passee=passe.mean(),
                                   annees_haussieres=(passe > 0).mean(), reel=g[a]))
    x = pd.DataFrame(lignes)
    x['fort'] = (x.annees_haussieres >= 0.8 - 1e-9) | (x.annees_haussieres <= 0.2 + 1e-9)
    x['juste'] = np.sign(x.reel) == np.sign(x.moyenne_passee)
    x['gain_pct'] = np.sign(x.moyenne_passee) * x.reel
    x.to_csv('data/persistance_saisonnalite.csv', index=False, float_format='%.4f')
    res = []
    for (n, fort), g in x.groupby(['fenetre', 'fort']):
        res.append(dict(fenetre=f'{n} ans', biais='fort (>= 80 %)' if fort else 'faible', n=len(g),
                        sens_juste_pct=round(g.juste.mean() * 100, 1), gain_moyen_pct=round(g.gain_pct.mean(), 3)))
    for n, g in x.groupby('fenetre'):
        res.append(dict(fenetre=f'{n} ans', biais='tous', n=len(g), sens_juste_pct=round(g.juste.mean() * 100, 1),
                        gain_moyen_pct=round(g.gain_pct.mean(), 3)))
    print(pd.DataFrame(res).to_string(index=False))
    for n in (6, 10):
        g = x[(x.fenetre == n) & x.fort]
        print(f"\nBiais forts sur {n} ans, par année :")
        print(g.groupby('an').agg(n=('juste', 'size'), juste_pct=('juste', lambda s: round(s.mean() * 100)),
                                  gain_pct=('gain_pct', lambda s: round(s.mean(), 2))).T.to_string())


if __name__ == '__main__':
    main()
