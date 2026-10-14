#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Le « narratif » d'Amirou ajouté à ses stratégies : les configurations vont-elles mieux quand elles suivent l'avis
qu'il a écrit sur les devises ?

Narratif : biais écrit par devise sur les 14 jours précédents (data/fondamental/indicateurs.csv, colonne amirou_14j,
tirée de ses messages et de ses rapports SignalX par scripts/biais_textuel.py). Pour une paire A/B, le biais vaut
biais(A) - biais(B), connu la veille du signal : > 0 = narratif acheteur, < 0 = vendeur, 0 ou absent = pas d'avis.

Stratégies (trades déjà simulés, mêmes règles que leurs rapports) :
- englobante + MLQ, objectif 2 R : data/englobante_mlq_objectifs/{journalier,horaire}.csv ;
- cassure puis retour sur MLQ, stop 0,5 ATR, objectif 2 R : data/cassure_retour_mlq/{journalier,horaire}.csv.gz.
Chaque trade est classé : dans le sens du narratif, contre, ou sans avis. Sortie : data/narratif_strategies/resultats.csv
"""
import os

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
SORTIE = 'data/narratif_strategies'


def biais_paires():
    i = pd.read_csv('data/fondamental/indicateurs.csv', usecols=['devise', 'date', 'amirou_14j'])
    b = i.pivot_table(index='date', columns='devise', values='amirou_14j').fillna(0)
    b.index = pd.to_datetime(b.index)
    return b.shift(1)                      # connu la veille


def classer(d, b):
    d = d.copy()
    jour = pd.to_datetime(d['date'].str[:10])
    base = np.array([b[p[:3]].get(j, np.nan) if p[:3] in b.columns else np.nan for p, j in zip(d['paire'], jour)])
    cote = np.array([b[p[3:]].get(j, np.nan) if p[3:] in b.columns else np.nan for p, j in zip(d['paire'], jour)])
    bias = base - cote
    s = np.where(d['sens'] == 'achat', 1, -1)
    d['narratif'] = np.select([np.isnan(bias) | (bias == 0), np.sign(bias) == s], ['sans avis', 'dans le sens'], 'contre')
    return d


def main():
    b = biais_paires()
    jeux = {
        'englobante + MLQ, journalier 2020-2026': pd.read_csv('data/englobante_mlq_objectifs/journalier.csv')
        .query("mlq and objectif == 2 and date >= '2020-01-01'"),
        'englobante + MLQ, horaire 2024-2026': pd.read_csv('data/englobante_mlq_objectifs/horaire.csv').query('mlq and objectif == 2'),
        'cassure-retour MLQ, journalier 2019-2026': pd.read_csv('data/cassure_retour_mlq/journalier.csv.gz')
        .query("groupe == 'MLQ' and objectif == 2 and stop_atr == 0.5 and date >= '2019-04-01'"),
        'cassure-retour MLQ, horaire 2024-2026': pd.read_csv('data/cassure_retour_mlq/horaire.csv.gz')
        .query("groupe == 'MLQ' and objectif == 2 and stop_atr == 0.5"),
    }
    res = []
    for nom, d in jeux.items():
        d = classer(d, b)
        for n, x in d.groupby('narratif'):
            res.append(dict(strategie=nom, narratif=n, trades=len(x), gagnants=round((x['r'] > 0).mean(), 3),
                            r_moyen=round(x['r'].mean(), 3), erreur_type=round(x['r'].std() / np.sqrt(len(x)), 3)))
    r = pd.DataFrame(res)
    os.makedirs(SORTIE, exist_ok=True)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 200)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
