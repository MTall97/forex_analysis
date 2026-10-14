#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peut-on choisir les bons trades d'une stratégie en apprenant des trades gagnants et perdants ?

Trades : data/journal_trades/*.csv (scripts/journal_trades_strategies.py). Variables connues à l'entrée :
paire, sens, jour de la semaine, heure, risque en ATR, tendance sur 5 et 20 jours (en ATR, dans le sens du trade),
volatilité relative, position dans le range de 60 jours, narratif d'Amirou (14 j), écart de COT, écart de taux.

Trois façons de sélectionner :
- « meilleures paires du passé » : garder les couples paire × sens dont le R moyen passé est > 0 (au moins 10 trades) ;
  c'est ce qu'on fait en regardant à la main les trades gagnants et perdants ;
- « régression linéaire » (ridge) qui prédit le R du trade ; on garde les trades dont le R prédit est > 0 ;
- « arbres de décision » (gradient boosting peu profond), même règle.

Deux mesures :
- « dans l'échantillon » : le modèle apprend sur tous les trades et sélectionne ces mêmes trades. C'est ce que donne
  une optimisation faite après coup ; le résultat est flatteur par construction ;
- « hors échantillon » (walk-forward) : par trimestre, le modèle n'apprend que sur les trades sortis avant le début
  du trimestre (7 jours de marge), puis choisit parmi les trades du trimestre. C'est ce qu'on aurait gagné en vrai.
Sortie : data/selection_trades/resultats.csv
"""
import os
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge

warnings.filterwarnings('ignore')
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
SORTIE = 'data/selection_trades'
NUM = ['jour_semaine', 'heure', 'risque_atr', 'tendance_5j', 'tendance_20j', 'vol_relative', 'position_60j',
       'narratif', 'cot_ecart', 'taux_ecart']
JEUX = {'englobante + MLQ, journalier 2012-2026': ('englobante_mlq_journalier', '2016-01-01'),
        'englobante + MLQ, horaire 2024-2026': ('englobante_mlq_horaire', '2025-01-01'),
        'cassure puis retour MLQ, horaire 2024-2026': ('cassure_retour_mlq', '2025-01-01'),
        'suivi de tendance 1 R, horaire 2024-2026': ('suivi_tendance', '2025-01-01')}


def matrice(d, colonnes=None, medianes=None):
    x = d[NUM].copy()
    medianes = x.median() if medianes is None else medianes
    x = x.fillna(medianes).fillna(0)
    x = pd.concat([x, pd.get_dummies(d['paire'] + '_' + d['sens'], dtype=float)], axis=1)
    if colonnes is not None:
        x = x.reindex(columns=colonnes, fill_value=0.0)
    return x, medianes


def predire(methode, train, test):
    if methode == 'meilleures paires du passé':
        g = train.groupby(['paire', 'sens'])['r'].agg(['mean', 'size'])
        ok = set(g[(g['mean'] > 0) & (g['size'] >= 10)].index)
        return np.array([1.0 if (p, s) in ok else -1.0 for p, s in zip(test['paire'], test['sens'])])
    xa, med = matrice(train)
    xt, _ = matrice(test, xa.columns, med)
    if methode == 'régression linéaire':
        mu, sd = xa.mean(), xa.std().replace(0, 1)
        m = Ridge(alpha=10.0).fit((xa - mu) / sd, train['r'])
        return m.predict((xt - mu) / sd)
    m = HistGradientBoostingRegressor(max_depth=3, min_samples_leaf=30, max_iter=150, learning_rate=0.05,
                                      random_state=0).fit(xa, train['r'])
    return m.predict(xt)


def stats(r):
    r = np.asarray(r, dtype=float)
    return (len(r), round(r.mean(), 3) if len(r) else np.nan,
            round(r.std(ddof=1) / np.sqrt(len(r)), 3) if len(r) > 1 else np.nan)


def main():
    res = []
    for nom, (f, debut_test) in JEUX.items():
        d = pd.read_csv(f'data/journal_trades/{f}.csv').dropna(subset=['r'])          # sans les trades en cours
        d = d.assign(entree_date_heure=d['entree_date_heure'].str[:10])
        d['t_entree'] = pd.to_datetime(d['entree_date_heure'].str[:10])
        d['t_sortie'] = pd.to_datetime(d['sortie_date_heure'].str[:10])
        for methode in ['meilleures paires du passé', 'régression linéaire', 'arbres de décision']:
            # 1. dans l'échantillon (optimisation après coup)
            p = predire(methode, d, d)
            sel = d['r'][p > 0]
            n, m, e = stats(sel)
            res.append(dict(strategie=nom, methode=methode, mesure="dans l'échantillon (après coup)",
                            periode=f"{d['t_entree'].min():%Y}-{d['t_entree'].max():%Y}", trades=len(d),
                            r_tous=round(d['r'].mean(), 3), gardes=n, r_gardes=m, erreur_type=e,
                            r_rejetes=round(d['r'][p <= 0].mean(), 3)))
            # 2. hors échantillon, trimestre par trimestre
            choix = []
            for q in pd.date_range(debut_test, d['t_entree'].max() + pd.offsets.QuarterBegin(1), freq='QS'):
                test = d[(d['t_entree'] >= q) & (d['t_entree'] < q + pd.offsets.QuarterBegin(1))]
                train = d[d['t_sortie'] < q - pd.Timedelta(days=7)]
                if len(test) == 0 or len(train) < 100:
                    continue
                choix.append(test.assign(pred=predire(methode, train, test)))
            c = pd.concat(choix)
            n, m, e = stats(c['r'][c['pred'] > 0])
            res.append(dict(strategie=nom, methode=methode, mesure='hors échantillon (walk-forward)',
                            periode=f"{c['t_entree'].min():%Y-%m}-{c['t_entree'].max():%Y-%m}", trades=len(c),
                            r_tous=round(c['r'].mean(), 3), gardes=n, r_gardes=m, erreur_type=e,
                            r_rejetes=round(c['r'][c['pred'] <= 0].mean(), 3)))
            print(res[-2]['strategie'], '|', methode, '| après coup', res[-2]['r_gardes'], '| hors échantillon',
                  res[-1]['r_gardes'], '±', res[-1]['erreur_type'], 'contre', res[-1]['r_tous'], 'pour tous', flush=True)
    r = pd.DataFrame(res)
    os.makedirs(SORTIE, exist_ok=True)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 250)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
