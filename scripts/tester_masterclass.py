#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste sur les cours réels les règles chiffrées enseignées par Amirou (masterclass et canal).

Données :
- bougies journalières Dukascopy 2010-2026 (data/prix/journalier_dukascopy.csv, scripts/prix_dukascopy_journalier.py) ;
- bougies horaires Yahoo déc. 2023 - sept. 2026 (scripts/prix_yahoo.py) pour les règles qui dépendent de l'heure.

Tests :
T1  « Le plus haut de la semaine se forme entre mardi et mercredi 70 % du temps » (#7820 ; masterclass : 60-75 %).
T2  Stratégie « trois barres » lundi-mardi-mercredi (masterclass ; 85 % sur GBPUSD, 70-75 % sur AUDJPY) :
    vente si lundi haussier « plein » (corps >= 60 % du range, clôture dans le quart haut), mardi rouge qui
    clôture sous la clôture de lundi ; entrée à la clôture du mardi, stop au-dessus du plus haut du mardi,
    objectif = plus bas du lundi, au moins 60 pips et RR >= 1,2, sortie au plus tard le vendredi. Achat : symétrique.
    Variantes : mardi qui dépasse d'abord le plus haut du lundi ; plus haut du mardi fait à Londres (horaire).
T3  « Lundi haussier, mardi haussier, mercredi prend le high de mardi avant de tomber » : 21 fois en 5 ans,
    71 % avec SL 20 pips et TP 60 pips (#14577-#14579). Vente au plus haut du mardi quand mercredi le dépasse.
T4  AUDJPY en avril : le plus bas du mois se forme en 1re semaine dans 75 % des cas (2015-2024), repli moyen
    de 91 pips sous l'ouverture du mois (masterclass ; #14662).
T5  MLQ (niveaux de 250 pips) : zone de ±25 pips, stop de 50 pips, objectif 250 pips, RR 1:5 (masterclass).
T6  « Bébé abandonné » : testé à part dans scripts/tester_bebe_abandonne.py.
T7  Corrélation AUDUSD / NZDUSD « de l'ordre de 80 % » (masterclass).
T8  Après une consolidation, « l'expansion suit systématiquement la sortie du range » (masterclass).

Toutes les simulations journalières sont prudentes : si l'objectif et le stop sont touchés le même jour,
on compte le stop. Le spread (modele_meta.SPREAD) est déduit.

Sorties : data/masterclass_resultats.json, data/masterclass_trades.csv, résumé à l'écran.
"""

import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_dukascopy_journalier as dk  # noqa: E402
import prix_yahoo  # noqa: E402
from modele_meta import SPREAD  # noqa: E402

JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi']


def pip(p):
    return 0.01 if p.endswith('JPY') else 0.1 if p == 'XAUUSD' else 0.0001


def spread(p):
    return SPREAD.get(p, 2) * (0.01 if p == 'XAUUSD' else pip(p))


def simuler_jours(d, i_debut, i_fin, sens, entree, sl, tp, p):
    """Rejoue un trade sur les bougies journalières d'indices i_debut..i_fin inclus. Renvoie (R net, issue)."""
    risque = abs(entree - sl)
    for j in range(i_debut, i_fin + 1):
        h, l = d.high.iat[j], d.low.iat[j]
        stop = h >= sl if sens < 0 else l <= sl
        obj = l <= tp if sens < 0 else h >= tp
        if stop:
            return -1 - spread(p) / risque, 'stop' if not obj else 'stop (même jour que l\'objectif)'
        if obj:
            return abs(tp - entree) / risque - spread(p) / risque, 'objectif'
    c = d.close.iat[i_fin]
    return (c - entree) * sens / risque - spread(p) / risque, 'sortie vendredi'


def resume(trades):
    if not len(trades):
        return {'n': 0}
    t = pd.DataFrame(trades)
    return {'n': int(len(t)), 'objectif_pct': round(float((t.issue == 'objectif').mean() * 100), 1),
            'gagnants_pct': round(float((t.r > 0).mean() * 100), 1), 'r_moyen': round(float(t.r.mean()), 3),
            'r_total': round(float(t.r.sum()), 1)}


# ------------------------------------------------------------------ T1
def t1(jd):
    out = {}
    for nom, col in [('plus_haut', 'high'), ('plus_bas', 'low')]:
        cpt = np.zeros(5)
        for p, d in jd.groupby('paire'):
            d = d.assign(sem=d.date.dt.to_period('W'))
            for _, s in d.groupby('sem'):
                if len(s) < 5:
                    continue
                j = s[col].idxmax() if col == 'high' else s[col].idxmin()
                cpt[s.loc[j, 'date'].weekday()] += 1
        out[nom] = {JOURS[k]: round(float(cpt[k] / cpt.sum() * 100), 1) for k in range(5)}
        out[nom]['mardi_mercredi'] = round(float((cpt[1] + cpt[2]) / cpt.sum() * 100), 1)
        out[nom]['semaines'] = int(cpt.sum())
    # plus haut OU plus bas de la semaine un mardi ou un mercredi
    return out


# ------------------------------------------------------------------ T2
def t2(jd, horaire):
    trades = []
    for p, d in jd.groupby('paire'):
        d = d.reset_index(drop=True)
        wd = d.date.dt.weekday.to_numpy()
        pp = pip(p)
        for i in range(len(d) - 4):
            if wd[i] != 0 or wd[i + 1] != 1:
                continue
            o, h, l, c = d.open.iat[i], d.high.iat[i], d.low.iat[i], d.close.iat[i]
            o2, h2, l2, c2 = d.open.iat[i + 1], d.high.iat[i + 1], d.low.iat[i + 1], d.close.iat[i + 1]
            rng = h - l
            if rng <= 0:
                continue
            plein = abs(c - o) >= 0.6 * rng
            for sens in (-1, 1):
                if sens < 0:   # vente : lundi haussier plein, clôture dans le quart haut ; mardi rouge sous clôture lundi
                    ok = plein and c > o and c >= h - 0.25 * rng and c2 < o2 and c2 < c
                    depasse = h2 > h
                    sl, tp = h2 + 2 * pp, l
                else:
                    ok = plein and c < o and c <= l + 0.25 * rng and c2 > o2 and c2 > c
                    depasse = l2 < l
                    sl, tp = l2 - 2 * pp, h
                if not ok:
                    continue
                entree = c2
                dist, risque = (entree - tp) * sens * -1, abs(entree - sl)
                if dist <= 0 or risque <= 0:
                    continue
                filtre = dist >= 60 * pp and dist / risque >= 1.2
                # fin : vendredi de la même semaine
                fin = i + 1
                while fin + 1 < len(d) and wd[fin + 1] > wd[fin]:
                    fin += 1
                r, issue = simuler_jours(d, i + 2, fin, sens, entree, sl, tp, p)
                # session du plus haut / plus bas du mardi (horaire, 2024-2026)
                londres = None
                hh = horaire.get(p)
                if hh is not None:
                    jour = d.date.iat[i + 1]
                    x = hh[(hh.date >= jour) & (hh.date < jour + pd.Timedelta(days=1))]
                    if len(x) >= 12:
                        k = x.high.idxmax() if sens < 0 else x.low.idxmin()
                        londres = int(7 <= x.loc[k, 'date'].hour < 16)
                trades.append(dict(test='T2', paire=p, date=str(d.date.iat[i + 2].date()), sens=sens, entree=entree,
                                   sl=sl, tp=tp, dist_pips=round(dist / pp, 1), rr=round(dist / risque, 2),
                                   filtre=int(filtre), depasse=int(depasse), londres=londres, r=r, issue=issue))
    t = pd.DataFrame(trades)
    f = t[t.filtre == 1]
    ans = (pd.to_datetime(t.date).dt.year.max() - pd.to_datetime(t.date).dt.year.min() + 1)
    out = {'toutes_configurations': resume(t.to_dict('records')),
           'avec_filtre_60_pips_rr_1_2': resume(f.to_dict('records')),
           'filtre_et_mardi_depasse_lundi': resume(f[f.depasse == 1].to_dict('records')),
           'filtre_et_extreme_mardi_a_londres_2024_2026': resume(f[f.londres == 1].to_dict('records')),
           'filtre_et_extreme_mardi_hors_londres_2024_2026': resume(f[f.londres == 0].to_dict('records')),
           'par_paire_filtre': {p: resume(g.to_dict('records')) for p, g in f.groupby('paire')},
           'par_annee_filtre': {str(a): resume(g.to_dict('records')) for a, g in f.groupby(pd.to_datetime(f.date).dt.year)},
           'setups_par_mois_et_par_paire': round(len(f) / ans / 12 / t.paire.nunique(), 2)}
    return out, trades


# ------------------------------------------------------------------ T3
def t3(jd):
    trades = []
    for p, d in jd.groupby('paire'):
        d = d.reset_index(drop=True)
        wd = d.date.dt.weekday.to_numpy()
        pp = pip(p)
        for i in range(len(d) - 3):
            if not (wd[i] == 0 and wd[i + 1] == 1 and wd[i + 2] == 2):
                continue
            if not (d.close.iat[i] > d.open.iat[i] and d.close.iat[i + 1] > d.open.iat[i + 1]):
                continue
            hm = d.high.iat[i + 1]
            if d.high.iat[i + 2] <= hm:
                continue
            entree, sl, tp = hm, hm + 20 * pp, hm - 60 * pp
            # mercredi : le prix a dépassé le plus haut du mardi (entrée) ; ordre intrajournalier inconnu
            fin = i + 2
            while fin + 1 < len(d) and wd[fin + 1] > wd[fin]:
                fin += 1
            r, issue = simuler_jours(d, i + 2, fin, -1, entree, sl, tp, p)
            trades.append(dict(test='T3', paire=p, date=str(d.date.iat[i + 2].date()), sens=-1, entree=entree, sl=sl,
                               tp=tp, r=r, issue=issue))
    t = pd.DataFrame(trades)
    recent = t[pd.to_datetime(t.date) >= '2021-03-01']
    return {'2010_2026': resume(trades), '5_dernieres_annees': resume(recent.to_dict('records')),
            '5_dernieres_annees_par_paire': {p: resume(g.to_dict('records')) for p, g in recent.groupby('paire')},
            'EURUSD_5_ans': resume(recent[recent.paire == 'EURUSD'].to_dict('records'))}, trades


# ------------------------------------------------------------------ T4
def t4(jd):
    out = {}
    for p in ['AUDJPY', 'EURUSD', 'GBPUSD', 'USDJPY']:
        d = jd[jd.paire == p].copy()
        d['mois'] = d.date.dt.to_period('M')
        lignes = []
        for m, g in d.groupby('mois'):
            if len(g) < 15:
                continue
            j = g.low.idxmin()
            lignes.append(dict(an=m.year, mois=m.month, semaine1=int(g.loc[j, 'date'].day <= 7),
                               repli=(g.open.iloc[0] - g.low.min()) / pip(p), hausse=int(g.close.iloc[-1] > g.open.iloc[0])))
        x = pd.DataFrame(lignes)
        avr = x[(x.mois == 4) & (x.an.between(2015, 2024))]
        out[p] = {'avril_2015_2024_plus_bas_en_semaine_1_pct': round(float(avr.semaine1.mean() * 100), 1),
                  'avril_2015_2024_repli_moyen_pips': round(float(avr.repli.mean()), 1),
                  'avril_2015_2024_mois_haussiers_pct': round(float(avr.hausse.mean() * 100), 1),
                  'tous_mois_plus_bas_en_semaine_1_pct': round(float(x.semaine1.mean() * 100), 1),
                  'mois_haussiers_plus_bas_en_semaine_1_pct': round(float(x[x.hausse == 1].semaine1.mean() * 100), 1)}
    return out


# ------------------------------------------------------------------ T5
def t5(jd):
    trades = []
    for p, d in jd.groupby('paire'):
        if p == 'XAUUSD':
            continue
        d = d.reset_index(drop=True)
        pp = pip(p)
        pas = 250 * pp
        dernier = -10
        for i in range(5, len(d) - 1):
            # arrivée sur un MLQ : la bougie touche un niveau de 250 pips alors que la veille en était à plus de 50 pips
            for sens in (-1, 1):
                niv = (np.floor(d.high.iat[i] / pas) * pas) if sens < 0 else (np.ceil(d.low.iat[i] / pas) * pas)
                if sens < 0 and not (d.high.iat[i] >= niv - 25 * pp and d.close.iat[i - 1] < niv - 50 * pp):
                    continue
                if sens > 0 and not (d.low.iat[i] <= niv + 25 * pp and d.close.iat[i - 1] > niv + 50 * pp):
                    continue
                if i - dernier < 3:
                    continue
                dernier = i
                entree = niv - sens * 25 * pp            # limite au bord de la zone de ±25 pips
                sl = entree - sens * 50 * pp
                tp = entree + sens * 250 * pp
                r, issue = simuler_jours(d, i, min(i + 30, len(d) - 1), sens, entree, sl, tp, p)
                trades.append(dict(test='T5', paire=p, date=str(d.date.iat[i].date()), sens=sens, entree=entree,
                                   sl=sl, tp=tp, r=r, issue=issue))
    t = pd.DataFrame(trades)
    return {'tous': resume(trades), 'seuil_rentabilite_pct': 16.7,
            'par_annee': {str(a): resume(g.to_dict('records')) for a, g in t.groupby(pd.to_datetime(t.date).dt.year)}}, trades


# ------------------------------------------------------------------ T7, T8
def t7(jd):
    r = jd.pivot_table(index='date', columns='paire', values='close').pct_change()
    c = r[['AUDUSD', 'NZDUSD']].dropna()
    par_an = c.groupby(c.index.year).apply(lambda x: x.AUDUSD.corr(x.NZDUSD))
    return {'correlation_2010_2026': round(float(c.AUDUSD.corr(c.NZDUSD)), 3),
            'par_annee': {str(k): round(float(v), 3) for k, v in par_an.items()}}


def t8(jd):
    lignes = []
    for p, d in jd.groupby('paire'):
        d = d.reset_index(drop=True)
        h, l, c = d.high.to_numpy(), d.low.to_numpy(), d.close.to_numpy()
        atr = pd.Series(h - l).rolling(20).mean().to_numpy()
        for i in range(25, len(d) - 5):
            hr, lr = h[i - 5:i].max(), l[i - 5:i].min()
            etroit = (hr - lr) <= 1.5 * atr[i - 1]     # 5 jours dans un range de 1,5 ATR : consolidation
            if c[i] > hr:
                s = 1
            elif c[i] < lr:
                s = -1
            else:
                continue
            # expansion : le prix avance d'1 ATR dans le sens de la cassure avant de revenir au milieu du range
            cible, retour = c[i] + s * atr[i], (hr + lr) / 2
            res = 0
            for j in range(i + 1, i + 6):
                if (s > 0 and l[j] <= retour) or (s < 0 and h[j] >= retour):
                    res = -1
                    break
                if (s > 0 and h[j] >= cible) or (s < 0 and l[j] <= cible):
                    res = 1
                    break
            lignes.append(dict(paire=p, etroit=int(etroit), res=res))
    x = pd.DataFrame(lignes)
    out = {}
    for e, g in x.groupby('etroit'):
        out['apres_consolidation' if e else 'cassure_ordinaire'] = {
            'n': int(len(g)), 'expansion_pct': round(float((g.res == 1).mean() * 100), 1),
            'retour_au_milieu_pct': round(float((g.res == -1).mean() * 100), 1)}
    return out


def main():
    jd = dk.charger()
    horaire = {}
    for p in jd.paire.unique():
        try:
            hh = prix_yahoo._charger(p, '1h').copy()
            hh['date'] = pd.to_datetime(hh.date)
            horaire[p] = hh.reset_index(drop=True)
        except Exception:
            pass
    res, toutes = {}, []
    res['T1_jour_du_plus_haut_et_du_plus_bas'] = t1(jd)
    res['T2_trois_barres'], tr = t2(jd, horaire)
    toutes += tr
    res['T3_lundi_mardi_haussiers_mercredi'], tr = t3(jd)
    toutes += tr
    res['T4_mois_plus_bas_semaine_1'] = t4(jd)
    res['T5_mlq_250'], tr = t5(jd)
    toutes += tr
    res['T6_bebe_abandonne'] = 'voir scripts/tester_bebe_abandonne.py (définition corrigée, horaire et journalier)'
    res['T7_correlation_audusd_nzdusd'] = t7(jd)
    res['T8_consolidation_expansion'] = t8(jd)
    res['periode'] = f"{jd.date.min().date()} -> {jd.date.max().date()}, {jd.paire.nunique()} paires"
    json.dump(res, open('data/masterclass_resultats.json', 'w'), indent=1, ensure_ascii=False)
    pd.DataFrame(toutes).to_csv('data/masterclass_trades.csv', index=False)
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == '__main__':
    main()
