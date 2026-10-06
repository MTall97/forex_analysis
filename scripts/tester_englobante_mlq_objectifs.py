#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Englobante journalière sur un MLQ : objectifs de 1 R, 2 R et 3 R, achats et ventes, contre deux témoins.

Signal : bougie J qui englobe le corps de J-1 de couleur opposée (corps de J >= corps de J-1) ; entrée à la
clôture de J ; stop à 2 pips au-delà de l'extrême de J ; objectif 1, 2 ou 3 R ; sortie au plus tard à la clôture
de J+3 ; spread déduit.
- « MLQ » : l'extrême de J (plus bas pour un achat, plus haut pour une vente) est à 25 pips ou moins d'un
  multiple de 250 pips ;
- témoin « niveaux décalés » : à 25 pips ou moins d'un multiple de 250 pips + 125 pips (des niveaux sans
  signification, aussi nombreux) ;
- témoin « toutes les englobantes ».

Deux rejeux :
1. journalier Dukascopy 2012-2026, 10 paires (data/prix/journalier_dukascopy.csv) : si le stop et l'objectif
   sont touchés le même jour, le stop compte (pessimiste, surtout pour 1 R) ;
2. horaire Yahoo 12/2023-10/2026, 22 paires : l'ordre des prix est connu à l'heure près.
Sortie : data/englobante_mlq_objectifs/{journalier,horaire}.csv et resultats.csv
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

SORTIE = 'data/englobante_mlq_objectifs'
OBJECTIFS = [1, 2, 3]


def niveau(extreme, pp, decalage):
    pas = 250 * pp
    x = extreme - decalage * pp
    return abs(x - round(x / pas) * pas) <= 25 * pp


def englobantes(d):
    """d : DataFrame journalier (open, high, low, close). Renvoie les indices i et le sens."""
    o, c = d['open'].to_numpy(), d['close'].to_numpy()
    for i in range(1, len(d) - 3):
        if abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1]) and (c[i] - o[i]) * (c[i - 1] - o[i - 1]) < 0:
            yield i, (1 if c[i] > o[i] else -1)


def rejouer(hh, ll, cc, e, sl, k):
    """Repère achat. hh, ll : bougies après l'entrée ; cc : clôture de sortie. R brut."""
    R = e - sl
    tp = e + k * R
    for i in range(len(hh)):
        if ll[i] <= sl:
            return -1.0
        if hh[i] >= tp:
            return float(k)
    return (cc - e) / R


def journalier():
    jd = pd.read_csv('data/prix/journalier_dukascopy.csv')
    lignes = []
    for p, d in jd[jd['paire'] != 'XAUUSD'].groupby('paire'):
        d = d.reset_index(drop=True)
        pp, sp = pip(p), spread(p)
        for i, s in englobantes(d):
            if s > 0:
                ext, sl0 = d['low'][i], d['low'][i] - 2 * pp
                hh, ll = d['high'][i + 1:i + 4].to_numpy(), d['low'][i + 1:i + 4].to_numpy()
            else:
                ext, sl0 = d['high'][i], -(d['high'][i] + 2 * pp)
                hh, ll = -d['low'][i + 1:i + 4].to_numpy(), -d['high'][i + 1:i + 4].to_numpy()
            e = d['close'][i] * s
            if e - sl0 < 5 * pp:
                continue
            base = dict(paire=p, date=d['date'][i], sens='achat' if s > 0 else 'vente', mlq=niveau(ext, pp, 0),
                        decale=niveau(ext, pp, 125))
            for k in OBJECTIFS:
                r = rejouer(hh, ll, d['close'][i + 3] * s, e, sl0, k) - sp / (e - sl0)
                lignes.append(dict(base, objectif=k, r=round(r, 4)))
    return pd.DataFrame(lignes)


def horaire():
    lignes = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = charger(p)
        jours = sorted(h['jour'].unique())
        pj = {j: g for j, g in h.groupby('jour')}
        d = pd.DataFrame([dict(jour=j, open=g['open'].iloc[0], high=g['high'].max(), low=g['low'].min(),
                               close=g['close'].iloc[-1], n=len(g)) for j, g in ((j, pj[j]) for j in jours)])
        pp, sp = pip(p), spread(p)
        for i, s in englobantes(d):
            if d['n'][i] < 18 or d['n'][i - 1] < 18:
                continue
            apres = pd.concat([pj[j] for j in d['jour'][i + 1:i + 4]])
            if s > 0:
                ext, sl0 = d['low'][i], d['low'][i] - 2 * pp
                hh, ll = apres['high'].to_numpy(), apres['low'].to_numpy()
            else:
                ext, sl0 = d['high'][i], -(d['high'][i] + 2 * pp)
                hh, ll = -apres['low'].to_numpy(), -apres['high'].to_numpy()
            e = d['close'][i] * s
            if e - sl0 < 5 * pp:
                continue
            base = dict(paire=p, date=d['jour'][i], sens='achat' if s > 0 else 'vente', mlq=niveau(ext, pp, 0),
                        decale=niveau(ext, pp, 125), dix_paires=p in PAIRES_DEMO)
            for k in OBJECTIFS:
                r = rejouer(hh, ll, apres['close'].iat[-1] * s, e, sl0, k) - sp / (e - sl0)
                lignes.append(dict(base, objectif=k, r=round(r, 4)))
    return pd.DataFrame(lignes)


def bilan(x):
    return pd.Series({'trades': len(x), 'gagnants': round((x['r'] > 0).mean(), 3), 'r_moyen': round(x['r'].mean(), 3),
                      'erreur_type': round(x['r'].std() / np.sqrt(len(x)), 3) if len(x) > 1 else np.nan})


def main():
    os.makedirs(SORTIE, exist_ok=True)
    res = []
    jd = journalier()
    jd.to_csv(f'{SORTIE}/journalier.csv', index=False)
    jd['periode'] = np.where(jd['date'] < '2020-01-01', '2012-2019', '2020-2026')
    hd = horaire()
    hd.to_csv(f'{SORTIE}/horaire.csv', index=False)
    for nom, d, periodes in [('journalier 10 paires', jd, ['2012-2019', '2020-2026']),
                             ('horaire 22 paires 2024-2026', hd.assign(periode='2024-2026'), ['2024-2026'])]:
        for per in periodes:
            x0 = d[d['periode'] == per]
            for filtre, m in [('MLQ', x0['mlq']), ('niveaux décalés (témoin)', x0['decale']),
                              ('toutes englobantes (témoin)', x0['mlq'] | ~x0['mlq'])]:
                for sens in ['achat', 'vente', 'les deux']:
                    x1 = x0[m & ((x0['sens'] == sens) if sens != 'les deux' else True)]
                    for k in OBJECTIFS:
                        res.append(dict(rejeu=nom, periode=per, filtre=filtre, sens=sens, objectif=f'{k} R',
                                        **bilan(x1[x1['objectif'] == k])))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 200)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
