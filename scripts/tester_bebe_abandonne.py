#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste la stratégie du « bébé abandonné » (masterclass, « 75 % de réussite »), en HORAIRE et en JOURNALIER.

Définition (précisée par l'utilisateur) :
- bougies 1 et 3 de MÊME couleur (par exemple vertes) ;
- bougie 2 (le « bébé ») de couleur OPPOSÉE, entièrement englobée par la bougie 1 ET par la bougie 3 ;
- la bougie 4 « explose » dans le sens des bougies 1 et 3.
Deux lectures de « englobée » sont testées :
- « mèches » (stricte) : plus haut et plus bas de la bougie 2 compris dans le range des bougies 1 et 3 ;
- « corps » : corps de la bougie 2 compris dans le corps des bougies 1 et 3.

Mesures :
1. fréquence à laquelle la bougie 4 clôture dans le sens annoncé (« explosion ») ; témoin : toute séquence
   de deux bougies de même couleur séparées par une bougie de couleur opposée, sans condition d'englobement,
   et le simple fait qu'une bougie suive la couleur de la précédente ;
2. trade : entrée à la clôture de la bougie 3, stop sous le plus bas de la figure (achat) ou au-dessus du
   plus haut (vente) + 1 pip, objectif 1 R ou 2 R, ou sortie à la clôture de la bougie 4 ; objectif et stop
   dans la même bougie -> stop ; spread déduit.

Données : horaire Yahoo (déc. 2023 -> sept. 2026, 13 paires) ; journalier Dukascopy 2012-2026 si
data/prix/journalier_dukascopy.csv existe (scripts/prix_dukascopy_journalier.py).

Sorties : data/bebe_abandonne_horaire.csv, data/bebe_abandonne_journalier.csv (figures seulement), résumé écran.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402
from modele_meta import SPREAD  # noqa: E402
from tester_strategie_bombe import PAIRES  # noqa: E402

GESTIONS = {'1R': 1.0, '2R': 2.0, 'clôture bougie 4': 'b4'}


def pip(p):
    return 0.01 if p.endswith('JPY') else 0.1 if p == 'XAUUSD' else 0.0001


def rejouer(h, l, c, i, s, sl, risque, rr, maxi):
    if rr == 'b4':
        j = i + 1
        if (s > 0 and l[j] <= sl) or (s < 0 and h[j] >= sl):
            return -1.0
        return (c[j] - c[i]) * s / risque
    for j in range(i + 1, min(i + 1 + maxi, len(c))):
        if (s > 0 and l[j] <= sl) or (s < 0 and h[j] >= sl):
            return -1.0
        if (s > 0 and h[j] >= c[i] + rr * risque) or (s < 0 and l[j] <= c[i] - rr * risque):
            return rr
    j = min(i + maxi, len(c) - 1)
    return (c[j] - c[i]) * s / risque


def analyser(p, d, maxi):
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    t = pd.to_datetime(d.date).to_numpy()
    col = np.sign(c - o)
    pp = pip(p)
    sp = SPREAD.get(p, 2) * (0.01 if p == 'XAUUSD' else pip(p))
    lignes = []
    for i in range(2, len(c) - maxi - 1):           # i = bougie 3
        a, b = i - 2, i - 1
        s = col[i]
        if s == 0 or col[a] != s or col[b] != -s:
            continue
        meches = h[b] <= min(h[a], h[i]) and l[b] >= max(l[a], l[i])
        corps = (max(o[b], c[b]) <= min(max(o[a], c[a]), max(o[i], c[i])) and
                 min(o[b], c[b]) >= max(min(o[a], c[a]), min(o[i], c[i])))
        sl = (min(l[a], l[b], l[i]) - pp) if s > 0 else (max(h[a], h[b], h[i]) + pp)
        risque = abs(c[i] - sl)
        if risque <= 0:
            continue
        ligne = dict(paire=p, date=t[i], sens=int(s), meches=bool(meches), corps=bool(corps),
                     b4_dans_le_sens=int(np.sign(c[i + 1] - c[i]) == s),
                     b4_depasse=int(c[i + 1] > h[i] if s > 0 else c[i + 1] < l[i]),
                     risque_pips=risque / pp)
        for g, rr in GESTIONS.items():
            ligne[g] = rejouer(h, l, c, i, int(s), sl, risque, rr, maxi) - sp / risque
        lignes.append(ligne)
    return lignes, float(np.mean(col[1:][col[:-1] != 0] == col[:-1][col[:-1] != 0]))


def resume(x, titre):
    out = [f"{titre:<44} n={len(x):>6}  bougie 4 dans le sens {x.b4_dans_le_sens.mean() * 100:4.1f} % "
           f"(clôture au-delà de la bougie 3 : {x.b4_depasse.mean() * 100:4.1f} %)"]
    for g in GESTIONS:
        r = x[g]
        tt = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 else np.nan
        out.append(f"      {g:<17}: {(r > 0).mean() * 100:4.0f} % gagnants, {r.mean():+.3f} R (t={tt:+.1f})")
    return '\n'.join(out)


def etudier(nom, series, maxi, sortie):
    lignes, suite = [], []
    for p, d in series:
        lg, s = analyser(p, d.reset_index(drop=True), maxi)
        lignes += lg
        suite.append(s)
    x = pd.DataFrame(lignes)
    print(f"\n=== {nom} : {x.date.min()} -> {x.date.max()}, {x.paire.nunique()} paires")
    print(f"Une bougie a la même couleur que la précédente dans {np.mean(suite) * 100:.1f} % des cas.")
    print(resume(x[x.meches], 'Bébé abandonné (englobé mèches comprises)'))
    print(resume(x[x.corps], 'Bébé abandonné (englobé par les corps)'))
    print(resume(x[~x.corps & ~x.meches], 'Témoin : même couleurs, sans englobement'))
    x[x.meches | x.corps].to_csv(sortie, index=False)
    return x


def main():
    horaire = []
    for p in PAIRES:
        d = prix_yahoo._charger(p, '1h').copy()
        horaire.append((p, d))
    etudier('Horaire', horaire, 24, 'data/bebe_abandonne_horaire.csv')
    if os.path.exists('data/prix/journalier_dukascopy.csv'):
        import prix_dukascopy_journalier as dk
        jd = dk.charger()
        etudier('Journalier', list(jd.groupby('paire')), 5, 'data/bebe_abandonne_journalier.csv')


if __name__ == '__main__':
    main()
