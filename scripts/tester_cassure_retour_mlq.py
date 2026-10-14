#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
« Cassure puis retour sur le MLQ » : la règle observée dans les trades d'Amirou d'octobre 2026
(analyses/OCTOBRE_2026.md), testée sur les cours, contre un témoin.

Règle (vente ; l'achat est symétrique), fixée avant le test :
- niveau L : multiple de 250 pips (MLQ) — témoin : multiple de 250 pips + 125 pips (niveaux sans signification) ;
- cassure : une bougie clôture sous L alors que la précédente clôturait au-dessus ;
- confirmation : dans les 48 h, le prix s'éloigne d'au moins 0,3 ATR(14) journalier sous L, sans reclôturer
  au-dessus de L avant ; sinon la cassure est abandonnée ;
- ordre de vente limite à L, valable 5 jours après la cassure ;
- stop à L + 0,35 ATR (variante 0,5 ATR), objectif 1, 2 ou 3 R, sortie au plus tard 5 jours après l'entrée ;
- une seule configuration à la fois par paire et par sens ; spread déduit.

Deux rejeux :
1. horaire Yahoo, 22 paires, 12/2023-10/2026 (principal) : dans la bougie de l'entrée, seul le stop compte ; dans
   une même heure, le stop passe avant l'objectif ;
2. journalier Dukascopy, 10 paires, 2012-2026 (contrôle sur la durée) : mêmes règles en jours (confirmation en
   2 jours, ordre valable 5 jours) ; quand un jour touche stop et objectif, on donne les deux bornes (stop d'abord,
   objectif d'abord).
Sortie : data/cassure_retour_mlq/{horaire,journalier}.csv.gz, resultats.csv
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

SORTIE = 'data/cassure_retour_mlq'
OBJECTIFS = (1, 2, 3)
STOPS = (0.35, 0.5)


def atr_journalier(d):
    tr = np.maximum(d['high'] - d['low'], np.maximum(abs(d['high'] - d['close'].shift()), abs(d['low'] - d['close'].shift())))
    return tr.rolling(14).mean().shift(1)


def scanner(o, h, l, c, atr, pp, decalage, conf_max, valid, sens):
    """Repère « achat » : pour une vente (sens = -1) les prix sont inversés (P -> -P), et la cassure vers le bas puis
    le retour par le bas deviennent une cassure vers le haut puis un retour par le haut. Renvoie les entrées."""
    s = sens
    O, H, L_, C = (o, h, l, c) if s > 0 else (-o, -l, -h, -c)
    pas, off = 250 * pp, s * decalage * pp            # grille des niveaux dans ce repère
    n = len(C)
    trades = []
    i = 1
    while i < n - 2:
        lv = (np.floor((C[i - 1] - off) / pas) + 1) * pas + off   # premier niveau au-dessus de la clôture précédente
        if not (C[i] >= lv) or np.isnan(atr[i]):
            i += 1
            continue
        dist = 0.3 * atr[i]
        j, ok = i + 1, False                          # confirmation : s'éloigner sans reclôturer sous le niveau
        while j < min(n, i + 1 + conf_max):
            if C[j] < lv:
                break
            if H[j] >= lv + dist:
                ok = True
                break
            j += 1
        if not ok:
            i = max(j, i + 1)
            continue
        fin_validite = min(n, i + 1 + valid)
        k_fill = next((m for m in range(j + 1, fin_validite) if L_[m] <= lv), None)
        if k_fill is None:
            i = fin_validite
            continue
        e = min(lv, O[k_fill])                        # ouverture déjà au-delà du niveau : exécution à l'ouverture
        trades.append(dict(i_entree=k_fill, entree_repere=e, niveau=lv * s, atr=atr[i]))
        i = k_fill + 1                                # une configuration à la fois
    return trades


def issue(H, L_, C, k, e, R, obj, fin, bornes=False):
    sl, tp = e - R, e + obj * R
    if L_[k] <= sl:
        return (-1.0, -1.0)
    for m in range(k + 1, min(fin, len(C))):
        st, ob = L_[m] <= sl, H[m] >= tp
        if st and ob:
            return (-1.0, float(obj)) if bornes else (-1.0, -1.0)
        if st:
            return (-1.0, -1.0)
        if ob:
            return (float(obj), float(obj))
    r = (C[min(fin, len(C)) - 1] - e) / R
    return (r, r)


def rejouer(nom, d, p, conf_max, valid, tenue, atr, bornes):
    pp, sp = pip(p), spread(p)
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    lignes = []
    for decalage, groupe in [(0, 'MLQ'), (125, 'niveaux décalés (témoin)')]:
        for s in (1, -1):
            O, H, L_, C = (o, h, l, c) if s > 0 else (-o, -l, -h, -c)
            for t in scanner(o, h, l, c, atr, pp, decalage, conf_max, valid, s):
                for m in STOPS:
                    R = m * t['atr']
                    for obj in OBJECTIFS:
                        rp, ro = issue(H, L_, C, t['i_entree'], t['entree_repere'], R, obj, t['i_entree'] + tenue, bornes)
                        lignes.append(dict(rejeu=nom, paire=p, date=str(d['date'].iat[t['i_entree']])[:16],
                                           sens='achat' if s > 0 else 'vente', groupe=groupe,
                                           niveau=round(t['niveau'], 5), stop_atr=m, objectif=obj,
                                           risque_pips=round(R / pp, 1),
                                           r=round(rp - sp / R, 4), r_optimiste=round(ro - sp / R, 4)))
    return lignes


def horaire():
    lignes = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = charger(p)
        dj = h.groupby('jour').agg(high=('high', 'max'), low=('low', 'min'), close=('close', 'last'))
        a = atr_journalier(dj)
        atr = h['jour'].map(a).to_numpy()
        lignes += rejouer('horaire 22 paires 2024-2026', h, p, 48, 120, 120, atr, bornes=False)
    return pd.DataFrame(lignes)


def journalier():
    jd = pd.read_csv('data/prix/journalier_dukascopy.csv')
    lignes = []
    for p, d in jd[jd['paire'] != 'XAUUSD'].groupby('paire'):
        d = d.reset_index(drop=True)
        atr = atr_journalier(d).to_numpy()
        lignes += rejouer('journalier 10 paires 2012-2026', d, p, 2, 5, 5, atr, bornes=True)
    return pd.DataFrame(lignes)


def main():
    os.makedirs(SORTIE, exist_ok=True)
    hd, jd = horaire(), journalier()
    hd.to_csv(f'{SORTIE}/horaire.csv.gz', index=False)
    jd.to_csv(f'{SORTIE}/journalier.csv.gz', index=False)
    jd['periode'] = np.where(jd['date'] < '2020', '2012-2019', '2020-2026')
    hd['periode'] = '2024-2026'
    res = []
    for d in (hd, jd):
        for (rj, per, g, sens, m, obj), x in d.groupby(['rejeu', 'periode', 'groupe', 'sens', 'stop_atr', 'objectif']):
            res.append(dict(rejeu=rj, periode=per, groupe=g, sens=sens, stop=f'{m} ATR', objectif=f'{obj} R', trades=len(x),
                            gagnants=round((x['r'] > 0).mean(), 3), r_moyen=round(x['r'].mean(), 3),
                            r_optimiste=round(x['r_optimiste'].mean(), 3),
                            erreur_type=round(x['r'].std() / np.sqrt(len(x)), 3)))
        for (rj, per, g, m, obj), x in d.groupby(['rejeu', 'periode', 'groupe', 'stop_atr', 'objectif']):
            res.append(dict(rejeu=rj, periode=per, groupe=g, sens='les deux', stop=f'{m} ATR', objectif=f'{obj} R',
                            trades=len(x), gagnants=round((x['r'] > 0).mean(), 3), r_moyen=round(x['r'].mean(), 3),
                            r_optimiste=round(x['r_optimiste'].mean(), 3),
                            erreur_type=round(x['r'].std() / np.sqrt(len(x)), 3)))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 220)
    print(r[r['sens'] == 'les deux'].to_string(index=False))


if __name__ == '__main__':
    main()
