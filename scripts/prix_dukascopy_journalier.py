#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Télécharge les bougies JOURNALIÈRES Dukascopy (BID) de 2010 à aujourd'hui pour les paires étudiées
et les écrit dans data/prix/journalier_dukascopy.csv (paire, date, open, high, low, close).

Pourquoi : les bougies journalières Yahoo du Forex sont fausses (ouverture = clôture dans 30 % des
cas, plus hauts et plus bas trop étroits avant 2023), et l'horaire Yahoo ne remonte qu'à fin 2023.
Dukascopy fournit un fichier par paire et par année ; le serveur limite le débit, d'où les pauses
(scripts/simuler_trades_dukascopy.py:telecharger). Les fichiers bruts restent dans
data/prix/dukascopy/ (non suivi par Git) : le script est relançable.

Remarque : chez Dukascopy, une bougie journalière va de 00h à 24h UTC (et non de 22h à 22h comme
chez la plupart des courtiers). L'écart est de 2 heures sur 24. La courte bougie du dimanche soir est
fusionnée avec celle du lundi.

Usage : python scripts/prix_dukascopy_journalier.py [--debut 2010] [--paires EURUSD GBPUSD ...]
"""

import argparse
import csv
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from simuler_trades_dukascopy import BASE, CACHE, decoder, telecharger  # noqa: E402

PAIRES = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'EURJPY', 'GBPJPY', 'AUDJPY',
          'EURGBP', 'EURAUD', 'EURNZD', 'GBPAUD', 'AUDNZD', 'XAUUSD']
SORTIE = 'data/prix/journalier_dukascopy.csv'


def charger(paires=None):
    """Bougies journalières (DataFrame paire, date, open, high, low, close), depuis le CSV produit par ce script."""
    import pandas as pd
    d = pd.read_csv(SORTIE, parse_dates=['date'])
    return d[d.paire.isin(paires)] if paires else d


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--debut', type=int, default=2010)
    a.add_argument('--paires', nargs='*', default=PAIRES)
    a.add_argument('--sortie', default=SORTIE)
    args = a.parse_args()
    lignes = []
    for p in args.paires:
        n = 0
        for an in range(args.debut, datetime.utcnow().year + 1):
            data = telecharger(f"{BASE}/{p}/{an}/BID_candles_day_1.bi5", f"{CACHE}/{p}/{an}_d1.bi5")
            dimanche = None
            for t, o, h, l, c in decoder(data, datetime(an, 1, 1), p):
                if t.weekday() == 6:              # quelques heures du dimanche soir : rattachées au lundi
                    dimanche = (o, h, l)
                    continue
                if t.weekday() == 5:
                    continue
                if dimanche and t.weekday() == 0:
                    o, h, l = dimanche[0], max(h, dimanche[1]), min(l, dimanche[2])
                dimanche = None
                lignes.append([p, t.strftime('%Y-%m-%d'), round(o, 6), round(h, 6), round(l, 6), round(c, 6)])
                n += 1
        print(f"  {p} : {n} jours", flush=True)
    lignes.sort()
    with open(args.sortie, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['paire', 'date', 'open', 'high', 'low', 'close'])
        w.writerows(lignes)
    print(f"{len(lignes)} bougies -> {args.sortie}")


if __name__ == '__main__':
    main()
