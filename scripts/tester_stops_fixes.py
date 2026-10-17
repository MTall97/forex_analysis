#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Les stratégies du journal avec un stop fixe de 20, 30, 40 ou 50 pips au lieu de leur stop d'origine.

Mêmes signaux, même entrée (prix et heure), même sortie au temps que chaque stratégie :
- englobante + MLQ (horaire 2024-2026 et journalier 2012-2026) : objectif 2 R, sortie à la clôture de J+3 ;
- lundi-mardi-mercredi (filtre masterclass) : objectif d'origine (plus haut / plus bas du lundi), et variante 2 R ;
  sortie à la clôture du vendredi ;
- cassure puis retour sur MLQ : objectif 2 R, sortie 120 h après l'entrée ; dans l'heure de l'entrée, seul le stop compte ;
- suivi de tendance : objectif 1 R, sortie à la bougie de 20h.
Stop prioritaire dans une même bougie ; spread déduit (en R du nouveau stop).
Sortie : data/stops_fixes/resultats.csv
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_englobante_fvg import charger  # noqa: E402
from tester_filtres_playbook import heure  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

STOPS = [20, 30, 40, 50]
_c = {}


def h1(p):
    if p not in _c:
        h = charger(p)
        _c[p] = (h, h['date'].to_numpy(), h['jour'].to_numpy())
    return _c[p]


def suivre(H, L, C, e, sl, tp, s, k0, k1, verif=None):
    """Prix réels ; s = +1 achat / -1 vente. Bougies k0..k1 ; verif : bougie d'entrée où seul le stop compte."""
    if verif is not None and ((L[verif] <= sl) if s > 0 else (H[verif] >= sl)):
        return -1.0
    R = abs(e - sl)
    for k in range(k0, min(k1, len(C) - 1) + 1):
        if (L[k] <= sl) if s > 0 else (H[k] >= sl):
            return -1.0
        if (H[k] >= tp) if s > 0 else (L[k] <= tp):
            return abs(tp - e) / R
    k = min(k1, len(C) - 1)
    return (C[k] - e) * s / R


def rejouer(nom, d, fin_fn, k0_fn, objectif, verif=False, decal=0):
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
        pp, sp = pip(t.paire), spread(t.paire)
        e = t.entree
        base = dict(strategie=nom, paire=t.paire, date=str(te)[:16], stop='origine', r=t.r)
        out.append(base)
        for x in STOPS:
            sl = e - s * x * pp
            for onom, tp in objectif(t, e, s, x * pp):
                r = suivre(H, L, C, e, sl, tp, s, k0 + (1 if verif else decal), k1, verif=k0 if verif else None)
                out.append(dict(base, stop=f'{x} pips', objectif=onom, r=r - sp / (x * pp)))
    return out


def k_apres(dates, te):        # entrée à la clôture : suivi dès la bougie qui ouvre à te ou après
    i = np.searchsorted(dates, np.datetime64(te), side='left')
    return int(i)


def k_dans(dates, te):         # entrée pendant la bougie qui ouvre à te
    i = np.searchsorted(dates, np.datetime64(te), side='left')
    return int(i)


def fin_j3(h, dates, jours, te, k0):
    js = sorted(set(jours[k0:k0 + 200]))
    if len(js) < 3:
        return None
    return int(np.where(jours == js[2])[0][-1])


def fin_vendredi(h, dates, jours, te, k0):
    vend = (te + pd.Timedelta(days=(4 - te.weekday()) % 7)).strftime('%Y-%m-%d')
    idx = np.where(jours == vend)[0]
    return int(idx[-1]) if len(idx) else None


def fin_120(h, dates, jours, te, k0):
    return k0 + 120


def fin_20h(h, dates, jours, te, k0):
    j = jours[k0]
    idx = np.where((jours == j) & (pd.DatetimeIndex(dates).hour == 20))[0]
    return int(idx[0]) if len(idx) else int(np.where(jours == j)[0][-1])


def journalier_englobante():
    d = pd.read_csv('data/journal_trades/englobante_mlq_journalier.csv').dropna(subset=['r'])
    jd = pd.read_csv('data/prix/journalier_dukascopy.csv')
    out = []
    for p, g in d.groupby('paire'):
        x = jd[jd['paire'] == p].reset_index(drop=True)
        dates = x['date'].tolist()
        H, L, C = x['high'].to_numpy(), x['low'].to_numpy(), x['close'].to_numpy()
        pp, sp = pip(p), spread(p)
        for t in g.itertuples():
            i = dates.index(t.entree_date_heure[:10])
            s = 1 if t.sens == 'achat' else -1
            base = dict(strategie='englobante + MLQ (journalier 2012-2026)', paire=p, date=t.entree_date_heure[:10],
                        stop='origine', r=t.r)
            out.append(base)
            for xp in STOPS:
                sl = t.entree - s * xp * pp
                tp = t.entree + s * 2 * xp * pp
                r = suivre(H, L, C, t.entree, sl, tp, s, i + 1, i + 3)
                out.append(dict(base, stop=f'{xp} pips', objectif='2 R', r=r - sp / (xp * pp)))
    return out


def lmm_trades():
    """Entrées LMM depuis la page des stratégies (mêmes règles) : reconstruites ici avec niveaux."""
    sys.path.insert(0, os.path.join(RACINE, 'scripts'))
    import construire_page_strategies as cps
    rows = []
    for t in cps.lmm():
        q = pip(t['p']) / 10
        rows.append(dict(paire=t['p'], sens=t['s'], entree_date_heure=t['te'], entree=t['e'],
                         objectif_px=t['e'] + t['tp'] * q, r=t['r']))
    return pd.DataFrame(rows)


def main():
    L = []
    d = pd.read_csv('data/journal_trades/englobante_mlq_horaire.csv').dropna(subset=['r'])
    L += rejouer('englobante + MLQ (horaire)', d, fin_j3, k_apres, lambda t, e, s, R: [('2 R', e + s * 2 * R)])
    L += journalier_englobante()
    lm = lmm_trades()
    L += rejouer('lundi-mardi-mercredi', lm, fin_vendredi, k_apres,
                 lambda t, e, s, R: [('objectif d\'origine', t.objectif_px), ('2 R', e + s * 2 * R)])
    d = pd.read_csv('data/journal_trades/cassure_retour_mlq.csv').dropna(subset=['r'])
    L += rejouer('cassure-retour MLQ', d, fin_120, k_dans, lambda t, e, s, R: [('2 R', e + s * 2 * R)], verif=True)
    d = pd.read_csv('data/journal_trades/suivi_tendance.csv').dropna(subset=['r'])
    L += rejouer('suivi de tendance 1 R', d, fin_20h, k_dans, lambda t, e, s, R: [('1 R', e + s * R)], decal=1)
    t = pd.DataFrame(L)
    t['objectif'] = t['objectif'].fillna('règle d\'origine')
    os.makedirs('data/stops_fixes', exist_ok=True)
    t.to_csv('data/stops_fixes/trades.csv.gz', index=False)
    res = []
    for (s, st, ob), g in t.groupby(['strategie', 'stop', 'objectif'], sort=False):
        r = g['r'].dropna()
        cum = np.cumsum(r.to_numpy())
        dd = (np.maximum.accumulate(np.r_[0, cum])[1:] - cum).max()
        half = g['date'] < sorted(g['date'])[len(g) // 2]
        res.append(dict(strategie=s, stop=st, objectif=ob, trades=len(r), gagnants=round((r > 0).mean(), 3),
                        r_moyen=round(r.mean(), 3), erreur_type=round(r.std() / np.sqrt(len(r)), 3),
                        r_1re_moitie=round(g.loc[half, 'r'].mean(), 3), r_2e_moitie=round(g.loc[~half, 'r'].mean(), 3),
                        baisse_max_R=round(dd, 1)))
    r = pd.DataFrame(res)
    r.to_csv('data/stops_fixes/resultats.csv', index=False)
    pd.set_option('display.width', 220)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
