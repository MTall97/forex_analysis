#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste deux stratégies documentées dans la littérature sur le Forex, sur 8 devises du G10
(USD, EUR, GBP, JPY, AUD, NZD, CAD, CHF), de 1999 à 2026, en données mensuelles :

1. CARRY : chaque fin de mois, on achète les 3 devises au taux directeur le plus élevé et on vend les 3
   au taux le plus bas (poids égaux). Le rendement comprend la variation de change ET le différentiel
   de taux encaissé (taux / 12 par mois).
2. MOMENTUM :
   - « de tendance » (time-series momentum, Moskowitz, Ooi et Pedersen, 2012) : pour chacune des 7
     devises contre le dollar, position dans le sens de son rendement des L derniers mois (L = 1, 3, 6, 12) ;
   - « transversal » : achat des 3 devises qui ont le plus monté sur 3 mois, vente des 3 qui ont le moins monté.
3. COMBINAISON : moitié carry, moitié momentum de tendance à 12 mois.

Coûts : 0,03 % par unité de position changée à chaque rééquilibrage (spread des courtiers sur les majeures).
Validation : résultats par sous-période (1999-2009, 2010-2019, 2020-2026) ; aucun paramètre n'est optimisé,
les valeurs (3 devises, 1-3-6-12 mois) sont celles de la littérature.

Données :
- cours quotidiens de la Fed (H.10) via github.com/datasets/exchange-rates (unités de devise pour 1 USD),
  mis en cache dans data/prix/fx_daily_fred_1999.csv ;
- taux directeurs quotidiens de la BIS (WS_CBPOL), cache data/prix/taux_directeurs_1999.csv.

Sorties : data/carry_momentum_mensuel.csv (rendements mensuels de chaque stratégie), résumé écran.
"""

import io
import os
import urllib.request

import numpy as np
import pandas as pd

FX = 'data/prix/fx_daily_fred_1999.csv'
TAUX = 'data/prix/taux_directeurs_1999.csv'
PAYS = {'Euro': 'EUR', 'United Kingdom': 'GBP', 'Japan': 'JPY', 'Australia': 'AUD', 'New Zealand': 'NZD',
        'Canada': 'CAD', 'Switzerland': 'CHF'}
BIS = {'US': 'USD', 'XM': 'EUR', 'GB': 'GBP', 'JP': 'JPY', 'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}
COUT = 0.0003


def lire(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read().decode('utf-8')


def donnees():
    if not os.path.exists(FX):
        d = pd.read_csv(io.StringIO(lire('https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv')))
        d = d[d.Country.isin(PAYS) & (d.Date >= '1999-01-01')]
        d.to_csv(FX, index=False)
    if not os.path.exists(TAUX):
        lignes = []
        for code, dev in BIS.items():
            t = pd.read_csv(io.StringIO(lire(f'https://stats.bis.org/api/v1/data/WS_CBPOL/D.{code}/all?startPeriod=1999-01-01&format=csv')))
            lignes.append(pd.DataFrame({'date': t.TIME_PERIOD, 'devise': dev, 'taux': t.OBS_VALUE}))
        pd.concat(lignes).dropna().to_csv(TAUX, index=False)
    fx = pd.read_csv(FX, parse_dates=['Date'])
    fx['dev'] = fx.Country.map(PAYS)
    s = fx.pivot_table(index='Date', columns='dev', values='Exchange rate').ffill()
    s = s.resample('ME').last()                                   # unités de devise pour 1 USD, fin de mois
    tx = pd.read_csv(TAUX, parse_dates=['date']).pivot_table(index='date', columns='devise', values='taux')
    tx = tx.ffill().resample('ME').last().reindex(s.index).ffill()
    return s, tx


def stats(r):
    r = r.dropna()
    if len(r) < 12:
        return {}
    eq = (1 + r).cumprod()
    return {'rendement_annuel_pct': round(((eq.iloc[-1]) ** (12 / len(r)) - 1) * 100, 2),
            'volatilite_pct': round(r.std() * np.sqrt(12) * 100, 1),
            'sharpe': round(r.mean() / r.std() * np.sqrt(12), 2),
            't_stat': round(r.mean() / r.std() * np.sqrt(len(r)), 2),
            'pire_baisse_pct': round(((eq / eq.cummax()) - 1).min() * 100, 1),
            'mois_positifs_pct': round((r > 0).mean() * 100, 0), 'mois': int(len(r))}


def main():
    s, tx = donnees()
    devs = list(s.columns)                                        # 7 devises hors USD
    # rendement excédentaire d'une position longue devise / courte USD sur le mois suivant
    fxr = np.log(s / s.shift(-1))                                 # la devise s'apprécie quand S baisse
    portage = (tx[devs].sub(tx['USD'], axis=0)) / 100 / 12
    xr = (fxr + portage).iloc[:-1]                                # mois t -> t+1, connu à la fin du mois t+1
    xr_all = xr.copy()
    xr_all['USD'] = 0.0
    taux_all = tx[devs + ['USD']]

    def portefeuille(poids):
        brut = (poids.shift(0) * xr_all.reindex(poids.index)[poids.columns]).sum(axis=1)
        rotation = poids.diff().abs().sum(axis=1).fillna(poids.abs().sum(axis=1))
        return brut - COUT * rotation

    # 1. carry
    rang = taux_all.loc[xr.index].rank(axis=1, method='first')
    w_carry = ((rang >= 6).astype(float) / 3 - (rang <= 3).astype(float) / 3)
    res = {'carry (3 contre 3)': portefeuille(w_carry)}
    # 2a. momentum de tendance
    cum = np.log(s / s.shift(1)).mul(-1)                          # rendement change de la devise, mois t-1 -> t
    for L in (1, 3, 6, 12):
        sig = np.sign(cum.rolling(L).sum()).loc[xr.index]
        res[f'momentum tendance {L} mois'] = portefeuille(sig / len(devs))
    # 2b. momentum transversal
    perf3 = cum.rolling(3).sum().loc[xr.index].copy()
    perf3['USD'] = 0.0
    r3 = perf3.rank(axis=1, method='first')
    res['momentum transversal 3 mois'] = portefeuille((r3 >= 6).astype(float) / 3 - (r3 <= 3).astype(float) / 3)
    # 3. combinaison
    res['carry + momentum 12 mois'] = 0.5 * res['carry (3 contre 3)'] + 0.5 * res['momentum tendance 12 mois']

    df = pd.DataFrame(res).iloc[12:]                              # 12 mois d'historique pour le momentum
    df.index.name = 'mois'
    df.to_csv('data/carry_momentum_mensuel.csv')
    pd.set_option('display.width', 220)
    for nom in df.columns:
        print(f"\n{nom}")
        print(f"  {'2000-2026':<10} {stats(df[nom])}")
        for a, b in [(2000, 2009), (2010, 2019), (2020, 2026)]:
            print(f"  {a}-{b}  {stats(df[nom][(df.index.year >= a) & (df.index.year <= b)])}")
    print('\nCorrélation des stratégies :')
    print(df.corr().round(2).to_string())


if __name__ == '__main__':
    main()
