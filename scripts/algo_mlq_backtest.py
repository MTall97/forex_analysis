#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Algorithme « MLQ » : rejet des niveaux de 250 pips (Major Large Quarters), tel que décrit par
Amirou (zones de 1 000 pips découpées en quarts de 250 pips : 1.10000, 1.12500, 1.15000… ;
2.50 yens sur les paires en JPY), avec une préférence pour le mercredi.

Règle de base (bougies horaires Yahoo, mi-décembre 2023 -> septembre 2026) :
- pendant les sessions de Londres et New York (07h-17h UTC), une bougie qui touche un MLQ
  (à 3 pips près) et clôture à au moins 10 pips de l'autre côté du niveau dont elle vient
  = « rejet » ; entrée à la clôture dans le sens du rejet (rejet par le haut -> vente) ;
- stop à 5 pips au-delà de l'extrême de la mèche ; objectif à 2,5 R ; un trade par paire et
  par jour ; sortie forcée après 5 jours ; spread déduit.

Variantes testées : tous les jours / mercredi seulement / mardi-jeudi ; avec ou sans filtre de
tendance (MM 20 jours) ; avec ou sans filtre fondamental (différentiel de surprises économiques
+ dynamique des taux, data/fondamental/indicateurs.csv).

Le script mesure d'abord ces deux habitudes sur ses trades réels (data/trades_simules.csv) :
part des entrées à moins de 25 pips d'un MLQ, et résultats selon le jour de déclenchement.

Sortie : data/backtest_mlq.csv et résumé à l'écran.
Usage : python scripts/algo_mlq_backtest.py [--habitudes-seulement]
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import timedelta
from statistics import mean

import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402
from algo_amirou_backtest import PAIRES, SPREAD_PIPS, pip, resume  # noqa: E402

RR = 2.5


def fondamental():
    df = pd.read_csv('data/fondamental/indicateurs.csv', parse_dates=['date'])
    df['score'] = df['surprise_30j'].fillna(0) / 10 + df['taux_90j'].fillna(0)
    return {(r.devise, r.date.date()): r.score for r in df.itertuples()}


def backtest(p, b, fond):
    pas = 250 * pip(p)
    tol, rej = 3 * pip(p), 10 * pip(p)
    jours = defaultdict(list)
    for x in b:
        jours[x[0].date()].append(x)
    dates = sorted(jours)
    closes = {d: jours[d][-1][4] for d in dates}
    trades = []
    for i in range(21, len(dates)):
        d = dates[i]
        ma20 = mean(closes[x] for x in dates[i - 20:i])
        tendance = 1 if closes[dates[i - 1]] > ma20 else -1
        fb = fond.get((p[:3], d), 0) - fond.get((p[3:], d), 0)
        pris = False
        for x in jours[d]:
            if pris or not (7 <= x[0].hour <= 16):
                continue
            o, h, l, c = x[1], x[2], x[3], x[4]
            sens = 0
            haut = (h // pas + 1) * pas if h % pas > tol else round(h / pas) * pas
            niveau_h = round(h / pas) * pas
            niveau_l = round(l / pas) * pas
            if abs(h - niveau_h) <= tol or (l < niveau_h < h):
                if c <= niveau_h - rej and o < niveau_h:      # monté chercher le niveau puis rejeté
                    sens, ext = -1, h
            if not sens and (abs(l - niveau_l) <= tol or (l < niveau_l < h)):
                if c >= niveau_l + rej and o > niveau_l:
                    sens, ext = 1, l
            if not sens:
                continue
            pris = True
            e = c
            risque = abs(e - ext) + 5 * pip(p)
            sl, tp = e - sens * risque, e + sens * RR * risque
            cout = SPREAD_PIPS[p] * pip(p) / risque
            res = None
            for y in [y for y in b if x[0] < y[0] <= x[0] + timedelta(days=5)]:
                if (sens == 1 and y[3] <= sl) or (sens == -1 and y[2] >= sl):
                    res = -1.0
                    break
                if (sens == 1 and y[2] >= tp) or (sens == -1 and y[3] <= tp):
                    res = RR
                    break
                dernier = y
            if res is None:
                res = (dernier[4] - e) * sens / risque
            trades.append(dict(paire=p, heure=x[0], jour=x[0].weekday(), sens=sens, tendance=int(sens == tendance),
                               fond=int(sens * fb > 0), fond_neutre=int(fb == 0), r=round(res - cout, 3),
                               risque_pips=round(risque / pip(p), 1)))
    return trades


def habitudes_amirou():
    """MLQ et mercredi sur ses trades annoncés et terminés (simulation sur les cours réels)."""
    import random
    d = pd.read_csv('data/trades_simules.csv')
    d = d[(d.statut == 'annoncé') & d.issue.isin(['objectif', 'stop'])].copy()
    d['pip'] = d.paire.map(pip)
    d['dist'] = d.apply(lambda r: abs(r.entree - round(r.entree / (250 * r.pip)) * 250 * r.pip) / r.pip, axis=1)
    random.seed(0)
    hasard = mean(1 if abs(random.uniform(0, 250) - 125) >= 100 else 0 for _ in range(100000))
    proche = d[d.dist <= 25]
    print(f"Ses trades annoncés et terminés : {len(d)}")
    print(f"  entrées à moins de 25 pips d'un MLQ : {len(proche) / len(d) * 100:.0f} % (hasard : {hasard * 100:.0f} %)")
    for nom, s in [('près d\'un MLQ', proche), ('loin d\'un MLQ', d[d.dist > 25])]:
        print(f"  {nom:<14} {len(s):>4} trades, {(s.issue == 'objectif').mean() * 100:.0f} % gagnants, "
              f"{s.resultat_r.mean():+.2f} R")
    d['jour'] = pd.to_datetime(d.entree_utc).dt.weekday
    print('  par jour de déclenchement :')
    for j, nom in enumerate(['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']):
        s = d[d.jour == j]
        if len(s):
            print(f"    {nom:<9} {len(s):>4} trades, {(s.issue == 'objectif').mean() * 100:.0f} % gagnants, "
                  f"{s.resultat_r.mean():+.2f} R")
    print()


def main():
    habitudes_amirou()
    if '--habitudes-seulement' in sys.argv:
        return
    fond = fondamental()
    tous = []
    for p in PAIRES:
        b = sorted(prix_yahoo.bougies(p, prix_yahoo.debut_horaire(p), pd.Timestamp('2026-10-01').to_pydatetime()))
        t = backtest(p, b, fond)
        tous += t
        print(f"  {p}: {len(t)} rejets de MLQ", flush=True)
    df = pd.DataFrame(tous).sort_values('heure')
    df.to_csv('data/backtest_mlq.csv', index=False)
    variantes = {
        'tous les jours': df,
        'mercredi seulement': df[df.jour == 2],
        'mardi à jeudi': df[df.jour.isin([1, 2, 3])],
        'tous les jours + tendance': df[df.tendance == 1],
        'mercredi + tendance': df[(df.jour == 2) & (df.tendance == 1)],
        'tous les jours + fondamental': df[df.fond == 1],
        'mercredi + fondamental': df[(df.jour == 2) & (df.fond == 1)],
        'mercredi + tendance + fondamental': df[(df.jour == 2) & (df.tendance == 1) & (df.fond == 1)],
    }
    for nom, v in variantes.items():
        t = [[r.paire, str(r.heure), r.sens, 0, 0, 0, r.r] for r in v.itertuples()]
        print(resume(nom, t))
    print('\nPar jour de la semaine (toutes variantes confondues) :')
    for j, nom in enumerate(['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']):
        s = df[df.jour == j]
        if len(s):
            print(f"  {nom:<9} {len(s):>4} trades, {(s.r > 0).mean() * 100:.0f} % gagnants, espérance {s.r.mean():+.3f} R")


if __name__ == '__main__':
    main()
