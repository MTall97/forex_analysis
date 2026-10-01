#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rendements mensuels réels et biais saisonniers des paires tradées dans le canal.

Sources (téléchargeables sans Yahoo Finance) :
    data/prix/fx_daily_fred.csv  cours quotidiens Fed H.10 (unités de devise par USD),
                                 https://github.com/datasets/exchange-rates (data/daily.csv)
    data/prix/gold_monthly.csv   or, moyenne mensuelle, https://github.com/datasets/gold-prices

Sorties :
    data/rendements_mensuels.csv  paire, mois (AAAA-MM), clôture, rendement (%)
    data/saisonnalite.csv         paire, mois (1-12), période, nb années, % mois haussiers,
                                  rendement moyen (%), biais (haussier / baissier / neutre)

Deux périodes : « projet » = 2020-2025 (celle des PDF de rapports_pdf/) et « long » = 2010-2025.
Biais : haussier si ≥ 2/3 des années positives ET moyenne > 0 ; baissier si ≤ 1/3 ET moyenne < 0 ;
sinon neutre. Pour l'or, la série est une moyenne mensuelle (rendements lissés).

Usage :
    python scripts/saisonnalite_mensuelle.py
"""

import csv
from collections import defaultdict
from statistics import mean

DEVISES = {'Euro': 'EUR', 'United Kingdom': 'GBP', 'Japan': 'JPY', 'Australia': 'AUD',
           'New Zealand': 'NZD', 'Canada': 'CAD', 'Switzerland': 'CHF'}
ORDRE = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CAD', 'CHF', 'JPY']  # hiérarchie des cotations
PERIODES = {'projet': (2020, 2025), 'long': (2010, 2025)}


def charger_usd():
    """Cours quotidiens : unités de chaque devise pour 1 USD (USD = 1)."""
    jours = defaultdict(dict)
    with open('data/prix/fx_daily_fred.csv', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['Country'] in DEVISES:
                jours[r['Date']][DEVISES[r['Country']]] = float(r['Exchange rate'])
    return jours


def clotures_mensuelles(jours):
    """Dernier fixing complet de chaque mois, pour chaque paire de la hiérarchie."""
    paires = [a + b for i, a in enumerate(ORDRE) for b in ORDRE[i + 1:]]
    fin_mois = {}
    for d in sorted(jours):
        if len(jours[d]) == 7:
            fin_mois[d[:7]] = jours[d]
    out = defaultdict(dict)
    for mois, u in fin_mois.items():
        u = dict(u, USD=1.0)
        for p in paires:
            out[p][mois] = u[p[3:]] / u[p[:3]]   # prix de la base exprimé en devise de cotation
    with open('data/prix/gold_monthly.csv', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['Date'] >= '2009-01':
                out['XAUUSD'][r['Date']] = float(r['Price'])
    return out


def main():
    clot = clotures_mensuelles(charger_usd())
    rend = defaultdict(dict)
    with open('data/rendements_mensuels.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['paire', 'mois', 'cloture', 'rendement_pct'])
        for p, serie in sorted(clot.items()):
            mois = sorted(serie)
            for a, b in zip(mois, mois[1:]):
                r = (serie[b] / serie[a] - 1) * 100
                rend[p][b] = r
                w.writerow([p, b, f"{serie[b]:.5f}", f"{r:.3f}"])

    with open('data/saisonnalite.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['paire', 'mois', 'periode', 'annees', 'pct_haussier', 'moyenne_pct', 'biais'])
        for p in sorted(rend):
            for m in range(1, 13):
                for nom, (a, b) in PERIODES.items():
                    vals = [rend[p][f"{y}-{m:02d}"] for y in range(a, b + 1) if f"{y}-{m:02d}" in rend[p]]
                    if not vals:
                        continue
                    pos = sum(v > 0 for v in vals) / len(vals)
                    moy = mean(vals)
                    biais = 'haussier' if pos >= 2 / 3 and moy > 0 else 'baissier' if pos <= 1 / 3 and moy < 0 else 'neutre'
                    w.writerow([p, m, nom, len(vals), f"{pos * 100:.1f}", f"{moy:.3f}", biais])
    print(f"{len(rend)} séries -> data/rendements_mensuels.csv, data/saisonnalite.csv")


if __name__ == '__main__':
    main()
