#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Journal détaillé, trade par trade, des trois stratégies testées, pour pouvoir vérifier chaque trade sur un graphique :
entrée (date, heure, prix), stop, objectif, sortie (date, heure, prix, motif) et résultat en R.

Variantes retenues (celles des rapports, sans en changer les règles) :
1. englobante + MLQ, objectif 2 R, sortie au plus tard à la clôture de J+3 (analyses/ENGLOBANTE_MLQ_ET_SUIVI_TENDANCE.md) :
   - « horaire » : 22 paires, 12/2023-10/2026, cours Yahoo horaires ;
   - « journalier » : 10 paires, 2012-2026, cours Dukascopy journaliers (heure de sortie inconnue : jour seulement ;
     si le stop et l'objectif sont touchés le même jour, le stop compte) ;
2. cassure puis retour sur MLQ, stop 0,5 ATR, objectif 2 R, 22 paires en horaire (analyses/CASSURE_RETOUR_MLQ.md) ;
3. suivi de tendance « cassure du plus haut / plus bas de la veille », tendance >= 1 ATR, stop 0,25 ATR,
   objectif 1 R, sortie à la bougie de 20h UTC (analyses/ENGLOBANTE_MLQ_ET_SUIVI_TENDANCE.md).

Conventions : heures en UTC ; l'heure d'une bougie horaire est celle de son ouverture (« 14:00 » = 14h-15h) ;
les trades encore ouverts à la fin des données ont le motif « en cours » et pas de R ;
dans une même bougie, le stop passe avant l'objectif (r) — r_optimiste donne l'inverse quand c'est ambigu ;
spread déduit dans r. Les prix sont ceux de Yahoo / Dukascopy, pas ceux d'un courtier.

On ajoute à chaque trade des variables connues au moment de l'entrée (tendance, volatilité, jour, heure, narratif
d'Amirou, COT, écart de taux), qui servent au test de sélection des trades (scripts/tester_selection_trades.py).
Sortie : data/journal_trades/{englobante_mlq_horaire,englobante_mlq_journalier,cassure_retour_mlq,suivi_tendance}.csv
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_cassure_retour_mlq import scanner  # noqa: E402
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO, charger  # noqa: E402
from tester_englobante_mlq_objectifs import niveau  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

SORTIE = 'data/journal_trades'
PAIRES = PAIRES_DEMO + PAIRES_AUTRES


def journalier_depuis_horaire(h):
    g = h.groupby('jour')
    d = pd.DataFrame({'open': g['open'].first(), 'high': g['high'].max(), 'low': g['low'].min(),
                      'close': g['close'].last(), 'n': g.size()}).reset_index()
    return d


def contexte(d):
    """Variables journalières connues à la clôture de chaque jour (index = jour)."""
    tr = np.maximum(d['high'] - d['low'], np.maximum(abs(d['high'] - d['close'].shift()), abs(d['low'] - d['close'].shift())))
    atr = tr.rolling(14).mean()
    return pd.DataFrame({'atr14': atr, 'vol_relative': atr / atr.rolling(100).mean(),
                         'tendance_5j': (d['close'] - d['close'].shift(5)) / atr,
                         'tendance_20j': (d['close'] - d['close'].shift(20)) / atr,
                         'position_60j': (d['close'] - d['low'].rolling(60).min())
                         / (d['high'].rolling(60).max() - d['low'].rolling(60).min())})


def suivre(H, L, C, dates, k_debut, k_fin, e, sl, tp, verif_entree=None):
    """Repère achat. Bougies k_debut..k_fin incluses ; verif_entree : bougie d'entrée où seul le stop compte.
    Renvoie (motif, indice de sortie, prix de sortie, R brut pessimiste, R brut optimiste)."""
    R = e - sl
    if verif_entree is not None and L[verif_entree] <= sl:
        return 'stop', verif_entree, sl, -1.0, -1.0
    for k in range(k_debut, min(k_fin, len(C) - 1) + 1):
        st, ob = L[k] <= sl, H[k] >= tp
        if st:
            return 'stop', k, sl, -1.0, ((tp - e) / R if ob else -1.0)
        if ob:
            return 'objectif', k, tp, (tp - e) / R, (tp - e) / R
    k = min(k_fin, len(C) - 1)
    if k == len(C) - 1:                               # fin des données avant la sortie prévue : trade encore ouvert
        return 'en cours', k, C[k], np.nan, np.nan
    return "sortie à l'échéance", k, C[k], (C[k] - e) / R, (C[k] - e) / R


def reel(x, s):
    return x * s if x is not None else None


def ligne(strategie, p, s, signal, quand_entree, e, sl, tp, motif, quand_sortie, px_sortie, rp, ro, R, extra):
    pp, sp = pip(p), spread(p)
    nd = 3 if p.endswith('JPY') else 5
    return dict(strategie=strategie, paire=p, sens='achat' if s > 0 else 'vente', signal=signal,
                entree_date_heure=quand_entree, entree=round(e * s, nd), stop=round(sl * s, nd), objectif=round(tp * s, nd),
                risque_pips=round(R / pp, 1), sortie_date_heure=quand_sortie, sortie=round(px_sortie * s, nd),
                motif_sortie=motif, r=round(rp - sp / R, 3), r_optimiste=round(ro - sp / R, 3), **extra)


def repere(o, h, l, c, s):
    return (o, h, l, c) if s > 0 else (-o, -l, -h, -c)


# ---------------------------------------------------------------- 1. englobante + MLQ
def englobante_horaire():
    lignes = []
    for p in PAIRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = charger(p)
        d = journalier_depuis_horaire(h)
        ctx = contexte(d)
        pp = pip(p)
        jour_h = h['jour'].to_numpy()
        dates = h['date'].dt.strftime('%Y-%m-%d %H:%M').to_numpy()
        debut_jour = {j: i for i, j in reversed(list(enumerate(jour_h)))}
        fin_jour = {j: i for i, j in enumerate(jour_h)}
        o, c = d['open'].to_numpy(), d['close'].to_numpy()
        for i in range(1, len(d) - 3):
            if not (abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1]) and (c[i] - o[i]) * (c[i - 1] - o[i - 1]) < 0):
                continue
            if d['n'][i] < 18 or d['n'][i - 1] < 18:
                continue
            s = 1 if c[i] > o[i] else -1
            ext = d['low'][i] if s > 0 else d['high'][i]
            if not niveau(ext, pp, 0):
                continue
            O, H, L, C = repere(*(h[k].to_numpy() for k in ['open', 'high', 'low', 'close']), s)
            e = c[i] * s
            sl = (d['low'][i] - 2 * pp) if s > 0 else -(d['high'][i] + 2 * pp)
            R = e - sl
            if R < 5 * pp:
                continue
            tp = e + 2 * R
            k0, k1 = fin_jour[d['jour'][i]] + 1, fin_jour[d['jour'][i + 3]]
            motif, k, px, rp, ro = suivre(H, L, C, dates, k0, k1, e, sl, tp)
            entree = f"{d['jour'][i]} 24:00 (clôture)"
            sortie = dates[k] + (' (clôture)' if motif in ("sortie à l'échéance", 'en cours') else '')
            x = ctx.iloc[i]
            lignes.append(ligne('englobante + MLQ (horaire)', p, s, f"englobante du {d['jour'][i]}", entree, e, sl, tp,
                                motif, sortie, px, rp, ro, R,
                                dict(niveau_mlq=round(round(ext / (250 * pp)) * 250 * pp, 5), heure=0,
                                     jour_semaine=pd.Timestamp(d['jour'][i]).weekday(), risque_atr=round(R / x['atr14'], 2),
                                     tendance_5j=round(x['tendance_5j'] * s, 2), tendance_20j=round(x['tendance_20j'] * s, 2),
                                     vol_relative=round(x['vol_relative'], 2),
                                     position_60j=round(x['position_60j'] if s > 0 else 1 - x['position_60j'], 2),
                                     jour_connu=d['jour'][i])))
    return pd.DataFrame(lignes)


def englobante_journalier():
    jd = pd.read_csv('data/prix/journalier_dukascopy.csv')
    lignes = []
    for p, d in jd[jd['paire'] != 'XAUUSD'].groupby('paire'):
        d = d.reset_index(drop=True)
        ctx = contexte(d)
        pp = pip(p)
        o, c = d['open'].to_numpy(), d['close'].to_numpy()
        dates = d['date'].to_numpy()
        for i in range(1, len(d) - 3):
            if not (abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1]) and (c[i] - o[i]) * (c[i - 1] - o[i - 1]) < 0):
                continue
            s = 1 if c[i] > o[i] else -1
            ext = d['low'][i] if s > 0 else d['high'][i]
            if not niveau(ext, pp, 0):
                continue
            O, H, L, C = repere(o, d['high'].to_numpy(), d['low'].to_numpy(), c, s)
            e = c[i] * s
            sl = (d['low'][i] - 2 * pp) if s > 0 else -(d['high'][i] + 2 * pp)
            R = e - sl
            if R < 5 * pp:
                continue
            tp = e + 2 * R
            motif, k, px, rp, ro = suivre(H, L, C, dates, i + 1, i + 3, e, sl, tp)
            x = ctx.iloc[i]
            lignes.append(ligne('englobante + MLQ (journalier)', p, s, f'englobante du {dates[i]}',
                                f'{dates[i]} clôture', e, sl, tp, motif,
                                f'{dates[k]}' + (' clôture' if motif in ("sortie à l'échéance", 'en cours') else ' (jour)'), px, rp, ro, R,
                                dict(niveau_mlq=round(round(ext / (250 * pp)) * 250 * pp, 5), heure=0,
                                     jour_semaine=pd.Timestamp(dates[i]).weekday(), risque_atr=round(R / x['atr14'], 2),
                                     tendance_5j=round(x['tendance_5j'] * s, 2), tendance_20j=round(x['tendance_20j'] * s, 2),
                                     vol_relative=round(x['vol_relative'], 2),
                                     position_60j=round(x['position_60j'] if s > 0 else 1 - x['position_60j'], 2),
                                     jour_connu=dates[i])))
    return pd.DataFrame(lignes)


# ---------------------------------------------------------------- 2. cassure puis retour sur MLQ
def cassure_retour():
    lignes = []
    for p in PAIRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = charger(p)
        d = journalier_depuis_horaire(h)
        ctx = contexte(d)
        atr_j = ctx['atr14'].shift(1)
        atr = h['jour'].map(dict(zip(d['jour'], atr_j))).to_numpy()
        ctx_veille = ctx.shift(1)
        ctx_veille.index = d['jour']
        pp = pip(p)
        o, hi, lo, c = (h[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
        dates = h['date'].dt.strftime('%Y-%m-%d %H:%M').to_numpy()
        for s in (1, -1):
            O, H, L, C = repere(o, hi, lo, c, s)
            for t in scanner(o, hi, lo, c, atr, pp, 0, 48, 120, s):
                k, e = t['i_entree'], t['entree_repere']
                R = 0.5 * t['atr']
                sl, tp = e - R, e + 2 * R
                motif, kk, px, rp, ro = suivre(H, L, C, dates, k + 1, k + 120, e, sl, tp, verif_entree=k)
                x = ctx_veille.loc[h['jour'][k]]
                lignes.append(ligne('cassure puis retour MLQ', p, s, f"retour sur {t['niveau']:g}", dates[k], e, sl, tp,
                                    motif, dates[kk] + (' (clôture)' if motif in ("sortie à l'échéance", 'en cours') else ''), px, rp, ro, R,
                                    dict(niveau_mlq=t['niveau'], heure=int(dates[k][11:13]),
                                         jour_semaine=pd.Timestamp(dates[k]).weekday(), risque_atr=0.5,
                                         tendance_5j=round(x['tendance_5j'] * s, 2), tendance_20j=round(x['tendance_20j'] * s, 2),
                                         vol_relative=round(x['vol_relative'], 2),
                                         position_60j=round(x['position_60j'] if s > 0 else 1 - x['position_60j'], 2),
                                         jour_connu=str((pd.Timestamp(dates[k][:10]) - pd.Timedelta(days=1)).date()))))
    return pd.DataFrame(lignes)


# ---------------------------------------------------------------- 3. suivi de tendance (cassure, 1 R)
def suivi_tendance():
    lignes = []
    for p in PAIRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = charger(p)
        pp = pip(p)
        d = journalier_depuis_horaire(h)
        ctx = contexte(d)
        atr = ctx['atr14'].shift(1).to_numpy()
        heure = h['date'].dt.hour.to_numpy()
        dates = h['date'].dt.strftime('%Y-%m-%d %H:%M').to_numpy()
        jour_h = h['jour'].to_numpy()
        idx = {j: np.where(jour_h == j)[0] for j in d['jour']}
        o, hi, lo, c = (h[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
        for i in range(15, len(d) - 1):
            if d['n'][i] < 18 or d['n'][i - 1] < 18 or np.isnan(atr[i]):
                continue
            mouvement = (d['close'][i - 1] - d['close'][i - 6]) / atr[i]
            ix = idx[d['jour'][i]]
            fin = next((k for k in ix if heure[k] == 20), ix[-1])
            fen = [k for k in ix if 7 <= heure[k] < 17]
            for s in (1, -1):
                if round(mouvement * s, 2) < 1:          # même arrondi que tester_suivi_tendance.py
                    continue
                O, H, L, C = repere(o, hi, lo, c, s)
                niv = (d['high'][i - 1] if s > 0 else -d['low'][i - 1]) + pp
                k0 = next((k for k in fen if H[k] >= niv), None)
                if k0 is None or fin <= k0:
                    continue
                e = max(niv, O[k0])
                R = 0.25 * atr[i]
                sl, tp = e - R, e + R
                motif, kk, px, rp, ro = suivre(H, L, C, dates, k0 + 1, fin, e, sl, tp)
                x = ctx.iloc[i - 1]
                lignes.append(ligne('suivi de tendance 1 R', p, s,
                                    f"cassure du {'plus haut' if s > 0 else 'plus bas'} de la veille", dates[k0], e, sl, tp,
                                    motif, dates[kk] + (' (clôture)' if motif in ("sortie à l'échéance", 'en cours') else ''), px, rp, ro, R,
                                    dict(niveau_mlq=np.nan, heure=int(heure[k0]), jour_semaine=pd.Timestamp(d['jour'][i]).weekday(),
                                         risque_atr=0.25, tendance_5j=round(mouvement * s, 2),
                                         tendance_20j=round(x['tendance_20j'] * s, 2), vol_relative=round(x['vol_relative'], 2),
                                         position_60j=round(x['position_60j'] if s > 0 else 1 - x['position_60j'], 2),
                                         jour_connu=d['jour'][i - 1])))
    return pd.DataFrame(lignes)


def fondamentaux(t):
    """Écarts base - cotation connus la veille : narratif d'Amirou (14 j), COT, taux directeurs."""
    ind = pd.read_csv('data/fondamental/indicateurs.csv', parse_dates=['date'])
    piv = {v: ind.pivot_table(index='date', columns='devise', values=v).sort_index().ffill() for v in ['amirou_14j', 'cot', 'taux']}
    jours = pd.to_datetime(t['jour_connu'])
    s = np.where(t['sens'] == 'achat', 1, -1)
    for v, nom in [('amirou_14j', 'narratif'), ('cot', 'cot_ecart'), ('taux', 'taux_ecart')]:
        b = piv[v]
        val = []
        for p, j in zip(t['paire'], jours):
            a, q = p[:3], p[3:]
            if a not in b.columns or q not in b.columns or j < b.index[0]:
                val.append(np.nan)
                continue
            r = b.loc[:j].iloc[-1]
            val.append(r[a] - r[q])
        t[nom] = np.round(np.array(val, dtype=float) * s, 4)
    if 'narratif' in t:
        t['narratif'] = t['narratif'].fillna(0)
    return t


def main():
    os.makedirs(SORTIE, exist_ok=True)
    for nom, f in [('englobante_mlq_horaire', englobante_horaire), ('englobante_mlq_journalier', englobante_journalier),
                   ('cassure_retour_mlq', cassure_retour), ('suivi_tendance', suivi_tendance)]:
        t = fondamentaux(f()).sort_values('entree_date_heure').reset_index(drop=True)
        t.to_csv(f'{SORTIE}/{nom}.csv', index=False)
        print(f"{nom:28s} {len(t):5d} trades  {t['entree_date_heure'].min()[:10]} -> {t['entree_date_heure'].max()[:10]}  "
              f"gagnants {(t['r'] > 0).mean():.1%}  R moyen {t['r'].mean():+.3f}")


if __name__ == '__main__':
    main()
