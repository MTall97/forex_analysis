"""Liste datée des trades simulés pour chaque règle de la masterclass, centrée sur 2020-2026.

Lit les fichiers d'occurrences produits par les tests (data/par_paire/occurrences_*.csv,
issus de tester_masterclass.py, tester_bebe_abandonne.py, tester_strategie_bombe.py,
strategie_combinee.py, tester_flashcards_englobante.py, via analyse_par_paire.py).

Sorties :
- data/masterclass_2020_2026/<regle>.csv : chaque trade de 2020-2026 (date, paire, sens, niveaux, issue, R) ;
- data/masterclass_2020_2026/resume_par_annee.csv : n, % gagnants, R moyen et cumulé par règle et par année ;
- data/masterclass_2020_2026/avant_apres_2020.csv : 2012-2019 contre 2020-2026 ;
- data/masterclass_2020_2026/t1_jour_plus_haut_par_annee.csv et t4_audjpy_avril.csv.

Usage : python scripts/trades_masterclass_par_date.py
"""
import math
import os

import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OCC = os.path.join(RACINE, 'data', 'par_paire')
SORTIE = os.path.join(RACINE, 'data', 'masterclass_2020_2026')

REGLES = [
    ('t2_trois_barres', 'T2 Lundi-mardi-mercredi « trois barres »',
     'occurrences_lundi_mardi_mercredi_trois_barres.csv'),
    ('t3_lundi_mardi_haussiers', 'T3 Lundi et mardi haussiers, mercredi prend le high',
     'occurrences_lundi_et_mardi_haussiers_mercredi_prend_.csv'),
    ('t5_mlq', 'T5 MLQ ±25 / stop 50 / objectif 250 pips', 'occurrences_mlq_25_50_250_pips.csv'),
    ('bebe_abandonne_journalier', 'Bébé abandonné (journalier)', 'occurrences_bebe_abandonne_journalier.csv'),
    ('bebe_abandonne_horaire', 'Bébé abandonné (horaire)', 'occurrences_bebe_abandonne_horaire.csv'),
    ('bombe_h1', 'Bombe (H1)', 'occurrences_bombe_h1.csv'),
    ('englobante_mercredi', 'Englobante du mercredi (objectif 2 R)',
     'occurrences_englobante_du_mercredi_objectif_2_r.csv'),
    ('englobante_mlq', 'Englobante + MLQ (objectif 2 R)', 'occurrences_englobante_mlq_objectif_2_r.csv'),
    ('trois_barres_mlq', 'Trois barres + MLQ (sortie au 3e jour)',
     'occurrences_trois_barres_mlq_sortie_au_3e_jour.csv'),
    ('flashcards_englobante', 'Englobante « Naruto » (rupture des flashcards)',
     'occurrences_englobante_rupture_des_flashcards.csv'),
]

PERIODES = [('2012-2019', 2012, 2019), ('2020-2026', 2020, 2026)]


def stats(r):
    r = pd.to_numeric(r, errors='coerce').dropna()
    n = len(r)
    if n == 0:
        return dict(n=0, gagnants_pct=None, r_moyen=None, r_cumule=None, t=None)
    sd = r.std(ddof=1) if n > 1 else float('nan')
    t = r.mean() / (sd / math.sqrt(n)) if n > 1 and sd > 0 else float('nan')
    return dict(n=n, gagnants_pct=round(100 * (r > 0).mean(), 1), r_moyen=round(r.mean(), 3),
                r_cumule=round(r.sum(), 1), t=round(t, 2))


def charger(fichier):
    d = pd.read_csv(os.path.join(OCC, fichier))
    d['date'] = pd.to_datetime(d['date'])
    d['annee'] = d['date'].dt.year
    return d.sort_values('date')


def t1_jour_plus_haut(j):
    """Part des plus hauts (et plus bas) hebdomadaires formés mardi ou mercredi, par année."""
    j = j.copy()
    j['date'] = pd.to_datetime(j['date'])
    j = j[j['date'].dt.dayofweek < 5]
    j['semaine'] = j['date'].dt.to_period('W-SUN')
    lignes = []
    for (p, s), g in j.groupby(['paire', 'semaine']):
        if len(g) < 4:
            continue
        lignes.append(dict(paire=p, annee=g['date'].iloc[0].year,
                           jour_haut=g.loc[g['high'].idxmax(), 'date'].dayofweek,
                           jour_bas=g.loc[g['low'].idxmin(), 'date'].dayofweek))
    w = pd.DataFrame(lignes)
    res = []
    for a, g in w.groupby('annee'):
        res.append(dict(annee=a, semaines=len(g),
                        haut_mardi_mercredi_pct=round(100 * g['jour_haut'].isin([1, 2]).mean(), 1),
                        bas_mardi_mercredi_pct=round(100 * g['jour_bas'].isin([1, 2]).mean(), 1),
                        haut_lundi_ou_vendredi_pct=round(100 * g['jour_haut'].isin([0, 4]).mean(), 1)))
    return pd.DataFrame(res)


def t4_mois(j, paire, mois):
    """Pour chaque année : date du plus bas du mois, plus bas en 1re semaine ?, variation du mois."""
    d = j[j['paire'] == paire].copy()
    d['date'] = pd.to_datetime(d['date'])
    d = d[d['date'].dt.month == mois]
    res = []
    for a, g in d.groupby(d['date'].dt.year):
        g = g.sort_values('date')
        jbas = g.loc[g['low'].idxmin(), 'date']
        res.append(dict(annee=a, paire=paire, mois=mois, ouverture=g['open'].iloc[0], cloture=g['close'].iloc[-1],
                        variation_pct=round(100 * (g['close'].iloc[-1] / g['open'].iloc[0] - 1), 2),
                        date_plus_bas=jbas.date(), plus_bas_semaine_1=bool(jbas.day <= 7),
                        repli_sous_ouverture_pips=round((g['open'].iloc[0] - g['low'].min()) * 100, 0)))
    return pd.DataFrame(res)


def main():
    os.makedirs(SORTIE, exist_ok=True)
    resume, avant_apres = [], []
    for cle, nom, fichier in REGLES:
        d = charger(fichier)
        recent = d[d['annee'] >= 2020].drop(columns=['annee'])
        recent.to_csv(os.path.join(SORTIE, f'{cle}.csv'), index=False, float_format='%.5f')
        for a in range(2020, 2027):
            s = stats(d.loc[d['annee'] == a, 'r'])
            resume.append(dict(regle=nom, annee=a, **s))
        for lib, a0, a1 in PERIODES:
            s = stats(d.loc[d['annee'].between(a0, a1), 'r'])
            avant_apres.append(dict(regle=nom, periode=lib,
                                    premiere_date=d.loc[d['annee'].between(a0, a1), 'date'].min(),
                                    derniere_date=d.loc[d['annee'].between(a0, a1), 'date'].max(), **s))
        print(f'{nom} : {len(recent)} trades 2020-2026')
    pd.DataFrame(resume).to_csv(os.path.join(SORTIE, 'resume_par_annee.csv'), index=False)
    pd.DataFrame(avant_apres).to_csv(os.path.join(SORTIE, 'avant_apres_2020.csv'), index=False)

    j = pd.read_csv(os.path.join(RACINE, 'data', 'prix', 'journalier_dukascopy.csv'))
    t1_jour_plus_haut(j).to_csv(os.path.join(SORTIE, 't1_jour_plus_haut_par_annee.csv'), index=False)
    pd.concat([t4_mois(j, 'AUDJPY', 4), t4_mois(j, 'EURJPY', 6)]).to_csv(
        os.path.join(SORTIE, 't4_audjpy_avril_eurjpy_juin.csv'), index=False)


if __name__ == '__main__':
    main()
