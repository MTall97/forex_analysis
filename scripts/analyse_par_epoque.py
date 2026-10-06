#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse les trades d'Amirou séparément pour ses deux manières de trader :
- 2021-2022 : Wyckoff / smart money / quarter points, stops serrés, grands ratios ;
- 2023-2026 : fondamental, sentiment, MLQ, stops de 40-50 pips, ratios de 1:2 à 1:3,5.

Données :
- data/trades_simules.csv (captures lues par OCR et rejouées sur les cours) ;
- data/meta_features.csv (contexte au moment de la publication, scripts/modele_meta.py) ;
- data/fondamental/indicateurs.csv (scripts/modele_fondamental.py) ;
- data/trades.csv (registre texte du canal, pour comparaison).

Pour chaque époque : volumes et statuts, performance (spread déduit), séries de pertes, effet
du BE, découpages (jour, heure, paire, sens, ratio, stop, MLQ, tendance, saisonnalité,
fondamentaux), puis un modèle d'IA entraîné uniquement sur l'époque, comparé au même modèle
entraîné sur les deux époques mélangées.

Sortie : tableaux Markdown à l'écran et data/epoques_trades.csv (un trade par ligne, avec époque).
Usage : python scripts/analyse_par_epoque.py
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(__file__))
from modele_meta import SPREAD, pip  # noqa: E402

EPOQUES = {'2021-2022': (2021, 2022), '2023-2026': (2023, 2026)}
JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']
FOND = ['surprise_30j', 'taux', 'taux_90j', 'cot', 'cot_4s', 'amirou_14j']
NOMS_FOND = {'surprise_30j': 'Surprises économiques 30 j', 'taux': 'Différentiel de taux',
             'taux_90j': 'Variation des taux 90 j', 'cot': 'COT (niveau)', 'cot_4s': 'COT (variation 4 sem.)',
             'amirou_14j': 'Son biais écrit (14 j)'}
META = ['rr', 'stop_pips', 'stop_atr', 'heure', 'session_londres', 'session_ny', 'session_asie', 'jour_semaine',
        'mois', 'avec_tendance', 'avec_saison', 'saison_neutre', 'dist_rond_r', 'achat', 'paire_jpy', 'paire_usd']


def epoque(an):
    return next((e for e, (a, b) in EPOQUES.items() if a <= an <= b), None)


def charger():
    s = pd.read_csv('data/trades_simules.csv')
    s['date'] = pd.to_datetime(s.date_publication)
    s['an'] = s.date.dt.year
    s['epoque'] = s.an.map(epoque)
    s['pip'] = s.paire.map(pip)
    s['stop_p'] = (s.entree - s.stop).abs() / s.pip
    s['mlq_dist'] = [abs(e - round(e / (250 * p)) * 250 * p) / p for e, p in zip(s.entree, s.pip)]
    risque = (s.entree - s.stop).abs()
    s['r_net'] = s.resultat_r - s.paire.map(lambda p: SPREAD.get(p, 2)) * s.pip / risque
    s['gagnant'] = (s.issue == 'objectif').astype(int)
    s['rr'] = s.ratio_rr
    s['jour'] = pd.to_datetime(s.entree_utc).dt.weekday
    m = pd.read_csv('data/meta_features.csv')
    m['date'] = pd.to_datetime(m.date)
    s = s.merge(m[['date', 'paire'] + [c for c in META if c != 'rr']], on=['date', 'paire'], how='left')
    ind = pd.read_csv('data/fondamental/indicateurs.csv', parse_dates=['date']).set_index(['devise', 'date'])
    sens = np.where(s.sens == 'achat', 1, -1)
    for v in FOND:
        def diff(r):
            try:
                d = r.date.normalize()
                return ind.at[(r.paire[:3], d), v] - ind.at[(r.paire[3:], d), v]
            except KeyError:
                return np.nan
        s[f'{v}_sens'] = [x for x in s.apply(diff, axis=1)] * sens
    return s


def ligne(nom, d):
    if not len(d):
        return f"| {nom} | 0 | | | |"
    h8 = d[d.ratio_rr <= 8]
    h8 = f"{h8.r_net.mean():+.2f} R" if len(h8) else "—"
    return f"| {nom} | {len(d)} | {d.gagnant.mean() * 100:.0f} % | {d.r_net.mean():+.2f} R | {h8} |"


def tableau(titre, groupes):
    print(f"\n**{titre}**\n")
    print("| | Trades | Gagnants | R net | R net hors ratios > 8 |\n|---|---|---|---|---|")
    for nom, d in groupes:
        print(ligne(nom, d))


def serie_max(r):
    m = c = 0
    for x in r:
        c = c + 1 if x < 0 else 0
        m = max(m, c)
    return m


def drawdown(r, risque=0.01):
    eq = np.cumprod(1 + risque * np.asarray(r))
    return (1 - eq / np.maximum.accumulate(eq)).max()


def modele(train, test):
    cols = META + [f'{v}_sens' for v in FOND]
    m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, C=0.3))
    m.fit(train[cols].fillna(0), train.gagnant)
    return m.predict_proba(test[cols].fillna(0))[:, 1]


def main():
    s = charger()
    s.to_csv('data/epoques_trades.csv', index=False)
    fini = s[(s.statut == 'annoncé') & s.issue.isin(['objectif', 'stop'])].sort_values('date')

    print("## Volumes et statuts des captures\n")
    print("| Époque | Captures lues | Annoncées | ↳ objectif | ↳ stop | ↳ jamais déclenchées | Après coup | "
          "dont objectif déjà dépassé | Incohérentes |\n|---|---|---|---|---|---|---|---|---|")
    for e in EPOQUES:
        d = s[s.epoque == e]
        a = d[d.statut == 'annoncé']
        print(f"| {e} | {len(d)} | {len(a)} | {(a.issue == 'objectif').sum()} | {(a.issue == 'stop').sum()} | "
              f"{a.issue.str.startswith('non déclenché').sum()} | {(d.statut == 'après coup').sum()} "
              f"({(d.statut == 'après coup').mean() * 100:.0f} %) | "
              f"{(d.issue == 'objectif déjà dépassé à la publication').sum()} | {(d.statut == 'incohérent').sum()} |")
    for e in EPOQUES:
        d = s[(s.epoque == e) & (s.statut == 'après coup') & s.issue.isin(['objectif', 'stop'])]
        print(f"\nAprès coup {e} : {len(d)} terminés, {d.gagnant.mean() * 100:.0f} % gagnants")

    print("\n## Performance des trades annoncés et terminés\n")
    print("| Époque | Trades | Gagnants | Stop médian | Ratio médian | R net | R net hors ratios > 8 | "
          "Série de stops max | Drawdown max à 1 % | à 2 % | Stops passés par +1 R | R net avec BE à 1 R |"
          "\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for e in EPOQUES:
        d = fini[fini.epoque == e]
        be = np.where((d.issue == 'stop') & (d.gain_max_r >= 1), d.r_net - d.resultat_r, d.r_net)
        print(f"| {e} | {len(d)} | {d.gagnant.mean() * 100:.0f} % | {d.stop_p.median():.0f} pips | "
              f"1:{d.ratio_rr.median():.1f} | {d.r_net.mean():+.2f} R | {d[d.ratio_rr <= 8].r_net.mean():+.2f} R | "
              f"{serie_max(d.r_net)} | {drawdown(d.r_net) * 100:.0f} % | {drawdown(d.r_net, 0.02) * 100:.0f} % | "
              f"{((d.issue == 'stop') & (d.gain_max_r >= 1)).sum()} / {(d.issue == 'stop').sum()} | {be.mean():+.2f} R |")
    print("\n| Année | Époque | Trades | Gagnants | R net | hors ratios > 8 |\n|---|---|---|---|---|---|")
    for an, d in fini.groupby('an'):
        print(f"| {an} | {d.epoque.iloc[0]} | {len(d)} | {d.gagnant.mean() * 100:.0f} % | {d.r_net.mean():+.2f} R | "
              f"{d[d.ratio_rr <= 8].r_net.mean():+.2f} R |")

    for e in EPOQUES:
        d = fini[fini.epoque == e]
        print(f"\n## Découpages {e} ({len(d)} trades)")
        tableau('Jour de déclenchement', [(JOURS[j], d[d.jour == j]) for j in range(5)])
        h = d.date.dt.hour
        tableau('Heure de publication (UTC)', [('nuit / Asie (0-7 h)', d[h < 7]), ('Londres (7-12 h)', d[(h >= 7) & (h < 12)]),
                                                ('New York (12-17 h)', d[(h >= 12) & (h < 17)]), ('soir (17-24 h)', d[h >= 17])])
        top = d.paire.value_counts()
        tableau('Paires (5 plus tradées)', [(p, d[d.paire == p]) for p in top.index[:5]] +
                [('autres', d[~d.paire.isin(top.index[:5])])])
        tableau('Sens', [('achat', d[d.sens == 'achat']), ('vente', d[d.sens == 'vente'])])
        tableau('Ratio annoncé', [('moins de 2,5', d[d.ratio_rr < 2.5]), ('2,5 à 5', d[(d.ratio_rr >= 2.5) & (d.ratio_rr < 5)]),
                                  ('5 à 8', d[(d.ratio_rr >= 5) & (d.ratio_rr <= 8)]), ('plus de 8', d[d.ratio_rr > 8])])
        tableau('Taille du stop', [('moins de 15 pips', d[d.stop_p < 15]), ('15 à 30', d[(d.stop_p >= 15) & (d.stop_p < 30)]),
                                   ('30 à 60', d[(d.stop_p >= 30) & (d.stop_p < 60)]), ('60 et plus', d[d.stop_p >= 60])])
        tableau('Distance au MLQ (niveau de 250 pips)', [('moins de 25 pips', d[d.mlq_dist <= 25]),
                                                          ('25 à 75', d[(d.mlq_dist > 25) & (d.mlq_dist <= 75)]),
                                                          ('plus de 75', d[d.mlq_dist > 75])])
        tableau('Tendance 20 jours', [('dans la tendance', d[d.avec_tendance == 1]), ('contre', d[d.avec_tendance == 0])])
        tableau('Saisonnalité (10 ans avant)', [('dans le sens', d[(d.avec_saison == 1)]),
                                               ('contre', d[(d.avec_saison == 0) & (d.saison_neutre == 0)])])
        print("\n**Fondamentaux au moment de la publication**\n")
        print("| Indicateur | Dans le sens | Contre |\n|---|---|---|")
        for v in FOND:
            c = d[f'{v}_sens']
            a, b = d[c > 0], d[c < 0]
            f = lambda x: f"{len(x)} : {x.gagnant.mean() * 100:.0f} %, {x.r_net.mean():+.2f} R" if len(x) else "—"
            print(f"| {NOMS_FOND[v]} | {f(a)} | {f(b)} |")

    print("\n## Modèle d'IA : une époque à la fois ou tout mélangé\n")
    print("| Année testée | Entraîné sur | Trades testés | AUC | R net, moitié retenue | R net, moitié écartée |"
          "\n|---|---|---|---|---|---|")
    plans = [(2022, [2021], 'époque seule (2021)'), (2022, [2021], None),
             (2024, [2023], 'époque seule (2023)'), (2024, [2021, 2022, 2023], 'tout mélangé (2021-2023)'),
             (2025, [2023, 2024], 'époque seule (2023-2024)'), (2025, [2021, 2022, 2023, 2024], 'tout mélangé (2021-2024)'),
             (2026, [2023, 2024, 2025], 'époque seule (2023-2025)'), (2026, [2021, 2022, 2023, 2024, 2025], 'tout mélangé (2021-2025)')]
    for an, ans, nom in plans:
        if nom is None:
            continue
        tr, te = fini[fini.an.isin(ans)], fini[fini.an == an]
        p = modele(tr, te)
        med = np.median(p)
        print(f"| {an} | {nom} | {len(te)} | {roc_auc_score(te.gagnant, p):.2f} | {te.r_net[p >= med].mean():+.2f} R | "
              f"{te.r_net[p < med].mean():+.2f} R |")

    t = pd.read_csv('data/trades.csv')
    t['an'] = t.date_utc.str[:4].astype(int)
    t['epoque'] = t.an.map(lambda a: epoque(a) or ('2019-2020' if a < 2021 else None))
    print("\n## Registre texte du canal (data/trades.csv)\n")
    issues = ['tp', 'gain', 'sl', 'be', 'rate', 'profit_flottant', 'inconnue']
    print("| Époque | Trades | " + " | ".join(issues) + " | Réussite (tp+gain / tp+gain+sl) |\n|" + "---|" * (len(issues) + 3))
    for e in ['2019-2020', '2021-2022', '2023-2026']:
        d = t[t.epoque == e]
        c = d.issue.value_counts()
        g, p = c.get('tp', 0) + c.get('gain', 0), c.get('sl', 0)
        taux = f"{g / (g + p) * 100:.0f} %" if g + p else "—"
        print(f"| {e} | {len(d)} | " + " | ".join(str(c.get(i, 0)) for i in issues) + f" | {taux} |")


if __name__ == '__main__':
    main()
