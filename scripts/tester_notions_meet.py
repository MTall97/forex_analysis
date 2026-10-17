#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Notions du Google Meet d'Amirou (transmises par l'utilisateur le 17/10/2026), testées sur les deux stratégies suivies :
l'englobante sur un MLQ et la configuration lundi-mardi-mercredi (LMM, T2 de la masterclass).

A. « Préservation du capital : chercher 1 R avec plus de marge sur le stop » :
   même signal, même entrée (clôture), stop élargi (x1, x1,5, x2 la distance d'origine), objectif à 1 R du nouveau
   stop ; comparé à la règle actuelle (englobante : 2 R, stop x1 ; LMM : objectif au plus bas/haut du lundi).
   Même sortie au temps (englobante : clôture de J+3 ; LMM : clôture du vendredi) ; stop prioritaire dans une même
   bougie ; spread déduit. Mesures : R moyen, gagnants, pire série de pertes, baisse maximale (en R, trades pris dans
   l'ordre à risque fixe).
B. « US10Y, US02Y, VIX, sentiment, liens des paires » : chaque trade est classé selon ce que disaient, la veille,
   - le taux américain à 2 ans (FRED DGS2) : hausse sur 5 jours = dollar soutenu ; le trade est « dans le sens » s'il
     achète le dollar (ou le vend quand le 2 ans baisse) ; neutre si la paire ne contient pas le dollar ou si la
     variation est < 3 points de base ;
   - la pente 10 ans - 2 ans (DGS10 - DGS2) : même logique avec sa variation sur 5 jours (pentification = dollar faible) ;
   - le VIX (FRED VIXCLS) : hausse sur 5 jours = aversion au risque, qui soutient le yen et le franc suisse et pèse sur
     l'AUD, le NZD et le CAD ; le trade est « dans le sens » s'il achète la devise refuge contre une devise risquée
     (ou l'inverse quand le VIX baisse) ; neutre sinon ;
   - le régime de stress : VIX > 25 la veille.
Données : englobante journalier Dukascopy 10 paires 2012-2026 et horaire Yahoo 22 paires 2024-2026 ; LMM horaire
Yahoo 22 paires 2024-2026. Taux et VIX : data/prix/fred_macro/ (FRED).
Sortie : data/notions_meet/{trades.csv.gz, stop_1r.csv, macro.csv}
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO, charger  # noqa: E402
from tester_englobante_mlq_objectifs import niveau  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

SORTIE = 'data/notions_meet'
VARIANTES = [('règle actuelle', 1.0, None), ('1 R, stop x1', 1.0, 1), ('1 R, stop x1,5', 1.5, 1), ('1 R, stop x2', 2.0, 1)]
REFUGES, RISQUEES = {'JPY', 'CHF'}, {'AUD', 'NZD', 'CAD'}


def suivre(H, L, C, e, sl, tp):
    """Repère achat, bougies après l'entrée. R brut (stop prioritaire)."""
    R = e - sl
    for i in range(len(H)):
        if L[i] <= sl:
            return -1.0
        if H[i] >= tp:
            return (tp - e) / R
    return (C[-1] - e) / R


def variantes(base, H, L, C, e, R0, tp_regle, sp):
    out = []
    for nom, m, k in VARIANTES:
        sl = e - m * R0
        tp = tp_regle if k is None else e + k * m * R0
        if tp <= e:
            continue
        out.append(dict(base, variante=nom, r=round(suivre(H, L, C, e, sl, tp) - sp / (m * R0), 4)))
    return out


def englobantes_journalier():
    jd = pd.read_csv('data/prix/journalier_dukascopy.csv')
    lignes = []
    for p, d in jd[jd['paire'] != 'XAUUSD'].groupby('paire'):
        d = d.reset_index(drop=True)
        pp, sp = pip(p), spread(p)
        o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
        for i in range(1, len(d) - 3):
            if not (abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1]) and (c[i] - o[i]) * (c[i - 1] - o[i - 1]) < 0):
                continue
            s = 1 if c[i] > o[i] else -1
            H, L, C = (h, l, c) if s > 0 else (-l, -h, -c)
            e = C[i]
            R0 = e - (L[i] - 2 * pp)
            if R0 < 5 * pp:
                continue
            base = dict(strategie='englobante, journalier 2012-2026', paire=p, date=d['date'][i],
                        sens='achat' if s > 0 else 'vente', mlq=niveau(l[i] if s > 0 else h[i], pp, 0))
            lignes += variantes(base, H[i + 1:i + 4], L[i + 1:i + 4], C[i + 1:i + 4], e, R0, e + 2 * R0, sp)
    return lignes


def horaires():
    lignes = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = charger(p)
        pp, sp = pip(p), spread(p)
        jours = sorted(h['jour'].unique())
        pj = {j: g for j, g in h.groupby('jour')}
        d = pd.DataFrame([dict(jour=j, o=pj[j]['open'].iloc[0], h=pj[j]['high'].max(), l=pj[j]['low'].min(),
                               c=pj[j]['close'].iloc[-1], n=len(pj[j])) for j in jours])

        def tranche(js, s):
            a = pd.concat([pj[j] for j in js])
            return ((a['high'], a['low'], a['close']) if s > 0 else (-a['low'], -a['high'], -a['close']))

        # englobante
        for i in range(1, len(d) - 3):
            if d['n'][i] < 18 or d['n'][i - 1] < 18:
                continue
            o1, c1, o0, c0 = d['o'][i], d['c'][i], d['o'][i - 1], d['c'][i - 1]
            if not (abs(c1 - o1) >= abs(c0 - o0) and (c1 - o1) * (c0 - o0) < 0):
                continue
            s = 1 if c1 > o1 else -1
            e = c1 * s
            ext = d['l'][i] if s > 0 else d['h'][i]
            R0 = e - (ext * s - 2 * pp)
            if R0 < 5 * pp:
                continue
            H, L, C = (x.to_numpy() for x in tranche(d['jour'][i + 1:i + 4], s))
            base = dict(strategie='englobante, horaire 2024-2026', paire=p, date=d['jour'][i],
                        sens='achat' if s > 0 else 'vente', mlq=niveau(ext, pp, 0))
            lignes += variantes(base, H, L, C, e, R0, e + 2 * R0, sp)
        # lundi-mardi-mercredi (T2)
        for i in range(len(d) - 2):
            lun, mar = pd.Timestamp(d['jour'][i]), pd.Timestamp(d['jour'][i + 1])
            if lun.weekday() != 0 or mar - lun != pd.Timedelta(days=1) or d['n'][i] < 18 or d['n'][i + 1] < 18:
                continue
            semaine = [j for j in d['jour'][i + 2:i + 5] if pd.Timestamp(j) - lun < pd.Timedelta(days=5)]
            if not semaine or pd.Timestamp(semaine[0]).weekday() != 2:
                continue
            o, hi, lo, c = d['o'][i], d['h'][i], d['l'][i], d['c'][i]
            o2, c2 = d['o'][i + 1], d['c'][i + 1]
            rng = hi - lo
            if rng <= 0 or abs(c - o) < 0.6 * rng:
                continue
            if c > o and c >= hi - 0.25 * rng and c2 < o2 and c2 < c:
                s = -1
            elif c < o and c <= lo + 0.25 * rng and c2 > o2 and c2 > c:
                s = 1
            else:
                continue
            e = c2 * s
            sl = (d['l'][i + 1] if s > 0 else d['h'][i + 1]) * s - 2 * pp
            tp = hi if s > 0 else -lo
            R0, dist = e - sl, tp - e
            if R0 <= 0 or dist <= 0:
                continue
            H, L, C = (x.to_numpy() for x in tranche(semaine, s))
            base = dict(strategie='lundi-mardi-mercredi, horaire 2024-2026', paire=p, date=d['jour'][i + 1],
                        sens='achat' if s > 0 else 'vente', mlq=bool(dist >= 60 * pp and dist / R0 >= 1.2))
            lignes += variantes(base, H, L, C, e, R0, tp, sp)
    return lignes


def parcours(r):
    """Pire série de pertes et baisse maximale (en R), trades dans l'ordre."""
    cum = np.cumsum(r)
    dd = (np.maximum.accumulate(np.r_[0, cum])[1:] - cum).max() if len(r) else 0
    serie = m = 0
    for x in r:
        serie = serie + 1 if x < 0 else 0
        m = max(m, serie)
    return m, dd


def macro(t):
    f = {k: pd.read_csv(f'data/prix/fred_macro/{k}.csv', parse_dates=['observation_date'], na_values='.')
         .set_index('observation_date')[k] for k in ['DGS10', 'DGS2', 'VIXCLS']}
    m = pd.DataFrame(f).ffill()
    m['d2y'] = m['DGS2'].diff(5)
    m['dpente'] = (m['DGS10'] - m['DGS2']).diff(5)
    m['dvix'] = m['VIXCLS'].diff(5)
    m = m.shift(1)                                     # connu la veille
    j = pd.to_datetime(t['date'].str[:10])
    u = m.reindex(m.index.union(pd.DatetimeIndex(j.unique()))).ffill()
    x = u.reindex(j)
    s = np.where(t['sens'] == 'achat', 1, -1)
    base, cote = t['paire'].str[:3].to_numpy(), t['paire'].str[3:].to_numpy()
    usd = np.where(base == 'USD', 1, np.where(cote == 'USD', -1, 0)) * s       # +1 = le trade achète le dollar

    def classe(signal, expo, seuil):
        v = np.sign(signal) * (np.abs(signal) >= seuil)
        a = v * expo
        return np.select([expo == 0, v == 0, a > 0], ['sans objet', 'neutre', 'dans le sens'], 'contre')
    t['taux_2_ans'] = classe(x['d2y'].to_numpy(), usd, 0.03)
    t['pente_10_2'] = classe(-x['dpente'].to_numpy(), usd, 0.03)
    ref = np.where(np.isin(base, list(REFUGES)) & np.isin(cote, list(RISQUEES)), 1,
                   np.where(np.isin(cote, list(REFUGES)) & np.isin(base, list(RISQUEES)), -1, 0)) * s
    t['vix'] = classe(x['dvix'].to_numpy(), ref, 0.5)
    t['vix_stress'] = np.where(x['VIXCLS'].to_numpy() > 25, 'VIX > 25', 'VIX <= 25')
    return t


def main():
    os.makedirs(SORTIE, exist_ok=True)
    t = pd.DataFrame(englobantes_journalier() + horaires())
    t.to_csv(f'{SORTIE}/trades.csv.gz', index=False)
    res = []
    for (st, v), g in t.groupby(['strategie', 'variante'], sort=False):
        groupes = ({'achats MLQ (règle en démo)': (g['sens'] == 'achat') & g['mlq'], 'toutes MLQ': g['mlq'],
                    'toutes englobantes': g['mlq'] | ~g['mlq']} if st.startswith('englobante') else
                   {'avec le filtre de la masterclass': g['mlq'], 'toutes les configurations': g['mlq'] | ~g['mlq']})
        for nom, m in groupes.items():
            x = g[m].sort_values('date')
            serie, dd = parcours(x['r'].to_numpy())
            res.append(dict(strategie=st, sous_ensemble=nom, variante=v, trades=len(x),
                            gagnants=round((x['r'] > 0).mean(), 3), r_moyen=round(x['r'].mean(), 3),
                            erreur_type=round(x['r'].std() / np.sqrt(len(x)), 3), pire_serie_pertes=serie,
                            baisse_max_R=round(dd, 1)))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/stop_1r.csv', index=False)
    pd.set_option('display.width', 230)
    print(r.to_string(index=False))
    # B. filtres macro, sur la règle actuelle
    a = macro(t[t['variante'] == 'règle actuelle'].copy())
    res = []
    for st, g in a.groupby('strategie', sort=False):
        for filtre in ['taux_2_ans', 'pente_10_2', 'vix', 'vix_stress']:
            for c, x in g.groupby(filtre):
                res.append(dict(strategie=st, filtre=filtre, classe=c, trades=len(x),
                                gagnants=round((x['r'] > 0).mean(), 3), r_moyen=round(x['r'].mean(), 3),
                                erreur_type=round(x['r'].std() / np.sqrt(len(x)), 3)))
    m = pd.DataFrame(res)
    m.to_csv(f'{SORTIE}/macro.csv', index=False)
    print(m.to_string(index=False))


if __name__ == '__main__':
    main()
