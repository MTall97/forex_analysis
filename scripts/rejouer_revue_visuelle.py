#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rejoue sur les cours les trades d'Amirou trouvés par la revue visuelle des captures
(data/revue_visuelle_captures.csv, 2 240 images que l'OCR n'avait pas exploitées).

1. Garde les lignes « trade » ou « resultat » avec paire, sens, entrée, stop et objectif lisibles,
   hors captures de membres ou de tiers (note contenant « membre », « tiers », « élève »).
2. Écarte les positions déjà rejouées dans data/trades_simules.csv (même paire, entrée et stop à
   0,05 % près, à moins de 10 jours), et les doublons internes.
3. Écrit data/revue_trades_amirou.csv au format de data/captures_trades.csv, puis lance
   scripts/simuler_trades_dukascopy.py (mêmes règles : après coup, non déclenché, stop prioritaire
   dans une bougie ambiguë) -> data/revue_trades_simules.csv.
4. Affiche le bilan par année.

Usage : python scripts/rejouer_revue_visuelle.py
"""
import csv
import os
import subprocess
import sys
from datetime import datetime

import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)

d = pd.read_csv('data/revue_visuelle_captures.csv')
d['note'] = d['note'].fillna('')
tiers = d['note'].str.contains(r'membre|tiers|élève|lilight', case=False)
complet = d[['paire', 'sens', 'entree', 'stop', 'objectif']].notna().all(axis=1)
t = d[d['categorie'].isin(['trade', 'resultat']) & complet & ~tiers].copy()

deja = pd.read_csv('data/trades_simules.csv')
deja['date'] = pd.to_datetime(deja['date_publication'])


def connu(r):
    e, sl, jour = float(r['entree']), float(r['stop']), datetime.fromisoformat(r['date'])
    m = deja[(deja['paire'] == r['paire'])]
    return bool(((abs(m['entree'] - e) / e < 5e-4) & (abs(m['stop'] - sl) / e < 5e-4)
                 & ((m['date'] - jour).abs().dt.days <= 10)).any())


t = t[~t.apply(connu, axis=1)]
with open('data/revue_trades_amirou.csv', 'w', newline='', encoding='utf-8') as fh:
    w = csv.writer(fh)
    w.writerow(['fichier', 'id_message', 'date_message', 'paire', 'unite_temps', 'publication_utc',
                'entree', 'stop', 'objectif', 'sens'])
    for _, r in t.iterrows():
        w.writerow([r['fichier'], r['id_message'], r['date'], r['paire'], r['unite'], '',
                    r['entree'], r['stop'], r['objectif'], r['sens']])
print(f"{len(t)} lignes candidates -> data/revue_trades_amirou.csv")

env = dict(os.environ, ENTREE_TRADES='data/revue_trades_amirou.csv', SORTIE_TRADES='data/revue_trades_simules.csv')
subprocess.run([sys.executable, 'scripts/simuler_trades_dukascopy.py'], check=True, env=env)

s = pd.read_csv('data/revue_trades_simules.csv')
s['annee'] = s['date_publication'].str[:4]
s['r'] = pd.to_numeric(s['resultat_r'], errors='coerce')
print(pd.crosstab(s['annee'], s['issue'], margins=True).to_string())
cop = s[(s['statut'] == 'annoncé') & s['issue'].isin(['objectif', 'stop', 'ouvert après 20 jours'])]
print(cop.groupby('annee')['r'].agg(['count', 'mean', 'sum']).round(2).to_string())
print('copiables :', len(cop), 'R moyen', round(cop['r'].mean(), 3))
