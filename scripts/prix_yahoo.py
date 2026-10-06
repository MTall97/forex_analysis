#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bougies de prix depuis Yahoo Finance (yfinance), avec cache local dans data/prix/yahoo/.

- horaire (1h) : disponible sur les ~730 derniers jours seulement (depuis mi-décembre 2023) ;
- journalier (1d) : depuis 2021.
bougies(paire, debut, fin) renvoie des tuples (datetime UTC naïf, ouverture, haut, bas, clôture)
en horaire quand c'est possible, sinon en journalier ; resolution(paire, date) indique laquelle.

Usage direct (pré-remplir le cache) :
    python scripts/prix_yahoo.py EURUSD GBPUSD ...
Compléter le cache horaire avec les derniers jours (Yahoo ne garde que 730 jours) :
    python scripts/prix_yahoo.py --mettre-a-jour [EURUSD GBPUSD ...]   (toutes les paires en cache par défaut)
"""

import os
import sys
from datetime import datetime

import pandas as pd

CACHE = 'data/prix/yahoo'
SYMBOLES = {'XAUUSD': 'GC=F', 'XAGUSD': 'SI=F', 'US30': '^DJI'}
_memo = {}


def symbole(paire):
    return SYMBOLES.get(paire, f"{paire}=X")


def _charger(paire, intervalle):
    cle = (paire, intervalle)
    if cle in _memo:
        return _memo[cle]
    f = f"{CACHE}/{paire}_{intervalle}.csv"
    if os.path.exists(f):
        df = pd.read_csv(f, parse_dates=['date'])
    else:
        import yfinance as yf
        if intervalle == '1h':
            d = yf.download(symbole(paire), period='730d', interval='1h', progress=False, auto_adjust=False)
        else:
            d = yf.download(symbole(paire), start='2020-06-01', interval='1d', progress=False, auto_adjust=False)
        if isinstance(d.columns, pd.MultiIndex):
            d.columns = d.columns.get_level_values(0)
        idx = d.index.tz_convert('UTC').tz_localize(None) if d.index.tz is not None else d.index
        df = pd.DataFrame({'date': idx, 'open': d['Open'].values, 'high': d['High'].values,
                           'low': d['Low'].values, 'close': d['Close'].values}).dropna()
        os.makedirs(CACHE, exist_ok=True)
        df.to_csv(f, index=False)
    _memo[cle] = df
    return df


def debut_horaire(paire):
    df = _charger(paire, '1h')
    return df['date'].min() if len(df) else datetime.max


def resolution(paire, date):
    return '1h' if date >= debut_horaire(paire) else '1d'


def bougies(paire, debut, fin):
    """Bougies horaires si la période est couverte, sinon journalières."""
    h0 = debut_horaire(paire)
    out = []
    if debut < h0:
        d = _charger(paire, '1d')
        d = d[(d['date'] >= pd.Timestamp(debut.date())) & (d['date'] <= min(fin, h0))]
        out += [(r.date.to_pydatetime(), r.open, r.high, r.low, r.close) for r in d.itertuples()]
    if fin >= h0:
        h = _charger(paire, '1h')
        h = h[(h['date'] >= max(debut, h0)) & (h['date'] <= fin)]
        out += [(r.date.to_pydatetime(), r.open, r.high, r.low, r.close) for r in h.itertuples()]
    return out


def mettre_a_jour(paire):
    """Ajoute au cache horaire les bougies des 60 derniers jours (sans toucher à l'historique)."""
    import yfinance as yf
    f = f"{CACHE}/{paire}_1h.csv"
    ancien = pd.read_csv(f, parse_dates=['date']) if os.path.exists(f) else pd.DataFrame(
        columns=['date', 'open', 'high', 'low', 'close'])
    d = yf.download(symbole(paire), period='60d', interval='1h', progress=False, auto_adjust=False)
    if d is None or d.empty:
        return 0
    if isinstance(d.columns, pd.MultiIndex):
        d.columns = d.columns.get_level_values(0)
    idx = d.index.tz_convert('UTC').tz_localize(None) if d.index.tz is not None else d.index
    neuf = pd.DataFrame({'date': idx, 'open': d['Open'].values, 'high': d['High'].values,
                         'low': d['Low'].values, 'close': d['Close'].values}).dropna()
    # la dernière bougie horaire de l'ancien cache pouvait être incomplète : on garde la nouvelle version
    tout = pd.concat([ancien, neuf]).drop_duplicates('date', keep='last').sort_values('date')
    tout.to_csv(f, index=False)
    _memo.pop((paire, '1h'), None)
    return len(tout) - len(ancien)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args and args[0] == '--mettre-a-jour':
        paires = args[1:] or sorted(n[:-7] for n in os.listdir(CACHE) if n.endswith('_1h.csv'))
        for p in paires:
            try:
                print(p, '+', mettre_a_jour(p), 'bougies horaires')
            except Exception as ex:
                print(p, 'échec :', ex)
    else:
        for p in args:
            print(p, len(_charger(p, '1d')), len(_charger(p, '1h')))
