#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La « fourchette » : ne trader une paire que quand plusieurs raisons indépendantes vont dans le même sens
(positions des spéculateurs au COT, banques centrales, tendance), par analogie avec la « fourchette » du morpion
(deux menaces à la fois). Test hebdomadaire sur les 28 paires des 8 grandes devises (USD, EUR, GBP, JPY, AUD, NZD, CAD, CHF), 2007-2026.

Chaque vendredi (jour de publication du COT), pour une paire A/B :
- COT (fonds à effet de levier, position nette en part de l'intérêt ouvert, CFTC « TFF ») :
  - « COT suivi » : z-score sur 3 ans de A moins celui de B ; on suit les spéculateurs si l'écart >= 1 ;
  - « COT accélération » : variation sur 4 semaines de A moins celle de B, dans le même sens ;
  - « COT contrarien » : contre les spéculateurs quand l'écart des z-scores >= 2 (positions extrêmes) ;
- banques centrales (taux directeurs BIS) :
  - « divergence » : le différentiel de taux A - B a monté (ou baissé) sur les 13 dernières semaines ;
  - « portage » : différentiel de taux d'au moins 0,5 point ;
- tendance : sens du rendement de la paire sur 4 semaines (variante : 13 semaines).
Une « fourchette » = trois raisons d'accord : on prend la position du vendredi au vendredi suivant.

Rendement : variation de change + différentiel de taux encaissé (portage / 52), moins 0,03 % à chaque ouverture,
fermeture ou retournement de position. Les 28 paires se recoupent : la significativité est mesurée sur la série
hebdomadaire du portefeuille (moyenne des positions ouvertes chaque semaine), pas trade par trade.
Validation : 2007-2014, 2015-2019, 2020-2026. Aucun seuil n'a été ajusté après coup.

Données : data/fondamental/cot.csv, data/prix/taux_directeurs_1999.csv, data/prix/fx_daily_fred_1999.csv.
Sortie : data/fourchette/resultats.csv, data/fourchette/hebdo.csv.gz
"""
import itertools
import os

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
SORTIE = 'data/fourchette'
PAYS = {'Euro': 'EUR', 'United Kingdom': 'GBP', 'Japan': 'JPY', 'Australia': 'AUD', 'New Zealand': 'NZD',
        'Canada': 'CAD', 'Switzerland': 'CHF'}
DEVISES = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'NZD', 'CAD', 'CHF']
COUT = 0.0003


def donnees():
    fx = pd.read_csv('data/prix/fx_daily_fred_1999.csv', parse_dates=['Date'])
    fx['dev'] = fx['Country'].map(PAYS)
    s = fx.pivot_table(index='Date', columns='dev', values='Exchange rate').ffill()
    # fichier datasets/exchange-rates : toutes les séries en unités de devise pour 1 USD
    vend = s.resample('W-FRI').last()
    logv = -np.log(vend)                       # log de la valeur de chaque devise en USD
    logv['USD'] = 0.0
    tx = pd.read_csv('data/prix/taux_directeurs_1999.csv', parse_dates=['date'])
    tx = tx.pivot_table(index='date', columns='devise', values='taux').ffill().resample('W-FRI').last()
    tx = tx.reindex(logv.index).ffill()
    cot = pd.read_csv('data/fondamental/cot.csv', parse_dates=['publication'])
    cot['semaine'] = cot['publication'].dt.to_period('W-FRI').dt.end_time.dt.normalize()
    c = cot.pivot_table(index='semaine', columns='devise', values='fonds_levier_net_oi').reindex(logv.index).ffill(limit=2)
    return logv[DEVISES], tx[DEVISES], c[DEVISES]


def main():
    logv, tx, cot = donnees()
    z = (cot - cot.rolling(156, min_periods=104).mean()) / cot.rolling(156, min_periods=104).std()
    dcot = cot.diff(4)
    lignes = []
    for a, b in itertools.combinations(DEVISES, 2):
        p = logv[a] - logv[b]                                  # log du prix de A en B
        r_suiv = p.shift(-1) - p + (tx[a] - tx[b]) / 100 / 52   # semaine suivante, portage compris
        diff = tx[a] - tx[b]
        zz = z[a] - z[b]
        d = pd.DataFrame({
            'paire': f'{a}{b}', 'r_suivant': r_suiv,
            'cot_suivi': np.where(zz >= 1, 1, np.where(zz <= -1, -1, 0)),
            'cot_acceleration': np.sign(dcot[a] - dcot[b]),
            'cot_contrarien': np.where(zz >= 2, -1, np.where(zz <= -2, 1, 0)),
            'divergence': np.sign(diff - diff.shift(13)).fillna(0),
            'portage': np.where(diff >= 0.5, 1, np.where(diff <= -0.5, -1, 0)),
            'tendance_4s': np.sign(p - p.shift(4)),
            'tendance_13s': np.sign(p - p.shift(13)),
        }, index=p.index)
        d.loc[zz.isna(), ['cot_suivi', 'cot_contrarien']] = np.nan
        d.loc[(dcot[a] - dcot[b]).isna(), 'cot_acceleration'] = np.nan
        lignes.append(d)
    h = pd.concat(lignes).rename_axis('semaine').reset_index()
    h = h[(h['semaine'] >= '2007-01-01') & h['r_suivant'].notna()]

    def accord(*cols):
        x = h[list(cols)]
        s = np.sign(x.sum(axis=1))
        ok = (x.abs() == 1).all(axis=1) & (x.nunique(axis=1) == 1)
        return np.where(ok, s, 0)

    regles = {
        # raisons seules
        'COT suivi seul': h['cot_suivi'], 'COT accélération seule': h['cot_acceleration'],
        'COT contrarien seul': h['cot_contrarien'], 'divergence de taux seule': h['divergence'],
        'portage seul': h['portage'], 'tendance 4 semaines seule': h['tendance_4s'],
        'tendance 13 semaines seule': h['tendance_13s'],
        # fourchettes (trois raisons d'accord)
        'fourchette : COT suivi + divergence + tendance 4s': accord('cot_suivi', 'divergence', 'tendance_4s'),
        'fourchette : COT suivi + portage + tendance 4s': accord('cot_suivi', 'portage', 'tendance_4s'),
        'fourchette : COT accélération + portage + tendance 4s': accord('cot_acceleration', 'portage', 'tendance_4s'),
        'fourchette : COT suivi + portage + tendance 13s': accord('cot_suivi', 'portage', 'tendance_13s'),
        'fourchette : COT contrarien + divergence + tendance 4s': accord('cot_contrarien', 'divergence', 'tendance_4s'),
        # deux raisons
        'COT suivi + tendance 4s': accord('cot_suivi', 'tendance_4s'),
        'portage + tendance 13s': accord('portage', 'tendance_13s'),
    }
    res, series = [], {}
    for nom, pos in regles.items():
        x = h[['semaine', 'paire', 'r_suivant']].copy()
        x['pos'] = pd.Series(pos, index=h.index).fillna(0).to_numpy()
        x = x.sort_values(['paire', 'semaine'])
        prec = x.groupby('paire')['pos'].shift().fillna(0)
        x['r'] = x['pos'] * x['r_suivant'] - COUT * (x['pos'] - prec).abs()
        actifs = x[x['pos'] != 0]
        port = actifs.groupby('semaine')['r'].mean().reindex(sorted(h['semaine'].unique())).fillna(0)
        series[nom] = port
        for per, (d0, d1) in {'2007-2026': ('2007', '2027'), '2007-2014': ('2007', '2015'),
                              '2015-2019': ('2015', '2020'), '2020-2026': ('2020', '2027')}.items():
            a = actifs[(actifs['semaine'] >= d0) & (actifs['semaine'] < d1)]
            s = port[(port.index >= d0) & (port.index < d1)]
            s_act = s[s != 0]
            res.append(dict(regle=nom, periode=per, positions_semaine=len(a),
                            semaines_actives=int((s != 0).sum()),
                            positions_gagnantes=round((a['r'] > 0).mean(), 3) if len(a) else np.nan,
                            r_moyen_position_pct=round(a['r'].mean() * 100, 3) if len(a) else np.nan,
                            rendement_annuel_pct=round(s.mean() * 52 * 100, 2),
                            sharpe=round(s.mean() / s.std() * np.sqrt(52), 2) if s.std() > 0 else np.nan,
                            t_stat=round(s_act.mean() / s_act.std() * np.sqrt(len(s_act)), 2) if len(s_act) > 2 else np.nan))
    r = pd.DataFrame(res)
    os.makedirs(SORTIE, exist_ok=True)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.DataFrame(series).to_csv(f'{SORTIE}/hebdo.csv.gz')
    pd.set_option('display.width', 250)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
