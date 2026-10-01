#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérifie les « flashcards » d'Amirou (cartes illustrées de personnages de Naruto, mai 2025 - juin 2026) :
« Probabilités de Rupture (3 Jours) » des configurations englobantes (engulfing) en journalier.

Lecture des cartes : après une bougie journalière englobante baissière, son plus bas est cassé dans
les 3 jours suivants dans ~71-81 % des cas (haussière : son plus haut, ~72-83 %), le plus souvent dès
le jour 1. Messages : #13327 USDJPY, #13340 EURNZD, #13343 USDCAD, #13355 XAUUSD, #13387 GBPJPY,
#13395 NZDUSD, #13409 AUDJPY, #13456 et #13804 EURUSD, #13618 GBPUSD, #14986 AUDUSD.
Méthode : #13305, #13306, #13415 (« si les probabilités dépassent 75 %, je regarde le fondamental »).

Données : bougies HORAIRES Yahoo Finance (déc. 2023 -> sept. 2026, data/prix/yahoo/), regroupées en
bougies journalières de 22h UTC à 22h UTC (clôture de New York). Les bougies journalières Yahoo du
Forex ne sont pas utilisables : l'ouverture est fausse (corps nul dans 30 % des cas) et les plus hauts
et plus bas sont trop étroits avant 2023.

Ce que fait le script :
1. reconstruit la configuration : bougie de sens opposé à la veille, dont le corps englobe celui de la
   veille (« corps ») ; variante stricte : elle englobe aussi les mèches de la veille (« range ») ;
2. mesure le taux de rupture à 3 jours et le jour de la rupture, à comparer aux cartes ;
3. mesure le même taux pour TOUTES les bougies de même couleur (le « hasard ») ;
4. transforme la rupture en trade, heure par heure : entrée à la clôture de l'englobante, objectif =
   extrême cassé de 1 pip, stop = l'autre extrême de la bougie, sortie au bout de 3 jours ; si
   objectif et stop tombent dans la même heure, on compte le stop ; spread déduit. Résultat en R
   et en fraction de l'ATR 14 jours ;
5. variante « + FVG » des cartes, avec trois définitions du fair value gap (voir analyser()) ; pour le
   FVG « suivant », connu seulement à la clôture du lendemain, on mesure aussi le trade pris à ce moment-là.

Sorties : data/flashcards_englobante.csv (paire x sens x configuration), data/flashcards_englobante_detail.csv
(une ligne par bougie, avec l'issue du trade et sa durée en heures) et tableau à l'écran.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402
from modele_meta import SPREAD  # noqa: E402

CARTES = {  # paire: (message, baissier %, haussier %)
    'USDJPY': (13327, 70.97, 77.85), 'EURNZD': (13340, 79.40, 73.53), 'USDCAD': (13343, 79.72, 83.40),
    'XAUUSD': (13355, 76.02, 71.88), 'GBPJPY': (13387, 74.7, 77.4), 'NZDUSD': (13395, 80.37, 82.46),
    'AUDJPY': (13409, 81.0, 74.9), 'EURUSD': (13804, 78.79, 75.19), 'GBPUSD': (13618, 76.80, 76.62),
    'AUDUSD': (14986, None, None),
}
HORIZON = 3


def pip(p):
    return 0.01 if p.endswith('JPY') else 0.1 if p == 'XAUUSD' else 0.0001


def journalier(hh):
    hh = hh.copy()
    hh['jour'] = (hh.date + pd.Timedelta(hours=2)).dt.floor('D')   # 22h UTC -> minuit
    g = hh.groupby('jour').agg(open=('open', 'first'), high=('high', 'max'), low=('low', 'min'),
                               close=('close', 'last'), n=('close', 'size')).reset_index()
    return g[(g.jour.dt.weekday < 5) & (g.n >= 12)].reset_index(drop=True)


def simuler(t, hh_h, hh_l, hh_c, s, entree, cible, stop, debut, fin):
    """Trade heure par heure entre debut et fin ; objectif et stop dans la même heure -> stop."""
    a, b = np.searchsorted(t, np.datetime64(debut)), np.searchsorted(t, np.datetime64(fin))
    duree = lambda j: (t[j] - np.datetime64(debut)) / np.timedelta64(1, 'h') + 1  # noqa: E731
    for j in range(a, b):
        if (hh_l[j] <= stop) if s > 0 else (hh_h[j] >= stop):
            return -abs(entree - stop), 'stop', duree(j)
        if (hh_h[j] >= cible) if s > 0 else (hh_l[j] <= cible):
            return abs(cible - entree), 'objectif', duree(j)
    return ((hh_c[b - 1] - entree) * s if b > a else 0.0), 'temps', np.nan


def analyser(p, hh):
    d = journalier(hh)
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    tr = np.maximum(h, np.r_[c[0], c[:-1]]) - np.minimum(l, np.r_[c[0], c[:-1]])
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    t = hh.date.to_numpy()
    hh_h, hh_l, hh_c = hh.high.to_numpy(), hh.low.to_numpy(), hh.close.to_numpy()
    pp, spread = pip(p), SPREAD.get(p, 2) * (0.01 if p == 'XAUUSD' else pip(p))
    fin_jour = lambda k: d.jour.iloc[k] + pd.Timedelta(hours=22)  # noqa: E731
    lignes = []
    for i in range(15, len(d) - HORIZON):
        s = np.sign(c[i] - o[i])
        if s == 0:
            continue
        corps = s == -np.sign(c[i - 1] - o[i - 1]) and abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1])
        rng = corps and h[i] >= h[i - 1] and l[i] <= l[i - 1]
        # FVG (fair value gap) dans le sens de la bougie, trois définitions :
        # - « suivant » : l'englobante est la bougie du milieu (bas du jour i+1 > haut du jour i-1 en
        #   haussier) ; n'est connu qu'à la clôture du jour i+1 ;
        # - « précédent » : l'englobante est la 3e bougie (bas du jour i > haut du jour i-2) ;
        # - « horaire » : un FVG de 3 bougies horaires d'au moins 5 % de l'ATR pendant la journée i.
        fvg_suiv = (l[i + 1] > h[i - 1]) if s > 0 else (h[i + 1] < l[i - 1])
        fvg_prec = (l[i] > h[i - 2]) if s > 0 else (h[i] < l[i - 2])
        a0, a1 = np.searchsorted(t, np.datetime64(fin_jour(i - 1))), np.searchsorted(t, np.datetime64(fin_jour(i)))
        gaps = (hh_l[a0 + 2:a1] - hh_h[a0:a1 - 2]) if s > 0 else (hh_l[a0:a1 - 2] - hh_h[a0 + 2:a1])
        fvg_h1 = bool(len(gaps)) and gaps.max() >= 0.05 * atr[i]
        cible = h[i] + pp if s > 0 else l[i] - pp
        stop = l[i] if s > 0 else h[i]
        touche = [(h[i + k] >= cible) if s > 0 else (l[i + k] <= cible) for k in range(1, HORIZON + 1)]
        jour = next((k + 1 for k, x in enumerate(touche) if x), None)
        res, issue, heures = simuler(t, hh_h, hh_l, hh_c, s, c[i], cible, stop, fin_jour(i), fin_jour(i + HORIZON))
        risque = abs(c[i] - stop)
        # variante FVG « suivant » tradable : entrée à la clôture du jour i+1, si l'extrême n'est pas
        # déjà cassé et si le stop n'a pas été touché ; même fenêtre de 3 jours
        res2, risque2 = np.nan, np.nan
        stop_touche = (l[i + 1] <= stop) if s > 0 else (h[i + 1] >= stop)
        if fvg_suiv and not touche[0] and not stop_touche:
            risque2 = abs(c[i + 1] - stop)
            res2 = simuler(t, hh_h, hh_l, hh_c, s, c[i + 1], cible, stop, fin_jour(i + 1), fin_jour(i + HORIZON))[0]
        lignes.append(dict(date=d.jour.iloc[i], sens=int(s), corps=int(corps), range=int(rng),
                           fvg_suivant=int(fvg_suiv), fvg_precedent=int(fvg_prec), fvg_horaire=int(fvg_h1),
                           rupture=int(jour is not None), jour=jour, issue=issue, heures=heures,
                           gain_r=(res - spread) / risque if risque > 0 else np.nan,
                           gain_atr=(res - spread) / atr[i], gagnant=int(res - spread > 0),
                           tradable_j2=int(not np.isnan(res2)),
                           rupture_j2=int(any(touche[1:])) if not np.isnan(res2) else np.nan,
                           gain_r_j2=(res2 - spread) / risque2 if risque2 and risque2 > 0 else np.nan,
                           gain_atr_j2=(res2 - spread) / atr[i] if not np.isnan(res2) else np.nan,
                           objectif_pips=abs(cible - c[i]) / pp, stop_pips=risque / pp))
    return pd.DataFrame(lignes)


CARTES_FVG = {'GBPJPY': (76.7, 74.5), 'AUDJPY': (81.7, 76.7), 'EURUSD': (81.6, 78.6)}  # baissier, haussier
CONFIGS = {
    'corps': lambda a: a.corps == 1,
    'range': lambda a: a.range == 1,
    'toutes': lambda a: a.corps >= 0,
    'corps+fvg_suivant': lambda a: (a.corps == 1) & (a.fvg_suivant == 1),
    'corps+fvg_precedent': lambda a: (a.corps == 1) & (a.fvg_precedent == 1),
    'corps+fvg_horaire': lambda a: (a.corps == 1) & (a.fvg_horaire == 1),
    'corps_sans_fvg_suivant': lambda a: (a.corps == 1) & (a.fvg_suivant == 0),
    'toutes+fvg_suivant': lambda a: a.fvg_suivant == 1,
}


def main():
    res, detail = [], []
    for p, (msg, cb, ch) in CARTES.items():
        hh = prix_yahoo._charger(p, '1h')
        a = analyser(p, hh)
        detail.append(a.assign(paire=p))
        print(f"  {p} : {len(a)} jours ({a.date.min().date()} -> {a.date.max().date()}), "
              f"{a.corps.sum()} englobantes", flush=True)
        for s, nom, carte in [(-1, 'baissier', cb), (1, 'haussier', ch)]:
            for conf, f in CONFIGS.items():
                x = a[(a.sens == s) & f(a)]
                fvg = CARTES_FVG.get(p, (None, None))[0 if s < 0 else 1] if 'fvg' in conf else None
                tj = x[x.tradable_j2 == 1]
                res.append(dict(paire=p, message=msg, sens=nom, configuration=conf,
                                carte_pct=fvg if 'fvg' in conf else carte, n=len(x),
                                rupture_3j_pct=round(x.rupture.mean() * 100, 1) if len(x) else np.nan,
                                rupture_jour1_pct=round((x.jour == 1).sum() / max(x.rupture.sum(), 1) * 100, 1),
                                trade_gagnant_pct=round(x.gagnant.mean() * 100, 1) if len(x) else np.nan,
                                gain_r=round(x.gain_r.mean(), 3), gain_atr=round(x.gain_atr.mean(), 3),
                                n_tradable_j2=len(tj), rupture_j2_pct=round(tj.rupture_j2.mean() * 100, 1) if len(tj) else np.nan,
                                gain_r_j2=round(tj.gain_r_j2.mean(), 3) if len(tj) else np.nan,
                                gain_atr_j2=round(tj.gain_atr_j2.mean(), 3) if len(tj) else np.nan,
                                objectif_median_pips=round(x.objectif_pips.median(), 1),
                                stop_median_pips=round(x.stop_pips.median(), 1)))
    df = pd.DataFrame(res)
    df.to_csv('data/flashcards_englobante.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    pd.set_option('display.max_rows', 100)
    cols = ['paire', 'sens', 'carte_pct', 'n', 'rupture_3j_pct', 'trade_gagnant_pct', 'gain_r']
    print(df[df.configuration == 'corps'][cols].to_string(index=False))
    print('\nVariante FVG (« suivant »), paires avec une carte FVG :')
    print(df[(df.configuration == 'corps+fvg_suivant') & df.paire.isin(CARTES_FVG)][cols].to_string(index=False))
    print('\nToutes paires confondues (moyenne pondérée) :')
    for conf in CONFIGS:
        x = df[(df.configuration == conf) & (df.n > 0)]
        w = x.n
        ligne = (f"  {conf:<24} n={w.sum():>5}  rupture {np.average(x.rupture_3j_pct, weights=w):5.1f} %  "
                 f"jour 1 {np.average(x.rupture_jour1_pct, weights=w):3.0f} %  "
                 f"gagnants {np.average(x.trade_gagnant_pct, weights=w):5.1f} %  "
                 f"gain {np.average(x.gain_r, weights=w):+.3f} R {np.average(x.gain_atr, weights=w):+.3f} ATR")
        y = x[x.n_tradable_j2 > 0]
        if 'fvg_suivant' in conf and len(y):
            ligne += (f"  | entrée au jour 2 : n={y.n_tradable_j2.sum()}, rupture "
                      f"{np.average(y.rupture_j2_pct, weights=y.n_tradable_j2):.1f} %, gain "
                      f"{np.average(y.gain_r_j2, weights=y.n_tradable_j2):+.3f} R "
                      f"{np.average(y.gain_atr_j2, weights=y.n_tradable_j2):+.3f} ATR")
        print(ligne)
    det = pd.concat(detail)
    det.to_csv('data/flashcards_englobante_detail.csv', index=False)
    e = det[det.corps == 1]
    for iss in ['objectif', 'stop']:
        x = e[e.issue == iss].heures
        print(f"\nDurée jusqu'à {iss} (englobantes, {len(x)} trades) : médiane {x.median():.0f} h, moyenne {x.mean():.1f} h, "
              f"moins de 5 h {(x <= 5).mean() * 100:.0f} %, moins de 24 h {(x <= 24).mean() * 100:.0f} %")
    print(f"Issues : {e.issue.value_counts(normalize=True).round(3).to_dict()}")
    cartes = df[(df.configuration == 'corps') & df.carte_pct.notna()]
    print(f"\nCartes : moyenne annoncée {cartes.carte_pct.mean():.1f} %, mesurée {cartes.rupture_3j_pct.mean():.1f} %")


if __name__ == '__main__':
    main()
