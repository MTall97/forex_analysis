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
   et en fraction de l'ATR 14 jours.

Sortie : data/flashcards_englobante.csv (paire x sens x configuration) et tableau à l'écran.
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


def analyser(p, hh):
    d = journalier(hh)
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    tr = np.maximum(h, np.r_[c[0], c[:-1]]) - np.minimum(l, np.r_[c[0], c[:-1]])
    atr = pd.Series(tr).rolling(14).mean().to_numpy()
    t = hh.date.to_numpy()
    hh_h, hh_l, hh_c = hh.high.to_numpy(), hh.low.to_numpy(), hh.close.to_numpy()
    pp, spread = pip(p), SPREAD.get(p, 2) * (0.01 if p == 'XAUUSD' else pip(p))
    lignes = []
    for i in range(15, len(d) - HORIZON):
        s = np.sign(c[i] - o[i])
        if s == 0:
            continue
        corps = s == -np.sign(c[i - 1] - o[i - 1]) and abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1])
        rng = corps and h[i] >= h[i - 1] and l[i] <= l[i - 1]
        cible = h[i] + pp if s > 0 else l[i] - pp
        stop = l[i] if s > 0 else h[i]
        futur = slice(i + 1, i + 1 + HORIZON)
        rupt = (h[futur].max() >= cible) if s > 0 else (l[futur].min() <= cible)
        jour = next((k for k in range(1, HORIZON + 1) if (h[i + k] >= cible if s > 0 else l[i + k] <= cible)), None)
        # trade heure par heure, de la clôture de la bougie i à la clôture du jour i+3
        debut = d.jour.iloc[i] + pd.Timedelta(hours=22)
        fin = d.jour.iloc[i + HORIZON] + pd.Timedelta(hours=22)
        a, b = np.searchsorted(t, np.datetime64(debut)), np.searchsorted(t, np.datetime64(fin))
        res = None
        for j in range(a, b):
            touche_s = hh_l[j] <= stop if s > 0 else hh_h[j] >= stop
            touche_c = hh_h[j] >= cible if s > 0 else hh_l[j] <= cible
            if touche_s:
                res = -abs(c[i] - stop)
                break
            if touche_c:
                res = abs(cible - c[i])
                break
        if res is None:
            res = (hh_c[b - 1] - c[i]) * s if b > a else 0.0
        risque = abs(c[i] - stop)
        lignes.append(dict(date=d.jour.iloc[i], sens=int(s), corps=int(corps), range=int(rng), rupture=int(rupt),
                           jour=jour, gain_r=(res - spread) / risque if risque > 0 else np.nan,
                           gain_atr=(res - spread) / atr[i], gagnant=int(res - spread > 0),
                           objectif_pips=abs(cible - c[i]) / pp, stop_pips=risque / pp))
    return pd.DataFrame(lignes)


def main():
    res = []
    for p, (msg, cb, ch) in CARTES.items():
        hh = prix_yahoo._charger(p, '1h')
        a = analyser(p, hh)
        print(f"  {p} : {len(a)} jours ({a.date.min().date()} -> {a.date.max().date()}), "
              f"{a.corps.sum()} englobantes", flush=True)
        for s, nom, carte in [(-1, 'baissier', cb), (1, 'haussier', ch)]:
            for conf in ['corps', 'range', 'toutes']:
                x = a[(a.sens == s) & ((a[conf] == 1) if conf != 'toutes' else True)]
                res.append(dict(paire=p, message=msg, sens=nom, configuration=conf, carte_pct=carte, n=len(x),
                                rupture_3j_pct=round(x.rupture.mean() * 100, 1),
                                rupture_jour1_pct=round((x.jour == 1).sum() / max(x.rupture.sum(), 1) * 100, 1),
                                trade_gagnant_pct=round(x.gagnant.mean() * 100, 1),
                                gain_r=round(x.gain_r.mean(), 3), gain_atr=round(x.gain_atr.mean(), 3),
                                objectif_median_pips=round(x.objectif_pips.median(), 1),
                                stop_median_pips=round(x.stop_pips.median(), 1)))
    df = pd.DataFrame(res)
    df.to_csv('data/flashcards_englobante.csv', index=False)
    pd.set_option('display.width', 250)
    pd.set_option('display.max_columns', 30)
    pd.set_option('display.max_rows', 100)
    print(df[df.configuration == 'corps'].drop(columns=['configuration']).to_string(index=False))
    print('\nToutes paires confondues (moyenne pondérée) :')
    for conf in ['corps', 'range', 'toutes']:
        x = df[df.configuration == conf]
        w = x.n
        print(f"  {conf:<7} n={w.sum():>5}  rupture {np.average(x.rupture_3j_pct, weights=w):.1f} %  "
              f"rupture jour 1 {np.average(x.rupture_jour1_pct, weights=w):.0f} %  "
              f"trades gagnants {np.average(x.trade_gagnant_pct, weights=w):.1f} %  "
              f"gain {np.average(x.gain_r, weights=w):+.3f} R  {np.average(x.gain_atr, weights=w):+.3f} ATR")
    cartes = df[(df.configuration == 'corps') & df.carte_pct.notna()]
    print(f"\nCartes : moyenne annoncée {cartes.carte_pct.mean():.1f} %, mesurée {cartes.rupture_3j_pct.mean():.1f} %")


if __name__ == '__main__':
    main()
