#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La méthode de « retournement » d'Amirou, telle qu'il la décrit dans le canal, testée sur les cours.

Ce qu'il écrit :
- « attendez la formation d'un candle de retournement de situation telle qu'un engulfing candle ou un inside bar
  candle inverse avant de prendre position » (#1187), « ne prenez jamais position sans la confirmation d'une bougie
  de retournement de situation » (#1366) ;
- l'entrée se fait dans une « zone de retournement », de liquidité, de support ou de résistance (#939, #1144, #1173) ;
- « ces genres de mouvement sont appelés des mouvements climatiques […] en général on s'attend à un renversement de
  tendance après des mouvements comme ça » (#15227).

Règles (achat ; vente symétrique, prix inversés), fixées avant le test :
- bougie de retournement (bougie i) : « englobante » (haussière, la précédente baissière, corps >= corps précédent)
  ou « pin bar » (mèche basse >= 2/3 de la bougie, clôture dans le tiers haut) ;
- « zone » : le plus bas de la bougie i touche, à 0,25 ATR près, le plus bas des 60 bougies précédentes (en excluant
  les 5 dernières) : un support déjà testé ;
- « mouvement climatique » : le plus haut des 5 bougies précédentes est au moins 3 ATR au-dessus du plus bas de i ;
- entrée à la clôture de i ; stop 2 pips sous le plus bas de i ; objectif 2 R (et 3 R) ; sortie au plus tard après
  5 bougies (journalier) ou 30 bougies de 4 h ; si une même bougie touche le stop et l'objectif, le stop compte ;
  spread déduit ; risque d'au moins 5 pips.
Groupes : zone + bougie de retournement ; mouvement climatique + bougie ; témoins : la bougie seule (n'importe où),
et la zone seule (entrée à la clôture de toute bougie qui touche la zone, sans bougie de retournement).
Rejeux : journalier Dukascopy, 10 paires, 2012-2026 ; 4 h (reconstruit depuis l'horaire Yahoo), 22 paires, 2024-2026.
Sortie : data/retournement/{journalier,h4}.csv.gz, resultats.csv
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO, charger  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

SORTIE = 'data/retournement'
OBJECTIFS = (2, 3)


def atr(H, L, C, n=14):
    pc = np.r_[np.nan, C[:-1]]
    tr = np.nanmax(np.vstack([H - L, abs(H - pc), abs(L - pc)]), axis=0)
    return pd.Series(tr).rolling(n).mean().shift(1).to_numpy()


def scanner(dates, O, H, L, C, p, tenue):
    """Repère achat (pour les ventes, appeler avec des prix inversés). Une ligne par signal et par objectif."""
    pp, sp = pip(p), spread(p)
    A = atr(H, L, C)
    lignes = []
    for i in range(66, len(C)):
        a = A[i]
        if np.isnan(a) or a <= 0:
            continue
        rng = H[i] - L[i]
        corps, corps_prec = C[i] - O[i], O[i - 1] - C[i - 1]
        englobante = corps > 0 and corps_prec > 0 and corps >= corps_prec
        pin = rng > 0 and (min(O[i], C[i]) - L[i]) >= 2 / 3 * rng and C[i] >= L[i] + 2 / 3 * rng
        support = L[i - 60:i - 5].min()
        zone = abs(L[i] - support) <= 0.25 * a
        climat = H[i - 5:i].max() - L[i] >= 3 * a
        if not (englobante or pin or zone):
            continue
        e = C[i]
        sl = L[i] - 2 * pp
        R = e - sl
        if R < 5 * pp:
            continue
        for k in OBJECTIFS:
            tp = e + k * R
            r = None
            fin = min(i + tenue, len(C) - 1)
            if i + tenue > len(C) - 1:
                continue
            for j in range(i + 1, fin + 1):
                if L[j] <= sl:
                    r = -1.0
                    break
                if H[j] >= tp:
                    r = float(k)
                    break
            if r is None:
                r = (C[fin] - e) / R
            lignes.append(dict(paire=p, date=dates[i], englobante=englobante, pin_bar=pin, zone=zone, climat=climat,
                               objectif=k, risque_pips=round(R / pp, 1), risque_atr=round(R / a, 2),
                               r=round(r - sp / R, 4)))
    return lignes


def rejouer(nom, series, tenue):
    lignes = []
    for p, d in series:
        o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
        dates = d['date'].astype(str).to_numpy()
        for s, (O, H, L, C) in [(1, (o, h, l, c)), (-1, (-o, -l, -h, -c))]:
            for x in scanner(dates, O, H, L, C, p, tenue):
                x.update(rejeu=nom, sens='achat' if s > 0 else 'vente')
                lignes.append(x)
    return pd.DataFrame(lignes)


def series_h4():
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h = charger(p)
        h['bloc'] = h['date'].dt.floor('4h')
        g = h.groupby('bloc')
        d = pd.DataFrame({'date': list(g.groups), 'open': g['open'].first().to_numpy(), 'high': g['high'].max().to_numpy(),
                          'low': g['low'].min().to_numpy(), 'close': g['close'].last().to_numpy(), 'n': g.size().to_numpy()})
        yield p, d[d['n'] >= 3].reset_index(drop=True)


def main():
    os.makedirs(SORTIE, exist_ok=True)
    jd = pd.read_csv('data/prix/journalier_dukascopy.csv')
    j = rejouer('journalier 10 paires', [(p, d.reset_index(drop=True)) for p, d in jd[jd['paire'] != 'XAUUSD'].groupby('paire')], 5)
    j['periode'] = np.where(j['date'] < '2020', '2012-2019', '2020-2026')
    h4 = rejouer('4 h, 22 paires', series_h4(), 30)
    h4['periode'] = '2024-2026'
    j.to_csv(f'{SORTIE}/journalier.csv.gz', index=False)
    h4.to_csv(f'{SORTIE}/h4.csv.gz', index=False)
    res = []
    for d in (j, h4):
        rb = d['englobante'] | d['pin_bar']
        groupes = {
            'zone + bougie de retournement': d['zone'] & rb,
            'zone + englobante': d['zone'] & d['englobante'],
            'zone + pin bar': d['zone'] & d['pin_bar'],
            'mouvement climatique + bougie de retournement': d['climat'] & rb,
            'climatique + zone + bougie': d['climat'] & d['zone'] & rb,
            'témoin : bougie de retournement seule': rb,
            'témoin : zone seule (sans bougie)': d['zone'],
        }
        for (rj, per, k), x in d.groupby(['rejeu', 'periode', 'objectif']):
            for g, m in groupes.items():
                y = x[m.loc[x.index]]
                res.append(dict(rejeu=rj, periode=per, objectif=f'{k} R', groupe=g, trades=len(y),
                                gagnants=round((y['r'] > 0).mean(), 3) if len(y) else np.nan,
                                r_moyen=round(y['r'].mean(), 3) if len(y) else np.nan,
                                erreur_type=round(y['r'].std() / np.sqrt(len(y)), 3) if len(y) > 1 else np.nan))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 220)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
