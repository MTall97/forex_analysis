#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Peut-on améliorer les stratégies en n'utilisant que ce que montrent le tracker et le journal des stratégies ?
Six règles « ne pas entrer quand… », fixées avant le test, tirées des colonnes du tracker :

  R1 saisonnalité contraire : la moyenne du même mois sur les 10 années précédentes (Fed H.10,
     data/rendements_mensuels.csv) va contre le sens du trade ;
  R2 annonce majeure dans les 24 h après l'entrée, sur l'une des deux devises (taux, NFP, inflation, chômage, PIB ;
     calendrier TradingView, importance haute) ;
  R3 décision de banque centrale dans les 48 h après l'entrée, sur l'une des deux devises ;
  R4 foule : positionnement des gérants d'actifs (COT) extrême dans le sens du trade (devise achetée au-dessus du 90e
     centile sur 3 ans, ou devise vendue sous le 10e), d'après le dernier rapport publié avant l'entrée ;
  R5 contre le narratif écrit d'Amirou (biais sur 14 jours, connu la veille, data/fondamental/indicateurs.csv) ;
  R6 contre le taux américain à 2 ans (paires avec le dollar) : achat du dollar alors que le 2 ans a baissé d'au moins
     3 pb sur 5 jours, ou vente alors qu'il a monté d'autant (connu la veille).

Trades : ceux des pages (journal des stratégies), règles inchangées :
  englobante + MLQ horaire 2024-2026, lundi-mardi-mercredi (filtre masterclass) 2024-2026, cassure-retour MLQ 2024-2026,
  suivi de tendance 1 R 2024-2026, et l'englobante + MLQ journalière 2012-2026 pour vérifier sur la durée.
Une règle n'est retenue que si les trades qu'elle écarte font moins bien que ceux qu'elle garde dans les deux moitiés
de chaque période et sur la plupart des stratégies.
Sortie : data/filtres_playbook/{trades.csv.gz, regles.csv, combine.csv}
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from contexte_marche import calendrier, cot, macro_us  # noqa: E402
from fiches_mensuelles import CLES  # noqa: E402

SORTIE = 'data/filtres_playbook'
REGLES = {'R1': 'saisonnalité contraire', 'R2': 'annonce majeure dans les 24 h', 'R3': 'banque centrale dans les 48 h',
          'R4': 'COT extrême dans le sens du trade', 'R5': "contre le narratif d'Amirou", 'R6': 'contre le taux US 2 ans'}


def heure(s):
    s = str(s).replace(' (clôture)', '').replace(' clôture', '').replace(' (jour)', '').strip()
    if s.endswith('24:00'):
        return pd.Timestamp(s[:10]) + pd.Timedelta(days=1)
    if len(s) == 10:                      # journalier : entrée à la clôture du jour
        return pd.Timestamp(s) + pd.Timedelta(days=1)
    return pd.Timestamp(s)


def trades():
    L = []
    for f, nom in [('data/journal_trades/englobante_mlq_horaire.csv', 'englobante + MLQ (horaire)'),
                   ('data/journal_trades/cassure_retour_mlq.csv', 'cassure-retour MLQ'),
                   ('data/journal_trades/suivi_tendance.csv', 'suivi de tendance 1 R'),
                   ('data/journal_trades/englobante_mlq_journalier.csv', 'englobante + MLQ (journalier 2012-2026)')]:
        d = pd.read_csv(f).dropna(subset=['r'])
        L.append(pd.DataFrame({'strategie': nom, 'paire': d['paire'], 'sens': d['sens'],
                               'te': d['entree_date_heure'].map(heure), 'r': d['r']}))
    n = pd.read_csv('data/notions_meet/trades.csv.gz')
    n = n[n['strategie'].str.startswith('lundi') & (n['variante'] == 'règle actuelle') & n['mlq']]
    L.append(pd.DataFrame({'strategie': 'lundi-mardi-mercredi', 'paire': n['paire'], 'sens': n['sens'],
                           'te': pd.to_datetime(n['date']) + pd.Timedelta(days=1), 'r': n['r']}))
    t = pd.concat(L, ignore_index=True)
    t['s'] = np.where(t['sens'] == 'achat', 1, -1)
    t['base'], t['cote'] = t['paire'].str[:3], t['paire'].str[3:]
    return t[t['paire'] != 'XAUUSD'].reset_index(drop=True)


def marquer(t):
    # R1 saisonnalité
    rm = pd.read_csv('data/rendements_mensuels.csv')
    rm['an'], rm['m'] = rm['mois'].str[:4].astype(int), rm['mois'].str[5:7]
    piv = rm.pivot_table(index=['paire', 'm'], columns='an', values='rendement_pct')
    moy = []
    for p, te in zip(t['paire'], t['te']):
        k = (p, f'{te.month:02d}')
        if k not in piv.index:
            moy.append(np.nan)
            continue
        row = piv.loc[k]
        moy.append(row[[a for a in row.index if te.year - 10 <= a < te.year]].mean())
    t['saison'] = moy
    t['R1'] = (np.sign(t['saison']) * t['s'] < 0).astype(float)
    t.loc[t['saison'].isna(), 'R1'] = np.nan
    # R2, R3 calendrier
    cal = calendrier()
    cal = cal[(cal['importance'] == 1) & cal['titre'].str.contains('|'.join(CLES), regex=True, na=False)
              & ~cal['titre'].str.contains('Flash|Prel|MoM', regex=True, na=False)]
    ev = {d: g['date'].sort_values().to_numpy() for d, g in cal.groupby('devise')}
    bc = {d: g['date'].sort_values().to_numpy() for d, g in cal[cal['titre'].str.contains('Interest Rate Decision')].groupby('devise')}

    def proche(dic, devs, te, h):
        a, b = np.datetime64(te), np.datetime64(te + pd.Timedelta(hours=h))
        for d in devs:
            x = dic.get(d)
            if x is not None:
                i = np.searchsorted(x, a, side='left')
                if i < len(x) and x[i] <= b:
                    return True
        return False
    couvert = t['te'] >= '2019-01-15'
    t['R2'] = np.array([proche(ev, (b, c), te, 24) for b, c, te in zip(t['base'], t['cote'], t['te'])], dtype=float)
    t['R3'] = np.array([proche(bc, (b, c), te, 48) for b, c, te in zip(t['base'], t['cote'], t['te'])], dtype=float)
    t.loc[~couvert, ['R2', 'R3']] = np.nan
    # R4 COT (rapport publié le vendredi suivant la date de référence)
    ct = cot()
    pct = ct.rolling(156, min_periods=60).apply(lambda x: (x <= x[-1]).mean() * 100, raw=True)
    pct.index = pct.index + pd.Timedelta(days=3)
    pj = pct.reindex(pct.index.union(pd.DatetimeIndex(t['te'].dt.normalize().unique()))).ffill()
    jb = [pj.at[te.normalize(), b] if b in pj else np.nan for b, te in zip(t['base'], t['te'])]
    jc = [pj.at[te.normalize(), c] if c in pj else np.nan for c, te in zip(t['cote'], t['te'])]
    achetee = np.where(t['s'] > 0, jb, jc)
    vendue = np.where(t['s'] > 0, jc, jb)
    t['R4'] = ((achetee >= 90) | (vendue <= 10)).astype(float)
    t.loc[np.isnan(achetee) & np.isnan(vendue), 'R4'] = np.nan
    # R5 narratif d'Amirou
    ind = pd.read_csv('data/fondamental/indicateurs.csv', parse_dates=['date'])
    b14 = ind.pivot_table(index='date', columns='devise', values='amirou_14j').sort_index().ffill().shift(1)
    bj = b14.reindex(b14.index.union(pd.DatetimeIndex(t['te'].dt.normalize().unique()))).ffill()
    sc = np.array([(bj.at[te.normalize(), b] if b in bj else 0) - (bj.at[te.normalize(), c] if c in bj else 0)
                   for b, c, te in zip(t['base'], t['cote'], t['te'])], dtype=float)
    t['R5'] = (np.nan_to_num(sc) * t['s'] < 0).astype(float)
    t.loc[t['te'] < '2019-04-01', 'R5'] = np.nan
    # R6 taux à 2 ans
    m = macro_us()
    d2 = m['DGS2'].diff(5).shift(1)
    dj = d2.reindex(d2.index.union(pd.DatetimeIndex(t['te'].dt.normalize().unique()))).ffill()
    x = dj.loc[t['te'].dt.normalize()].to_numpy()
    usd = np.where(t['base'] == 'USD', 1, np.where(t['cote'] == 'USD', -1, 0)) * t['s']   # +1 : achète le dollar
    t['R6'] = (((usd > 0) & (x <= -0.03)) | ((usd < 0) & (x >= 0.03))).astype(float)
    t.loc[usd == 0, 'R6'] = np.nan
    return t


def moitie(t):
    """Deux moitiés de la période de chaque stratégie (par date médiane)."""
    out = pd.Series(index=t.index, dtype=object)
    for s, g in t.groupby('strategie'):
        med = g['te'].quantile(0.5)
        out[g.index] = np.where(g['te'] < med, '1re moitié', '2e moitié')
    return out


def main():
    t = marquer(trades())
    t['moitie'] = moitie(t)
    os.makedirs(SORTIE, exist_ok=True)
    t.to_csv(f'{SORTIE}/trades.csv.gz', index=False)
    res = []
    for (s, mo), g in list(t.groupby(['strategie', 'moitie'])) + [((s, 'toute la période'), g) for s, g in t.groupby('strategie')]:
        for k, nom in REGLES.items():
            x = g[g[k].notna()]
            ecart, garde = x[x[k] == 1], x[x[k] == 0]
            if len(ecart) < 5 or len(garde) < 5:
                continue
            se = np.sqrt(ecart['r'].var() / len(ecart) + garde['r'].var() / len(garde))
            res.append(dict(strategie=s, periode=mo, regle=k, nom=nom, ecartes=len(ecart), part=round(len(ecart) / len(x), 2),
                            r_ecartes=round(ecart['r'].mean(), 3), r_gardes=round(garde['r'].mean(), 3),
                            gain=round(garde['r'].mean() - x['r'].mean(), 3),
                            ecart_t=round((garde['r'].mean() - ecart['r'].mean()) / se, 2)))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/regles.csv', index=False)
    pd.set_option('display.width', 230)
    print(r[r['periode'] == 'toute la période'].to_string(index=False))
    # stabilité : la règle aide-t-elle (r_ecartes < r_gardes) dans chaque moitié de chaque stratégie ?
    m = r[r['periode'] != 'toute la période']
    st = m.assign(aide=m['r_ecartes'] < m['r_gardes']).groupby(['regle', 'nom'])['aide'].agg(['sum', 'count']).reset_index()
    print('\nNombre de (stratégie x moitié) où la règle aide :')
    print(st.to_string(index=False))
    st.to_csv(f'{SORTIE}/stabilite.csv', index=False)


if __name__ == '__main__':
    main()
