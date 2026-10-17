#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Contexte de marché partagé par les fiches mensuelles et l'analyse « quand ne pas entrer » :
- force des devises (8 devises contre leur moyenne) : FRED H.10 jusqu'à fin 2023, puis clôtures journalières (UTC)
  reconstruites depuis l'horaire Yahoo des paires en dollar ;
- taux directeurs (BIS), positionnement COT (gérants d'actifs), calendrier économique (TradingView), VIX et taux
  américains (FRED).
"""
import os

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEVISES = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF']
FRED_PAYS = {'Euro': 'EUR', 'United Kingdom': 'GBP', 'Japan': 'JPY', 'Australia': 'AUD', 'New Zealand': 'NZD',
             'Canada': 'CAD', 'Switzerland': 'CHF'}
YAHOO = {'EUR': ('EURUSD', 1), 'GBP': ('GBPUSD', 1), 'AUD': ('AUDUSD', 1), 'NZD': ('NZDUSD', 1),
         'JPY': ('USDJPY', -1), 'CAD': ('USDCAD', -1), 'CHF': ('USDCHF', -1)}
LIEN = 'https://t.me/Thehalalwayamirou/{}'


def chemin(p):
    return os.path.join(RACINE, p)


def valeurs_usd():
    """log de la valeur en dollars de chaque devise, une ligne par jour de bourse."""
    f = pd.read_csv(chemin('data/prix/fx_daily_fred.csv'), parse_dates=['Date'])
    f = f[f['Country'].isin(FRED_PAYS)]
    f['devise'] = f['Country'].map(FRED_PAYS)
    fred = -np.log(f.pivot_table(index='Date', columns='devise', values='Exchange rate'))   # devise par dollar
    fred = fred[fred.index < '2024-01-01']
    cols = {}
    for c, (p, s) in YAHOO.items():
        h = pd.read_csv(chemin(f'data/prix/yahoo/{p}_1h.csv'), parse_dates=['date'])
        h = h[h['date'].dt.weekday < 5]
        cl = h.groupby(h['date'].dt.normalize())['close'].last()
        cols[c] = s * np.log(cl)
    yah = pd.DataFrame(cols)
    yah = yah[yah.index >= '2024-01-01']
    v = pd.concat([fred, yah]).sort_index().ffill().dropna()
    v['USD'] = 0.0
    return v[DEVISES]


def force(v, debut, fin):
    """Variation de chaque devise contre la moyenne des 8, en %, entre deux dates (clôtures)."""
    a = v[v.index <= debut]
    b = v[v.index <= fin]
    if not len(a) or not len(b):
        return None
    d = b.iloc[-1] - a.iloc[-1]
    return (d - d.mean()) * 100


def taux():
    t = pd.read_csv(chemin('data/fondamental/taux.csv'), parse_dates=['date'])
    return t.pivot_table(index='date', columns='devise', values='taux_directeur').sort_index().ffill()


def cot():
    c = pd.read_csv(chemin('data/fondamental/cot.csv'), parse_dates=['reference'])
    return c.pivot_table(index='reference', columns='devise', values='gerants_net').sort_index()


def calendrier():
    c = pd.read_csv(chemin('data/fondamental/calendrier.csv'))
    c['date'] = pd.to_datetime(c['date'].str[:19])
    return c


def macro_us():
    f = {k: pd.read_csv(chemin(f'data/prix/fred_macro/{k}.csv'), parse_dates=['observation_date'], na_values='.')
         .set_index('observation_date')[k] for k in ['DGS10', 'DGS2', 'VIXCLS']}
    return pd.DataFrame(f).ffill()
