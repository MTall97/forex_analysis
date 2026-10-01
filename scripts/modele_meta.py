#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modèle d'IA « méta » : sur les trades annoncés à l'avance par Amirou (data/trades_simules.csv,
statut « annoncé », issue objectif ou stop), apprend quels contextes mènent à l'objectif.

Variables calculées au moment de la publication (aucune information future) :
- ratio objectif/risque, taille du stop en pips et en ATR journalier (14 jours) ;
- heure de publication (UTC), session (Asie, Londres, New York), jour de la semaine, mois ;
- tendance : sens du trade vs clôture d'hier au-dessus / au-dessous de la moyenne 20 jours ;
- saisonnalité ex ante : sens du trade vs biais du mois sur les 10 années précédentes ;
- distance de l'entrée au niveau rond le plus proche (00 / 50), en fraction de risque ;
- paire (USD, JPY, croisées) et sens.

Validation : chronologique (entraînement sur le passé, test sur la période suivante), jamais
mélangée. On compare la sélection du modèle (trades à probabilité prédite > seuil) au fait de
prendre tous les trades. Sorties : data/meta_features.csv et un rapport à l'écran.
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402

SPREAD = {'EURUSD': 0.8, 'GBPUSD': 1.2, 'USDJPY': 1.0, 'AUDUSD': 1.0, 'NZDUSD': 1.5, 'USDCAD': 1.5, 'USDCHF': 1.5,
          'EURJPY': 1.5, 'GBPJPY': 2.5, 'AUDJPY': 1.8, 'NZDJPY': 2.0, 'CADJPY': 2.0, 'CHFJPY': 2.5, 'EURGBP': 1.2,
          'GBPAUD': 2.5, 'EURAUD': 2.0, 'EURNZD': 3.0, 'EURCAD': 2.0, 'EURCHF': 1.5, 'GBPNZD': 3.5, 'GBPCAD': 3.0,
          'GBPCHF': 2.5, 'AUDNZD': 2.0, 'AUDCAD': 2.0, 'NZDCAD': 2.5, 'XAUUSD': 30, 'US30': 30}


def pip(p):
    return 0.01 if p.endswith('JPY') or p == 'XAUUSD' else 1.0 if p == 'US30' else 0.0001


def biais_saison():
    rend = defaultdict(dict)
    for r in csv.DictReader(open('data/rendements_mensuels.csv', encoding='utf-8')):
        rend[r['paire']][r['mois']] = float(r['rendement_pct'])

    def f(p, an, mo):
        v = [rend[p][f"{y}-{mo:02d}"] for y in range(an - 10, an) if f"{y}-{mo:02d}" in rend.get(p, {})]
        return 0 if len(v) < 6 else (1 if mean(v) > 0 else -1)
    return f


def features():
    saison = biais_saison()
    rows = []
    for r in csv.DictReader(open('data/trades_simules.csv', encoding='utf-8')):
        if r['statut'] != 'annoncé' or r['issue'] not in ('objectif', 'stop'):
            continue
        p, d = r['paire'], datetime.fromisoformat(r['date_publication'])
        e, sl, tp = float(r['entree']), float(r['stop']), float(r['objectif'])
        s = 1 if r['sens'] == 'achat' else -1
        jour = prix_yahoo._charger(p, '1d')
        hist = jour[jour['date'] < pd.Timestamp(d.date())].tail(25)
        if len(hist) < 21:
            continue
        tr = (hist['high'] - hist['low']).tail(14).mean()
        ma20 = hist['close'].tail(20).mean()
        tendance = 1 if hist['close'].iloc[-1] > ma20 else -1
        risque = abs(e - sl)
        pas = 50 * pip(p) if p not in ('XAUUSD', 'US30') else (10.0 if p == 'XAUUSD' else 100.0)
        rond = min(abs(e - round(e / pas) * pas), pas) / risque
        h = d.hour
        rows.append({
            'date': d, 'paire': p, 'issue': r['issue'], 'gagnant': int(r['issue'] == 'objectif'),
            'resultat_r_net': float(r['resultat_r']) - SPREAD.get(p, 2) * pip(p) / risque,
            'rr': float(r['ratio_rr']), 'stop_pips': risque / pip(p), 'stop_atr': risque / tr,
            'heure': h, 'session_londres': int(7 <= h < 12), 'session_ny': int(12 <= h < 17),
            'session_asie': int(h >= 21 or h < 7), 'jour_semaine': d.weekday(), 'mois': d.month,
            'avec_tendance': int(s == tendance), 'avec_saison': int(s == saison(p, d.year, d.month)),
            'saison_neutre': int(saison(p, d.year, d.month) == 0), 'dist_rond_r': rond,
            'achat': int(s == 1), 'paire_jpy': int('JPY' in p), 'paire_usd': int('USD' in p),
            'resolution_horaire': int(prix_yahoo.resolution(p, d) == '1h'),
        })
    return pd.DataFrame(rows).sort_values('date').reset_index(drop=True)


def univarie(df):
    print("\nTaux de réussite et espérance nette par contexte :")
    def ligne(nom, m):
        sub = df[m]
        if len(sub) >= 8:
            print(f"  {nom:<34} n={len(sub):>3}  réussite {sub.gagnant.mean() * 100:4.0f} %  espérance {sub.resultat_r_net.mean():+.2f} R")
    ligne('tous', df.index >= 0)
    for c, nom in [('avec_tendance', 'dans le sens de la tendance'), ('avec_saison', 'dans le sens de la saison'),
                   ('session_londres', 'publié session de Londres'), ('session_ny', 'publié session de New York'),
                   ('session_asie', 'publié session asiatique / nuit'), ('achat', 'achats'), ('paire_jpy', 'paires en JPY')]:
        ligne(nom, df[c] == 1)
        ligne('  (contraire)', df[c] == 0)
    for a, b, nom in [(0, 2.5, 'ratio < 2,5'), (2.5, 4, 'ratio 2,5 à 4'), (4, 100, 'ratio > 4')]:
        ligne(nom, (df.rr >= a) & (df.rr < b))
    for a, b, nom in [(0, 0.3, 'stop < 0,3 ATR'), (0.3, 0.7, 'stop 0,3 à 0,7 ATR'), (0.7, 99, 'stop > 0,7 ATR')]:
        ligne(nom, (df.stop_atr >= a) & (df.stop_atr < b))
    for j, nom in enumerate(['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']):
        ligne(nom, df.jour_semaine == j)


def chronologique(df):
    cols = ['rr', 'stop_pips', 'stop_atr', 'heure', 'session_londres', 'session_ny', 'session_asie', 'jour_semaine',
            'mois', 'avec_tendance', 'avec_saison', 'saison_neutre', 'dist_rond_r', 'achat', 'paire_jpy', 'paire_usd']
    print("\nValidation chronologique (apprend sur le passé, teste sur l'année suivante) :")
    for nom, modele in [('régression logistique', make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.5))),
                        ('gradient boosting', GradientBoostingClassifier(n_estimators=150, max_depth=2, learning_rate=0.05, subsample=0.8, random_state=0))]:
        tout_p, tout_y, tout_r = [], [], []
        for an in [2023, 2024, 2025, 2026]:
            app = df[df.date.dt.year < an]
            test = df[df.date.dt.year == an]
            if len(test) < 5 or app.gagnant.nunique() < 2:
                continue
            modele.fit(app[cols], app.gagnant)
            pr = modele.predict_proba(test[cols])[:, 1]
            tout_p += list(pr)
            tout_y += list(test.gagnant)
            tout_r += list(test.resultat_r_net)
        pr, y, r = np.array(tout_p), np.array(tout_y), np.array(tout_r)
        auc = roc_auc_score(y, pr) if len(set(y)) > 1 else float('nan')
        seuil = np.median(pr)
        print(f"  {nom}: AUC hors échantillon {auc:.2f} (0,50 = hasard) sur {len(y)} trades 2023-2026")
        print(f"     tous les trades : espérance {r.mean():+.2f} R | moitié jugée la meilleure : {r[pr >= seuil].mean():+.2f} R "
              f"| moitié écartée : {r[pr < seuil].mean():+.2f} R")
        if nom == 'gradient boosting':
            imp = sorted(zip(modele.feature_importances_, cols), reverse=True)[:6]
            print('     variables les plus utilisées : ' + ', '.join(f"{c} ({v:.2f})" for v, c in imp))


def main():
    df = features()
    df.to_csv('data/meta_features.csv', index=False)
    print(f"{len(df)} trades annoncés avec issue (objectif / stop) -> data/meta_features.csv")
    univarie(df)
    chronologique(df)


if __name__ == '__main__':
    main()
