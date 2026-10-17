#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Données de la page « Journal des stratégies » (même structure que le tracker saisonnalité & fonda) : pour chaque
stratégie, une ligne par mois, et pour chaque trade les bougies autour de l'entrée, pour dessiner deux images :
« au moment de l'entrée » (le futur masqué) et « après » (jusqu'à la sortie).

Stratégies (trades déjà rejoués, règles inchangées) :
- englobante + MLQ, horaire 2024-2026 (data/journal_trades/englobante_mlq_horaire.csv) ;
- lundi-mardi-mercredi avec le filtre de la masterclass (rejoué ici, mêmes règles que scripts/tester_entrees_lmm.py :
  entrée à la clôture du mardi, stop 2 pips au-delà du mardi, objectif au plus haut/bas du lundi, sortie vendredi) ;
- cassure puis retour sur MLQ (data/journal_trades/cassure_retour_mlq.csv) ;
- suivi de tendance 1 R (data/journal_trades/suivi_tendance.csv) ;
- checklist A+ du playbook, complète (data/checklist_a_plus/{horaire,journalier}.csv).
Bougies : horaire Yahoo (agrégé en 4 h pour les stratégies journalières), journalier Dukascopy pour la checklist en
journalier. Prix codés en dixièmes de pip relatifs à l'entrée.

Usage : python scripts/construire_page_strategies.py DOSSIER   ->  DOSSIER/strategies/<clé>.json, DOSSIER/index.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO, charger  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

AVANT, APRES, MAXB = 36, 6, 150
_cache = {}


def horaire(p):
    if p not in _cache:
        h = charger(p).set_index('date')[['open', 'high', 'low', 'close']]
        _cache[p] = h
    return _cache[p]


def en4h(h):
    g = h.resample('4h', origin='epoch')
    x = pd.DataFrame({'open': g['open'].first(), 'high': g['high'].max(), 'low': g['low'].min(), 'close': g['close'].last()})
    return x.dropna()


_c4 = {}


def h4(p):
    if p not in _c4:
        _c4[p] = en4h(horaire(p))
    return _c4[p]


_dk = None


def jour(p):
    global _dk
    if _dk is None:
        _dk = pd.read_csv('data/prix/journalier_dukascopy.csv', parse_dates=['date'])
    return _dk[_dk['paire'] == p].set_index('date')[['open', 'high', 'low', 'close']]


def heure(s):
    s = str(s).replace(' (clôture)', '').replace(' clôture', '').replace(' (jour)', '').strip()
    if s.endswith('24:00'):
        return pd.Timestamp(s[:10]) + pd.Timedelta(days=1)
    return pd.Timestamp(s)


def fenetre(b, te, tx):
    """Bougies : AVANT bougies dont l'ouverture précède l'entrée, puis jusqu'à la sortie + APRES."""
    avant = b[b.index < te].tail(AVANT)
    apres = b[(b.index >= te) & (b.index <= tx)]
    suite = b[b.index > tx].head(APRES)
    w = pd.concat([avant, apres, suite])
    pas = 1
    while len(w) > MAXB * pas:
        pas += 1
    return w, len(avant), len(avant) + max(len(apres) - 1, 0), pas


def coder(p, w, e, i0, ix, pas):
    q = pip(p) / 10
    if pas > 1:   # trop de bougies : on regroupe par paquets, en gardant l'entrée et la sortie lisibles
        grp = np.arange(len(w)) // pas
        w = w.groupby(grp).agg(open=('open', 'first'), high=('high', 'max'), low=('low', 'min'), close=('close', 'last'))
        i0, ix = i0 // pas, ix // pas
    bars = [[int(round((r.open - e) / q)), int(round((r.high - e) / q)), int(round((r.low - e) / q)),
             int(round((r.close - e) / q))] for r in w.itertuples()]
    return bars, i0, ix


def ligne(p, s, te, tx, e, sl, tp, r, motif, tf, b, extra=None):
    w, i0, ix, pas = fenetre(b, te, tx)
    if i0 == 0 or not len(w):
        return None
    bars, i0, ix = coder(p, w, e, i0, ix, pas)
    q = pip(p) / 10
    return dict(p=p, s=s, te=te.strftime('%Y-%m-%d %H:%M'), tx=tx.strftime('%Y-%m-%d %H:%M'), e=round(e, 5),
                sl=int(round((sl - e) / q)), tp=int(round((tp - e) / q)), r=None if pd.isna(r) else round(float(r), 2),
                mo=motif, tf=tf if pas == 1 else f'{tf}×{pas}', t0=w.index[0].strftime('%Y-%m-%d %H:%M'), i0=i0, ix=ix,
                b=bars, **(extra or {}))


def depuis_journal(f, tf):
    out = []
    for t in pd.read_csv(f).itertuples():
        if t.motif_sortie == 'en cours':
            continue
        te, tx = heure(t.entree_date_heure), heure(t.sortie_date_heure)
        b = h4(t.paire) if tf == '4h' else horaire(t.paire)
        x = ligne(t.paire, t.sens, te, tx, t.entree, t.stop, t.objectif, t.r, t.motif_sortie, tf, b, dict(sig=t.signal))
        if x:
            out.append(x)
    return out


def lmm():
    out = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = horaire(p)
        pp, sp = pip(p), spread(p)
        jours = sorted(set(h.index.strftime('%Y-%m-%d')))
        pj = {j: g for j, g in h.groupby(h.index.strftime('%Y-%m-%d'))}
        for i in range(len(jours) - 2):
            lun, mar = pd.Timestamp(jours[i]), pd.Timestamp(jours[i + 1])
            if lun.weekday() != 0 or mar - lun != pd.Timedelta(days=1):
                continue
            g1, g2 = pj[jours[i]], pj[jours[i + 1]]
            if len(g1) < 18 or len(g2) < 18:
                continue
            semaine = [j for j in jours[i + 2:i + 5] if pd.Timestamp(j) - lun < pd.Timedelta(days=5)]
            if not semaine or pd.Timestamp(semaine[0]).weekday() != 2:
                continue
            o, hi, lo, c = g1['open'].iloc[0], g1['high'].max(), g1['low'].min(), g1['close'].iloc[-1]
            o2, c2 = g2['open'].iloc[0], g2['close'].iloc[-1]
            rng = hi - lo
            if rng <= 0 or abs(c - o) < 0.6 * rng:
                continue
            if c > o and c >= hi - 0.25 * rng and c2 < o2 and c2 < c:
                s = -1
            elif c < o and c <= lo + 0.25 * rng and c2 > o2 and c2 > c:
                s = 1
            else:
                continue
            e = c2
            sl = (g2['low'].min() - 2 * pp) if s > 0 else (g2['high'].max() + 2 * pp)
            tp = hi if s > 0 else lo
            R, dist = (e - sl) * s, (tp - e) * s
            if R <= 0 or dist <= 0 or not (dist >= 60 * pp and dist / R >= 1.2):
                continue
            a = pd.concat([pj[j] for j in semaine])
            res, motif, tx = None, 'échéance', a.index[-1]
            for t, r_ in a.iterrows():
                if (r_['low'] <= sl) if s > 0 else (r_['high'] >= sl):
                    res, motif, tx = -1.0, 'stop', t
                    break
                if (r_['high'] >= tp) if s > 0 else (r_['low'] <= tp):
                    res, motif, tx = dist / R, 'objectif', t
                    break
            if res is None:
                res = (a['close'].iloc[-1] - e) * s / R
            te = pd.Timestamp(jours[i + 1]) + pd.Timedelta(days=1)
            x = ligne(p, 'achat' if s > 0 else 'vente', te, tx, e, sl, tp, res - sp / R, motif, '4h', h4(p),
                      dict(sig='lundi plein, mardi contraire'))
            if x:
                out.append(x)
    return out


def checklist():
    out = []
    c = ['orderflow_w', 'orderflow_d', 'discount', 'sous_weekly_open', 'cible_300', 'ote', 'ratio_3']
    for f, tf in [('data/checklist_a_plus/horaire.csv', '1h'), ('data/checklist_a_plus/journalier.csv', '1d')]:
        d = pd.read_csv(f)
        d = d[d[c].all(axis=1) & d['r'].notna()]
        for t in d.itertuples():
            te = heure(t.entree_date_heure)
            tx = heure(t.sortie_date_heure)
            if tf == '1d':
                te = te + pd.Timedelta(hours=12)   # entrée pendant la journée : la bougie du jour reste « au moment »
                b = jour(t.paire)
            else:
                b = horaire(t.paire)
            x = ligne(t.paire, t.sens, te, tx, t.entree, t.stop, t.objectif, t.r, t.motif, tf, b,
                      dict(sig='checklist A+ complète (' + ('horaire' if tf == '1h' else 'journalier') + ')'))
            if x:
                out.append(x)
    return out


STRATS = [
    ('englobante', 'Englobante + MLQ', depuis_journal, ('data/journal_trades/englobante_mlq_horaire.csv', '4h'),
     "Bougie journalière qui englobe le corps de la veille, dont l'extrême touche un MLQ (multiple de 250 pips, à 25 pips "
     "près). Entrée à la clôture, stop 2 pips derrière l'extrême, objectif 2 R, sortie au plus tard à la clôture de J+3.",
     'ENGLOBANTE_MLQ_ET_SUIVI_TENDANCE.md',
     "Achats : +0,15 R par trade en 2024-2026, mais négatif sur 2012-2019. Suivi en démo depuis le 02/10/2026."),
    ('lmm', 'Lundi-mardi-mercredi', None, None,
     "Lundi « plein » (corps ≥ 60 % de la bougie, clôture dans le quart extrême), mardi de couleur opposée qui clôture en "
     "deçà. Entrée à la clôture du mardi dans le sens du mardi, stop 2 pips au-delà du mardi, objectif au plus haut ou "
     "plus bas du lundi, sortie vendredi. Filtre : objectif ≥ 60 pips et ratio ≥ 1,2.",
     'ENTREES_LUNDI_MARDI_MERCREDI.md', "+0,39 R par trade sur 88 trades (2024-2026), à confirmer : échantillon petit."),
    ('cassure', 'Cassure puis retour sur MLQ', depuis_journal, ('data/journal_trades/cassure_retour_mlq.csv', '1h'),
     "Le prix clôture au-delà d'un MLQ, s'en éloigne de 0,3 ATR sans reclôturer de l'autre côté, puis revient dessus : "
     "ordre limite sur le niveau, stop à 0,5 ATR, objectif 2 R, sortie après 5 jours.",
     'CASSURE_RETOUR_MLQ.md', "Environ 0 R par trade, comme sur des niveaux décalés sans signification."),
    ('tendance', 'Suivi de tendance 1 R', depuis_journal, ('data/journal_trades/suivi_tendance.csv', '1h'),
     "Tendance d'au moins 1 ATR sur 5 jours ; entre 07h et 17h UTC, cassure du plus haut (ou plus bas) de la veille dans "
     "le sens de la tendance ; stop 0,25 ATR, objectif 1 R, sortie à 20h.",
     'ENGLOBANTE_MLQ_ET_SUIVI_TENDANCE.md', "−0,13 R par trade après spread : pile ou face avant frais."),
    ('a_plus', 'Checklist A+ du playbook', None, None,
     "Les 9 points du playbook traduits en règles : orderflow weekly et daily, discount, sous l'ouverture de la semaine, "
     "FVG journalier, OTE, confirmation H1 en killzone (horaire), stop ≥ 50 pips, objectif au plus haut ou plus bas de la "
     "semaine précédente, ratio ≥ 3.",
     'CHECKLIST_A_PLUS.md', "13 à 33 % de gagnants, pas 90 % ; +0,18 R ± 0,24 sur 2012-2026 ; très rare."),
]


def main():
    sortie = sys.argv[1]
    os.makedirs(f'{sortie}/strategies', exist_ok=True)
    index = []
    for cle, nom, f, args, regle, rapport, verdict in STRATS:
        if cle == 'lmm':
            t = lmm()
        elif cle == 'a_plus':
            t = checklist()
        else:
            t = f(*args)
        t.sort(key=lambda x: x['te'])
        js = json.dumps(t, ensure_ascii=False, separators=(',', ':'))
        open(f'{sortie}/strategies/{cle}.json', 'w', encoding='utf-8').write(js)
        r = np.array([x['r'] for x in t if x['r'] is not None])
        index.append(dict(cle=cle, nom=nom, regle=regle, rapport=rapport, verdict=verdict, n=len(t),
                          gagnants=round(float((r > 0).mean()), 3), r_moyen=round(float(r.mean()), 3),
                          et=round(float(r.std() / np.sqrt(len(r))), 3), debut=t[0]['te'][:7], fin=t[-1]['te'][:7]))
        print(f"{nom:32s} {len(t):5d} trades  {len(js) / 1e6:.2f} Mo  R moyen {r.mean():+.3f}")
    json.dump(index, open(f'{sortie}/index.json', 'w', encoding='utf-8'), ensure_ascii=False)


if __name__ == '__main__':
    main()
