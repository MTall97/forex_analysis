#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Les stratégies du journal avec le stop remonté au point d'entrée (break-even, BE) dès que le prix a fait +1 R.

Mêmes signaux, même entrée, même stop et même objectif que chaque stratégie (tester_stops_fixes.py pour le moteur) :
- englobante + MLQ (horaire 2024-2026 et journalier 2012-2026) : objectif 2 R, sortie à la clôture de J+3 ;
- lundi-mardi-mercredi (filtre masterclass) : objectif d'origine, sortie à la clôture du vendredi ;
- cassure puis retour sur MLQ : objectif 2 R, sortie 120 h après l'entrée.
Le suivi de tendance (objectif 1 R) n'est pas concerné : l'objectif est atteint avant le BE.
Variantes : sans BE (règle d'origine rejouée par le même moteur), BE à +1 R (demande), BE à +1,5 R (contrôle).
Prudence : le BE ne s'applique qu'à partir de la bougie qui suit celle où +1 R est touché (dans une même bougie on ne
sait pas si le prix a d'abord monté ou baissé) ; stop prioritaire dans une même bougie ; spread déduit.
Sortie : data/be_1r/{trades.csv.gz, resultats.csv}
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_filtres_playbook import heure  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402
from tester_stops_fixes import fin_120, fin_j3, fin_vendredi, h1, k_apres, k_dans, lmm_trades  # noqa: E402

VARIANTES = [('sans BE', None), ('BE à +1 R', 1.0), ('BE à +1,5 R', 1.5)]


def suivre(H, L, C, e, sl, tp, s, k0, k1, be, verif=None):
    """Renvoie (R, motif). be : niveau en R qui déclenche le stop au point d'entrée (None : jamais)."""
    if verif is not None and ((L[verif] <= sl) if s > 0 else (H[verif] >= sl)):
        return -1.0, 'stop'
    R = abs(e - sl)
    stop, arme = sl, False
    for k in range(k0, min(k1, len(C) - 1) + 1):
        if (L[k] <= stop) if s > 0 else (H[k] >= stop):
            return ((stop - e) * s / R, 'BE' if arme else 'stop')
        if (H[k] >= tp) if s > 0 else (L[k] <= tp):
            return abs(tp - e) / R, 'objectif'
        if be is not None and not arme and ((H[k] - e) if s > 0 else (e - L[k])) >= be * R:
            stop, arme = e, True
    k = min(k1, len(C) - 1)
    return (C[k] - e) * s / R, 'échéance'


def rejouer(nom, d, fin_fn, k0_fn, verif=False):
    out = []
    for t in d.itertuples():
        h, dates, jours = h1(t.paire)
        te = heure(t.entree_date_heure)
        s = 1 if t.sens == 'achat' else -1
        H, L, C = h['high'].to_numpy(), h['low'].to_numpy(), h['close'].to_numpy()
        k0 = k0_fn(dates, te)
        k1 = fin_fn(h, dates, jours, te, k0)
        if k0 is None or k1 is None or k0 >= len(C):
            continue
        R = abs(t.entree - t.stop)
        for v, be in VARIANTES:
            r, m = suivre(H, L, C, t.entree, t.stop, t.objectif, s, k0 + (1 if verif else 0), k1, be,
                          verif=k0 if verif else None)
            out.append(dict(strategie=nom, paire=t.paire, date=str(te)[:16], variante=v, motif=m,
                            r=r - spread(t.paire) / R))
    return out


def journalier():
    d = pd.read_csv('data/journal_trades/englobante_mlq_journalier.csv').dropna(subset=['r'])
    jd = pd.read_csv('data/prix/journalier_dukascopy.csv')
    out = []
    for p, g in d.groupby('paire'):
        x = jd[jd['paire'] == p].reset_index(drop=True)
        dates = x['date'].tolist()
        H, L, C = x['high'].to_numpy(), x['low'].to_numpy(), x['close'].to_numpy()
        for t in g.itertuples():
            i = dates.index(t.entree_date_heure[:10])
            s = 1 if t.sens == 'achat' else -1
            for v, be in VARIANTES:
                r, m = suivre(H, L, C, t.entree, t.stop, t.objectif, s, i + 1, i + 3, be)
                out.append(dict(strategie='englobante + MLQ (journalier 2012-2026)', paire=p,
                                date=t.entree_date_heure[:10], variante=v, motif=m,
                                r=r - spread(p) / abs(t.entree - t.stop)))
    return out


def main():
    L = []
    d = pd.read_csv('data/journal_trades/englobante_mlq_horaire.csv').dropna(subset=['r'])
    L += rejouer('englobante + MLQ (horaire)', d, fin_j3, k_apres)
    L += journalier()
    lm = lmm_trades()
    import construire_page_strategies as cps
    lm['stop'] = [x['e'] + x['sl'] * pip(x['p']) / 10 for x in cps.lmm()]
    lm['objectif'] = lm['objectif_px']
    L += rejouer('lundi-mardi-mercredi', lm, fin_vendredi, k_apres)
    d = pd.read_csv('data/journal_trades/cassure_retour_mlq.csv').dropna(subset=['r'])
    L += rejouer('cassure-retour MLQ', d, fin_120, k_dans, verif=True)
    t = pd.DataFrame(L)
    os.makedirs('data/be_1r', exist_ok=True)
    t.to_csv('data/be_1r/trades.csv.gz', index=False)
    res = []
    for (s, v), g in t.groupby(['strategie', 'variante'], sort=False):
        r = g['r']
        cum = np.cumsum(r.to_numpy())
        dd = (np.maximum.accumulate(np.r_[0, cum])[1:] - cum).max()
        half = g['date'] < sorted(g['date'])[len(g) // 2]
        mo = g['motif'].value_counts()
        res.append(dict(strategie=s, variante=v, trades=len(r), gagnants=round((r > 0).mean(), 3),
                        objectif=int(mo.get('objectif', 0)), be=int(mo.get('BE', 0)), stop=int(mo.get('stop', 0)),
                        echeance=int(mo.get('échéance', 0)), r_moyen=round(r.mean(), 3),
                        erreur_type=round(r.std() / np.sqrt(len(r)), 3),
                        r_1re_moitie=round(g.loc[half, 'r'].mean(), 3), r_2e_moitie=round(g.loc[~half, 'r'].mean(), 3),
                        baisse_max_R=round(dd, 1)))
    r = pd.DataFrame(res)
    r.to_csv('data/be_1r/resultats.csv', index=False)
    pd.set_option('display.width', 230)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
