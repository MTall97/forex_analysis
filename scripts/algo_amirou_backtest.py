#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version algorithmique (simplifiée) de la méthode enseignée par Amirou, backtestée sur les
bougies horaires Yahoo Finance (mi-décembre 2023 -> septembre 2026, ~2,8 ans).

Règles traduites du canal (voir analyses/STRATEGIE_ET_MODELE.md) :
- biais du jour : tendance (clôture d'hier au-dessus / au-dessous de sa moyenne mobile 20 jours),
  en option combiné au biais saisonnier ex ante du mois (scripts/saisonnalite_mensuelle.py) ;
- « prise de liquidité / spring » : pendant les sessions de Londres et New York (07h-17h UTC),
  le prix passe sous le plus bas de la veille (achat) ou au-dessus du plus haut de la veille
  (vente), puis la bougie horaire clôture de nouveau à l'intérieur du range de la veille ;
- entrée à cette clôture ; stop au-delà de l'extrême de la mèche (+ 10 % du risque) ;
  objectif à 2,5 R (Amirou vise « minimum 1:2,5 ») ; un trade par paire et par jour ;
- option « BE » : stop remonté à l'entrée quand le gain latent atteint 1 R ;
- fin de trade au plus tard après 5 jours (« money likes speed » : sortie au prix du moment).

Coûts : un spread fixe par paire est déduit (paramètre SPREAD_PIPS). Pas de glissement.

Sortie : data/backtest_algo.csv (un trade par ligne) et un résumé à l'écran.
Usage :
    python scripts/algo_amirou_backtest.py [--debut 2021-01] [--fin 2026-09]
"""

import argparse
import csv
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402

PAIRES = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'EURJPY', 'GBPJPY',
          'AUDJPY', 'EURGBP', 'GBPAUD', 'EURAUD', 'EURNZD']
SPREAD_PIPS = {'EURUSD': 0.8, 'GBPUSD': 1.2, 'USDJPY': 1.0, 'AUDUSD': 1.0, 'NZDUSD': 1.5, 'USDCAD': 1.5,
               'EURJPY': 1.5, 'GBPJPY': 2.5, 'AUDJPY': 1.8, 'EURGBP': 1.2, 'GBPAUD': 2.5, 'EURAUD': 2.0, 'EURNZD': 3.0}
RR = 2.5


def pip(p):
    return 0.01 if p.endswith('JPY') else 0.0001


def biais_saisonnier():
    """(paire, mois, année) -> +1 / -1 / 0, sur les 10 années précédentes."""
    rend = defaultdict(dict)
    for r in csv.DictReader(open('data/rendements_mensuels.csv', encoding='utf-8')):
        rend[r['paire']][r['mois']] = float(r['rendement_pct'])
    def f(p, an, mo):
        v = [rend[p][f"{y}-{mo:02d}"] for y in range(an - 10, an) if f"{y}-{mo:02d}" in rend[p]]
        if len(v) < 6:
            return 0
        pos = sum(x > 0 for x in v) / len(v)
        return 1 if pos >= 0.6 and mean(v) > 0 else -1 if pos <= 0.4 and mean(v) < 0 else 0
    return f


def bougies(p, debut, fin):
    """Bougies horaires Yahoo (disponibles depuis mi-décembre 2023)."""
    debut = max(debut, prix_yahoo.debut_horaire(p))
    return sorted(prix_yahoo.bougies(p, debut, fin))


def backtest(p, b, saison, filtre_saison, avec_be):
    jours = defaultdict(list)
    for x in b:
        jours[x[0].date()].append(x)
    dates = sorted(jours)
    closes = {d: jours[d][-1][4] for d in dates}
    trades = []
    for i in range(21, len(dates)):
        d, veille = dates[i], dates[i - 1]
        hv = max(x[2] for x in jours[veille])
        lv = min(x[3] for x in jours[veille])
        ma20 = mean(closes[x] for x in dates[i - 20:i])
        tendance = 1 if closes[veille] > ma20 else -1
        s = saison(p, d.year, d.month)
        if filtre_saison and s != tendance:
            continue
        pris = False
        for k, x in enumerate(jours[d]):
            if pris or not (7 <= x[0].hour <= 16):
                continue
            sens = 0
            if tendance == 1 and x[3] < lv and x[4] > lv:
                sens, e, ext = 1, x[4], x[3]
            elif tendance == -1 and x[2] > hv and x[4] < hv:
                sens, e, ext = -1, x[4], x[2]
            if not sens:
                continue
            risque = abs(e - ext) * 1.1
            if risque < 5 * pip(p):
                continue
            pris = True
            sl = e - sens * risque
            tp = e + sens * RR * risque
            cout = SPREAD_PIPS[p] * pip(p) / risque
            suite = [y for y in b if x[0] < y[0] <= x[0] + timedelta(days=5)]
            stop, be_actif, res = sl, False, None
            for y in suite:
                if (sens == 1 and y[3] <= stop) or (sens == -1 and y[2] >= stop):
                    res = 0.0 if be_actif else -1.0
                    break
                if (sens == 1 and y[2] >= tp) or (sens == -1 and y[3] <= tp):
                    res = RR
                    break
                if avec_be and not be_actif and ((y[2] - e) * sens if sens == 1 else (e - y[3])) >= risque:
                    be_actif, stop = True, e
            if res is None:
                res = ((suite[-1][4] - e) * sens / risque) if suite else 0.0
            trades.append([p, x[0].isoformat(), 'achat' if sens == 1 else 'vente', round(e, 5), round(sl, 5),
                           round(tp, 5), round(res - cout, 3)])
    return trades


def resume(nom, t):
    if not t:
        return f"{nom}: aucun trade"
    r = [x[-1] for x in t]
    gagnants = sum(1 for x in r if x > 0)
    eq, pic, dd = 0, 0, 0
    for x in r:
        eq += x
        pic = max(pic, eq)
        dd = max(dd, pic - eq)
    return (f"{nom}: {len(r)} trades, {gagnants / len(r) * 100:.0f} % gagnants, espérance {mean(r):+.3f} R/trade, "
            f"total {sum(r):+.1f} R, perte max cumulée {dd:.1f} R")


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--debut', default='2023-12')
    a.add_argument('--fin', default='2026-10')
    args = a.parse_args()
    debut = datetime.strptime(args.debut, '%Y-%m')
    fin = datetime.strptime(args.fin, '%Y-%m')
    saison = biais_saisonnier()
    variantes = {'tendance seule': (False, False), 'tendance + BE à 1R': (False, True),
                 'tendance + saisonnalité': (True, False), 'tendance + saisonnalité + BE': (True, True)}
    tous = defaultdict(list)
    for p in PAIRES:
        b = bougies(p, debut, fin)
        print(f"  {p}: {len(b)} bougies", flush=True)
        for nom, (fs, be) in variantes.items():
            tous[nom] += backtest(p, b, saison, fs, be)
    with open('data/backtest_algo.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['variante', 'paire', 'heure_utc', 'sens', 'entree', 'stop', 'objectif', 'resultat_r'])
        for nom, t in tous.items():
            for x in t:
                w.writerow([nom] + x)
    for nom, t in tous.items():
        print(resume(nom, sorted(t, key=lambda x: x[1])))
        par_an = defaultdict(list)
        for x in t:
            par_an[x[1][:4]].append(x[-1])
        print('   par année : ' + ', '.join(f"{y} {sum(v):+.0f}R" for y, v in sorted(par_an.items())))


if __name__ == '__main__':
    main()
