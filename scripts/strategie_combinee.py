#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peut-on construire une stratégie rentable en combinant les « briques » d'Amirou ?
- E : bougie journalière englobante (flashcards) ;
- W : le mercredi (trade pris à la clôture du mardi, ou englobante formée le mercredi) ;
- M : un MLQ (niveau de 250 pips) à moins de 25 pips de l'extrême de la bougie signal (rejet du niveau) ;
- T : configuration « trois barres » lundi-mardi (masterclass).

Méthode, pour éviter de « trouver » une stratégie par hasard :
1. Toutes les combinaisons sont définies AVANT de regarder les résultats (liste COMBINAISONS).
2. Période d'apprentissage 2012-2019 : on choisit la meilleure combinaison et la meilleure gestion.
3. Période de validation 2020-2026, jamais regardée pendant le choix : on vérifie que le résultat tient.
4. Test de significativité : le R moyen est comparé à 0 (statistique t) ; avec des dizaines de
   combinaisons testées, une seule combinaison « significative » à 5 % peut être due au hasard.

Trade : entrée à la clôture de la bougie signal, stop à l'autre extrême de la bougie (+ 2 pips),
objectif 1 R, 2 R ou sortie à la clôture du 3e jour ; bougies journalières Dukascopy ; si l'objectif et
le stop sont touchés le même jour, on compte le stop ; spread déduit.

Sorties : data/strategie_combinee.csv (une ligne par combinaison x gestion x période),
data/strategie_combinee_trades.csv (chaque occurrence datée avec ses résultats), résumé écran.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_dukascopy_journalier as dk  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

GESTIONS = {'1R': 1.0, '2R': 2.0, '3 jours': None}
COMBINAISONS = {
    'E (englobante seule)': lambda x: x.E,
    'E + englobante du mardi (trade mercredi)': lambda x: x.E & (x.jour == 1),
    'E + englobante du mercredi': lambda x: x.E & (x.jour == 2),
    'E + MLQ': lambda x: x.E & x.M,
    'E + MLQ + mardi': lambda x: x.E & x.M & (x.jour == 1),
    'E + MLQ + mercredi': lambda x: x.E & x.M & (x.jour == 2),
    'T (trois barres)': lambda x: x.T,
    'T + MLQ': lambda x: x.T & x.M,
    'T + englobante': lambda x: x.T & x.E,
    'MLQ seul': lambda x: x.M,
    'MLQ + mardi': lambda x: x.M & (x.jour == 1),
    'Toute bougie (témoin)': lambda x: x.sens != 0,
}


def signaux(p, d):
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    wd = d.date.dt.weekday.to_numpy()
    pp = pip(p)
    pas = 250 * pp
    lignes = []
    for i in range(2, len(d) - 4):
        s = int(np.sign(c[i] - o[i]))
        if s == 0:
            continue
        E = s == -np.sign(c[i - 1] - o[i - 1]) and abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1])
        extreme = h[i] if s < 0 else l[i]                   # vente : le haut a rejeté un niveau ; achat : le bas
        M = abs(extreme - round(extreme / pas) * pas) <= 25 * pp and p != 'XAUUSD'
        rng = h[i - 1] - l[i - 1]
        T = False
        if wd[i] == 1 and wd[i - 1] == 0 and rng > 0:      # mardi, après un lundi « plein »
            plein = abs(c[i - 1] - o[i - 1]) >= 0.6 * rng
            T = plein and ((s < 0 and c[i - 1] > o[i - 1] and c[i - 1] >= h[i - 1] - 0.25 * rng and c[i] < c[i - 1]) or
                           (s > 0 and c[i - 1] < o[i - 1] and c[i - 1] <= l[i - 1] + 0.25 * rng and c[i] > c[i - 1]))
        sl = (h[i] + 2 * pp) if s < 0 else (l[i] - 2 * pp)
        risque = abs(c[i] - sl)
        if risque < 5 * pp:
            continue
        res = {}
        for g, rr in GESTIONS.items():
            r = None
            for j in range(i + 1, i + 4):
                stop = h[j] >= sl if s < 0 else l[j] <= sl
                obj = rr is not None and ((l[j] <= c[i] - rr * risque) if s < 0 else (h[j] >= c[i] + rr * risque))
                if stop:
                    r = -1.0
                    break
                if obj:
                    r = rr
                    break
            if r is None:
                r = (c[i + 3] - c[i]) * s / risque
            res[g] = r - spread(p) / risque
        lignes.append(dict(paire=p, date=d.date.iat[i], jour=wd[i], sens=s, E=bool(E), M=bool(M), T=bool(T), **res))
    return lignes


def main():
    jd = dk.charger()
    jd = jd[jd.date >= '2012-01-01']
    x = pd.DataFrame([l for p, d in jd.groupby('paire') for l in signaux(p, d.reset_index(drop=True))])
    x['periode'] = np.where(x.date.dt.year <= 2019, 'apprentissage 2012-2019', 'validation 2020-2026')
    x[x.E | x.M | x.T].to_csv('data/strategie_combinee_trades.csv', index=False)   # occurrences datées
    res = []
    for nom, f in COMBINAISONS.items():
        sel = x[f(x)]
        for per, g in sel.groupby('periode'):
            for gest in GESTIONS:
                r = g[gest]
                t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 else np.nan
                res.append(dict(combinaison=nom, gestion=gest, periode=per, n=len(r),
                                gagnants_pct=round((r > 0).mean() * 100, 1), r_moyen=round(r.mean(), 3),
                                t_stat=round(t, 2), par_an=round(len(r) / (8 if per.startswith('app') else 6.75), 1)))
    df = pd.DataFrame(res)
    df.to_csv('data/strategie_combinee.csv', index=False)
    pd.set_option('display.width', 220)
    pd.set_option('display.max_rows', 200)
    piv = df.pivot_table(index=['combinaison', 'gestion'], columns='periode', values=['n', 'r_moyen', 't_stat'])
    print(piv.round(3).to_string())
    app = df[df.periode.str.startswith('app')].sort_values('r_moyen', ascending=False)
    best = app[app.n >= 30].iloc[0]
    val = df[(df.combinaison == best.combinaison) & (df.gestion == best.gestion) & df.periode.str.startswith('val')].iloc[0]
    print(f"\nMeilleure sur 2012-2019 (>= 30 trades) : {best.combinaison} / {best.gestion} : "
          f"{best.n} trades, {best.r_moyen:+.3f} R (t = {best.t_stat})")
    print(f"Même règle sur 2020-2026                : {val.n} trades, {val.r_moyen:+.3f} R (t = {val.t_stat})")


if __name__ == '__main__':
    main()
