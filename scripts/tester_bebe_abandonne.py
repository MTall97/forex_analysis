#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste la stratégie du « bébé abandonné » (masterclass, « 75 % de réussite ») en HORAIRE.

Définition de la masterclass : une bougie directionnelle forte, suivie d'une petite bougie « interne »
(corps compris dans celui de la précédente), suivie d'une troisième bougie qui clôture franchement
au-dessus ou en dessous de la bougie centrale (continuation ou retournement).

Traduction en code (bougies H1 Yahoo, déc. 2023 -> sept. 2026, 13 paires) :
- bougie 1 « forte » : corps >= 60 % de son range et range >= ATR horaire (50 bougies) ;
- bougie 2 « interne » : corps compris dans le corps de la bougie 1, range <= 60 % de celui de la bougie 1 ;
- bougie 3 : clôture au-delà du plus haut (achat) ou du plus bas (vente) de la bougie 2.
Trade : entrée à la clôture de la bougie 3 ; stop à l'autre extrême de la figure (bougies 2 et 3) + 1 pip ;
objectif 1 R, 2 R ou sortie après 24 heures ; objectif et stop dans la même heure -> stop ; spread déduit.

Témoin : toute bougie qui clôture au-delà de l'extrême de la bougie précédente, gérée de la même façon
(même stop relatif, mêmes objectifs). Si la figure ne fait pas mieux, elle n'apporte rien.

Sorties : data/bebe_abandonne_horaire.csv (les bébés abandonnés seulement), résumé à l'écran (par sens de la figure, par session).
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402
from modele_meta import SPREAD  # noqa: E402
from tester_strategie_bombe import PAIRES, pip  # noqa: E402

GESTIONS = {'1R': 1.0, '2R': 2.0, '24 h': None}


def rejouer(h, l, c, i, s, sl, risque, rr, maxi=24):
    for j in range(i + 1, min(i + 1 + maxi, len(c))):
        if (s > 0 and l[j] <= sl) or (s < 0 and h[j] >= sl):
            return -1.0
        if rr is not None and ((s > 0 and h[j] >= c[i] + rr * risque) or (s < 0 and l[j] <= c[i] - rr * risque)):
            return rr
    j = min(i + maxi, len(c) - 1)
    return (c[j] - c[i]) * s / risque


def analyser(p, d):
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    t = pd.to_datetime(d.date).to_numpy()
    rng = h - l
    atr = pd.Series(rng).rolling(50).mean().to_numpy()
    pp = pip(p)
    sp = SPREAD.get(p, 2) * pp
    lignes = []
    for i in range(52, len(c) - 25):
        if c[i] > h[i - 1]:
            s = 1
        elif c[i] < l[i - 1]:
            s = -1
        else:
            continue
        a, b = i - 2, i - 1
        fort = rng[a] > 0 and abs(c[a] - o[a]) >= 0.6 * rng[a] and rng[a] >= atr[a]
        interne = (max(o[b], c[b]) <= max(o[a], c[a]) and min(o[b], c[b]) >= min(o[a], c[a])
                   and rng[b] <= 0.6 * rng[a])
        bebe = bool(fort and interne)
        nature = ('continuation' if s == np.sign(c[a] - o[a]) else 'retournement') if bebe else ''
        sl = (min(l[b], l[i]) - pp) if s > 0 else (max(h[b], h[i]) + pp)
        risque = abs(c[i] - sl)
        if risque < 3 * pp:
            continue
        ligne = dict(paire=p, date=t[i], heure=pd.Timestamp(t[i]).hour, sens=s, bebe=bebe, nature=nature,
                     risque_pips=risque / pp)
        for g, rr in GESTIONS.items():
            ligne[g] = rejouer(h, l, c, i, s, sl, risque, rr) - sp / risque
        lignes.append(ligne)
    return lignes


def resume(x, titre):
    out = [f"{titre:<38} n={len(x):>6}"]
    for g in GESTIONS:
        r = x[g]
        t = r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 else np.nan
        out.append(f"{g}: {(r > 0).mean() * 100:4.0f} % gagn., {r.mean():+.3f} R (t={t:+.1f})")
    return '  '.join(out)


def main():
    lignes = []
    for p in PAIRES:
        d = prix_yahoo._charger(p, '1h').reset_index(drop=True)
        lignes += analyser(p, d)
    x = pd.DataFrame(lignes)
    x[x.bebe].to_csv('data/bebe_abandonne_horaire.csv', index=False)   # le témoin (~96 000 lignes) n'est pas écrit
    b = x[x.bebe]
    mois = (x.date.max() - x.date.min()).days / 30.4
    print(f"{x.date.min():%Y-%m-%d} -> {x.date.max():%Y-%m-%d}, {len(PAIRES)} paires, "
          f"{len(b)} bébés abandonnés ({len(b) / mois / len(PAIRES):.1f} par mois et par paire)\n")
    print(resume(b, 'Bébé abandonné (tous)'))
    for n, g in b.groupby('nature'):
        print(resume(g, f'  {n}'))
    sess = lambda hr: 'Asie (0-7 h)' if hr < 7 else 'Londres (7-12 h)' if hr < 12 else 'New York (12-17 h)' if hr < 17 else 'soir (17-24 h)'  # noqa: E731
    for n, g in b.groupby(b.heure.map(sess)):
        print(resume(g, f'  {n}'))
    print(resume(x[~x.bebe], 'Témoin : autres cassures de bougie'))


if __name__ == '__main__':
    main()
