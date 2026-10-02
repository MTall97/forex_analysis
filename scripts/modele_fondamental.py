#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Version « fondamentale » du modèle : indicateurs macro par devise, puis trois tests.

Indicateurs par devise et par jour (calculés uniquement avec l'information publiée AVANT ce jour) :
- surprise_30j : somme des surprises économiques des 30 derniers jours (annonce - consensus,
  normalisée par l'écart habituel de l'indicateur ; signe inversé pour chômage et inscriptions
  au chômage ; plafonnée à ±3 par annonce), annonces d'importance moyenne ou forte ;
- taux / taux_90j : taux directeur et sa variation sur 90 jours (BIS) ;
- cot / cot_4s : positionnement net des fonds à effet de levier en % de l'open interest (CFTC)
  et sa variation sur 4 semaines ;
- amirou_14j : biais exprimé par Amirou sur 14 jours (scripts/biais_textuel.py).
Pour une paire BASE/COTATION, chaque indicateur = valeur(BASE) - valeur(COTATION).

Tests :
A. La lecture macro d'Amirou anticipe-t-elle la devise sur les 5 jours suivants ?
B. Ses trades (data/trades_simules.csv) gagnent-ils plus quand ils vont dans le sens des
   fondamentaux ? Méta-modèle avec ces variables, validation chronologique.
C. Modèle fondamental autonome : prévoir le sens de la semaine suivante sur 13 paires
   (validation chronologique par année, coûts déduits), puis l'utiliser comme biais de
   l'algorithme technique (scripts/algo_amirou_backtest.py).

Sorties : data/fondamental/indicateurs.csv, data/fondamental/resultats_tests.json, résumé écran.
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(__file__))

DEV = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF']
PAYS_DEV = {'US': 'USD', 'EU': 'EUR', 'DE': 'EUR', 'GB': 'GBP', 'JP': 'JPY', 'AU': 'AUD', 'NZ': 'NZD',
            'CA': 'CAD', 'CH': 'CHF'}
INVERSE = re.compile(r'unemploy|jobless|claimant|initial claims|continuing claims', re.I)
PAIRES = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'EURJPY', 'GBPJPY', 'AUDJPY',
          'EURGBP', 'GBPAUD', 'EURAUD', 'EURNZD']
VARS = ['surprise_30j', 'taux', 'taux_90j', 'cot', 'cot_4s', 'amirou_14j']


# ---------------------------------------------------------------- indicateurs par devise
def surprises():
    df = pd.read_csv('data/fondamental/calendrier.csv')
    df = df[df['pays'].isin(PAYS_DEV) & df['importance'].isin([0, 1])]
    df = df.dropna(subset=['actuel', 'consensus'])
    df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_localize(None)
    df['devise'] = df['pays'].map(PAYS_DEV)
    df['ecart'] = pd.to_numeric(df['actuel'], errors='coerce') - pd.to_numeric(df['consensus'], errors='coerce')
    df = df.dropna(subset=['ecart']).sort_values('date')
    # échelle propre à chaque indicateur : écart absolu médian des annonces PRÉCÉDENTES
    df['cle'] = df['pays'] + '|' + df['indicateur'].fillna(df['titre'])
    df['echelle'] = df.groupby('cle')['ecart'].transform(lambda s: s.abs().shift().expanding().median())
    df = df[df['echelle'] > 0]
    df['z'] = (df['ecart'] / df['echelle']).clip(-3, 3)
    df.loc[df['titre'].str.contains(INVERSE) | df['indicateur'].fillna('').str.contains(INVERSE), 'z'] *= -1
    return df[['date', 'devise', 'z', 'titre']]


def serie_quotidienne(debut, fin):
    jours = pd.date_range(debut, fin, freq='D')
    out = {}
    sp = surprises()
    taux = pd.read_csv('data/fondamental/taux.csv', parse_dates=['date'])
    cot = pd.read_csv('data/fondamental/cot.csv', parse_dates=['publication'])
    am = pd.read_csv('data/fondamental/biais_amirou.csv', parse_dates=['date'])
    for d in DEV:
        s = sp[sp.devise == d].set_index('date')['z']
        # surprise cumulée sur 30 jours, connue AVANT le jour J (décalage d'un jour)
        cum = s.groupby(s.index.floor('D')).sum().reindex(jours, fill_value=0).rolling(30, min_periods=1).sum().shift(1)
        t = taux[taux.devise == d].set_index('date')['taux_directeur'].groupby(level=0).last()
        t = t.reindex(jours).ffill().shift(1)
        c = cot[cot.devise == d].set_index('publication')['fonds_levier_net_oi'].groupby(level=0).last()
        c = c.reindex(jours).ffill().shift(1)
        a = am[am.devise == d].groupby('date')['score'].sum().reindex(jours, fill_value=0).rolling(14, min_periods=1).sum().shift(1)
        out[d] = pd.DataFrame({'surprise_30j': cum, 'taux': t, 'taux_90j': t - t.shift(90), 'cot': c,
                               'cot_4s': c - c.shift(28), 'amirou_14j': a}, index=jours)
    # le dollar n'a pas de contrat COT direct dans la plupart des années : opposé de la moyenne des autres
    if out['USD']['cot'].isna().mean() > 0.5:
        autres = pd.concat([out[d]['cot'] for d in DEV if d != 'USD'], axis=1).mean(axis=1)
        out['USD']['cot'] = -autres
        out['USD']['cot_4s'] = out['USD']['cot'] - out['USD']['cot'].shift(28)
    return out


def pour_paire(ind, paire, date):
    b, q = paire[:3], paire[3:]
    if b not in ind or q not in ind:
        return None
    d = pd.Timestamp(date.date())
    try:
        return {v: float(ind[b].at[d, v] - ind[q].at[d, v]) for v in VARS}
    except KeyError:
        return None


# ---------------------------------------------------------------- prix quotidiens (Fed H.10)
def prix_quotidiens():
    fx = pd.read_csv('data/prix/fx_daily_fred.csv', parse_dates=['Date'])
    noms = {'Euro': 'EUR', 'United Kingdom': 'GBP', 'Japan': 'JPY', 'Australia': 'AUD', 'New Zealand': 'NZD',
            'Canada': 'CAD', 'Switzerland': 'CHF'}
    fx['dev'] = fx['Country'].map(noms)
    u = fx.pivot_table(index='Date', columns='dev', values='Exchange rate').dropna()
    u['USD'] = 1.0
    return u  # unités de devise pour 1 USD


# ---------------------------------------------------------------- test A
def test_a(ind, u):
    am = pd.read_csv('data/fondamental/biais_amirou.csv', parse_dates=['date'])
    g = am.groupby(['date', 'devise'])['score'].sum().reset_index()
    g = g[g.score != 0]
    # valeur d'une devise contre le panier des 7 autres : moyenne des log(prix en devise étrangère)
    lu = np.log(u)
    indice = pd.DataFrame({d: -(lu[d] - lu.drop(columns=d).mean(axis=1)) for d in DEV})
    res = []
    for r in g.itertuples():
        d0 = indice.index.searchsorted(r.date + pd.Timedelta(days=1))
        if d0 + 5 >= len(indice):
            continue
        perf = indice[r.devise].iloc[d0 + 5] - indice[r.devise].iloc[d0 - 1]
        res.append({'date': r.date, 'devise': r.devise, 'signe': np.sign(r.score), 'perf_5j': perf * 100})
    df = pd.DataFrame(res)
    df['juste'] = np.sign(df.perf_5j) == df.signe
    out = {'n': int(len(df)), 'taux_juste': round(float(df.juste.mean()), 3),
           'perf_moyenne_dans_le_sens_pct': round(float((df.signe * df.perf_5j).mean()), 3)}
    par_an = df.groupby(df.date.dt.year).apply(lambda x: round(float(x.juste.mean()), 3)).to_dict()
    out['par_annee'] = {int(k): v for k, v in par_an.items()}
    par_dev = df.groupby('devise').apply(lambda x: (round(float(x.juste.mean()), 3), int(len(x)))).to_dict()
    out['par_devise'] = par_dev
    return out


# ---------------------------------------------------------------- test B
SPREAD = {'EURUSD': 0.8, 'GBPUSD': 1.2, 'USDJPY': 1.0, 'AUDUSD': 1.0, 'NZDUSD': 1.5, 'USDCAD': 1.5, 'USDCHF': 1.5,
          'EURJPY': 1.5, 'GBPJPY': 2.5, 'AUDJPY': 1.8, 'NZDJPY': 2.0, 'CADJPY': 2.0, 'CHFJPY': 2.5, 'EURGBP': 1.2,
          'GBPAUD': 2.5, 'EURAUD': 2.0, 'EURNZD': 3.0, 'EURCAD': 2.0, 'EURCHF': 1.5, 'GBPNZD': 3.5, 'GBPCAD': 3.0,
          'GBPCHF': 2.5, 'AUDNZD': 2.0, 'AUDCAD': 2.0, 'NZDCAD': 2.5}


def pip(p):
    return 0.01 if p.endswith('JPY') else 0.0001


def test_b(ind):
    rows = []
    for r in csv.DictReader(open('data/trades_simules.csv', encoding='utf-8')):
        if r['statut'] != 'annoncé' or r['issue'] not in ('objectif', 'stop') or r['paire'] not in SPREAD:
            continue
        d = datetime.fromisoformat(r['date_publication'])
        f = pour_paire(ind, r['paire'], d)
        if not f:
            continue
        s = 1 if r['sens'] == 'achat' else -1
        risque = abs(float(r['entree']) - float(r['stop']))
        x = {f'{v}_sens': s * f[v] for v in VARS}
        x.update(date=d, gagnant=int(r['issue'] == 'objectif'),
                 r_net=float(r['resultat_r']) - SPREAD[r['paire']] * pip(r['paire']) / risque, rr=float(r['ratio_rr']))
        rows.append(x)
    df = pd.DataFrame(rows).sort_values('date').reset_index(drop=True)
    out = {'n': int(len(df)), 'univarie': {}}
    for v in VARS:
        c = f'{v}_sens'
        dd = df.dropna(subset=[c])
        avec, contre = dd[dd[c] > 0], dd[dd[c] < 0]
        out['univarie'][v] = {'avec': [int(len(avec)), round(float(avec.gagnant.mean()), 3) if len(avec) else None,
                                       round(float(avec.r_net.mean()), 2) if len(avec) else None],
                              'contre': [int(len(contre)), round(float(contre.gagnant.mean()), 3) if len(contre) else None,
                                         round(float(contre.r_net.mean()), 2) if len(contre) else None]}
    cols = [f'{v}_sens' for v in VARS] + ['rr']
    dfm = df.fillna(0)
    pr_all, y_all, r_all = [], [], []
    for an in [2023, 2024, 2025, 2026]:
        app, test = dfm[dfm.date.dt.year < an], dfm[dfm.date.dt.year == an]
        if len(test) < 5:
            continue
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.3)).fit(app[cols], app.gagnant)
        pr_all += list(m.predict_proba(test[cols])[:, 1])
        y_all += list(test.gagnant)
        r_all += list(test.r_net)
    pr, y, r = np.array(pr_all), np.array(y_all), np.array(r_all)
    med = np.median(pr)
    out['meta_auc'] = round(float(roc_auc_score(y, pr)), 3)
    out['meta_selection'] = {'tous': round(float(r.mean()), 2), 'meilleure_moitie': round(float(r[pr >= med].mean()), 2),
                             'moitie_ecartee': round(float(r[pr < med].mean()), 2), 'n_test': int(len(r))}
    return out


# ---------------------------------------------------------------- test C
def test_c(ind, u):
    lu = np.log(u)
    vendredis = [d for d in u.index if d.weekday() == 4 and d >= pd.Timestamp('2020-01-01')]
    rows = []
    for d in vendredis:
        i = u.index.get_loc(d)
        if i + 5 >= len(u):
            break
        for p in PAIRES:
            b, q = p[:3], p[3:]
            f = pour_paire(ind, p, d.to_pydatetime() + timedelta(days=1))
            if not f or any(np.isnan(v) for v in f.values()):
                continue
            prix = lambda k: lu[q].iloc[k] - lu[b].iloc[k]  # log(prix de la paire)
            ret = (prix(i + 5) - prix(i)) * 100
            mom = (prix(i) - prix(i - 20)) * 100 if i >= 20 else 0.0
            rows.append(dict(date=d, paire=p, ret=ret, mom_4s=mom, **f))
    df = pd.DataFrame(rows)
    df['y'] = (df.ret > 0).astype(int)
    cols = VARS + ['mom_4s']
    out = {'n_semaines_paires': int(len(df)), 'par_annee': {}}
    cout = 0.015  # ≈ 1,5 pip aller-retour, en %
    for nom, mdl in [('logistique', lambda: make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, C=0.3))),
                     ('gradient_boosting', lambda: GradientBoostingClassifier(n_estimators=200, max_depth=2,
                                                                               learning_rate=0.03, subsample=0.8, random_state=0))]:
        tous_p, tous_y, tous_r = [], [], []
        for an in range(2022, 2027):
            app, test = df[df.date.dt.year < an], df[df.date.dt.year == an]
            if len(test) < 20:
                continue
            m = mdl().fit(app[cols], app.y)
            p_ = m.predict_proba(test[cols])[:, 1]
            pos = np.where(p_ > 0.5, 1, -1)
            pnl = pos * test.ret.values - cout
            out['par_annee'].setdefault(nom, {})[an] = {'auc': round(float(roc_auc_score(test.y, p_)), 3),
                                                        'gain_moyen_pct_semaine': round(float(pnl.mean()), 3),
                                                        'gain_total_pct': round(float(pnl.sum()), 1)}
            tous_p += list(p_)
            tous_y += list(test.y)
            tous_r += list(pnl)
        out[nom] = {'auc': round(float(roc_auc_score(tous_y, tous_p)), 3),
                    'gain_moyen_pct_par_trade': round(float(np.mean(tous_r)), 4),
                    'gain_total_pct_somme': round(float(np.sum(tous_r)), 1),
                    'part_gagnante': round(float(np.mean(np.array(tous_r) > 0)), 3)}
    # repères simples
    t = df[df.date.dt.year >= 2022]
    out['repere_momentum'] = round(float((np.sign(t.mom_4s) * t.ret - cout).mean()), 4)
    out['repere_portage_taux'] = round(float((np.sign(t.taux) * t.ret - cout).mean()), 4)
    out['repere_surprises'] = round(float((np.sign(t.surprise_30j) * t.ret - cout).mean()), 4)
    out['repere_amirou'] = round(float((np.sign(t.amirou_14j[t.amirou_14j != 0]) * t.ret[t.amirou_14j != 0] - cout).mean()), 4)
    out['n_semaines_avec_avis_amirou'] = int((t.amirou_14j != 0).sum())
    return out, df


def main():
    ind = serie_quotidienne('2019-01-01', '2026-10-01')
    pd.concat({d: ind[d] for d in DEV}, names=['devise', 'date']).reset_index().to_csv(
        'data/fondamental/indicateurs.csv', index=False, float_format='%.4f')
    u = prix_quotidiens()
    res = {}
    res['A_lecture_macro_amirou'] = test_a(ind, u)
    print('A.', json.dumps(res['A_lecture_macro_amirou'], ensure_ascii=False))
    res['B_ses_trades_vs_fondamentaux'] = test_b(ind)
    print('B.', json.dumps(res['B_ses_trades_vs_fondamentaux'], ensure_ascii=False))
    res['C_modele_fondamental_hebdo'], _ = test_c(ind, u)
    print('C.', json.dumps(res['C_modele_fondamental_hebdo'], ensure_ascii=False))
    json.dump(res, open('data/fondamental/resultats_tests.json', 'w'), ensure_ascii=False, indent=1, default=str)


if __name__ == '__main__':
    main()
