#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
La checklist du « SETUP A+ WEEKLY CYCLE » du playbook Notion d'Amirou (data/playbook_notion/playbook.txt), traduite
en règles fixées avant le test, puis rejouée sur les cours.

Règles (achat ; la vente est symétrique, prix inversés) — le jour J, avec ce qui est connu à la clôture de J-1 :
 1. orderflow weekly : la dernière semaine terminée clôture au-dessus de la clôture d'il y a 4 semaines ;
    orderflow daily : clôture de J-1 au-dessus de sa moyenne sur 20 jours ;
 2. premium/discount daily : l'entrée est dans la moitié basse (discount) du range des 20 derniers jours ;
 3. weekly open (PO3) : l'entrée est sous l'ouverture de la semaine en cours ;
 4. cible : plus haut de la semaine précédente, à 300 pips au plus de l'entrée ;
 5. entrée sur un FVG daily haussier (plus haut de k-2 < plus bas de k) formé dans les 20 derniers jours, pas encore
    comblé, sous le prix ; le prix revient dedans pendant J ;
 6. OTE : le FVG chevauche la zone de 62 % à 79 % de retracement de la dernière jambe haussière (plus bas des
    20 derniers jours -> plus haut atteint depuis) ;
 7. confirmation en H1 dans une killzone (Londres 07h-10h, New York 12h-15h UTC) : après que le prix a touché le FVG
    pendant J sans clôturer sous son bas, une bougie H1 de la killzone clôture haussière au-dessus du haut du FVG ;
    entrée à cette clôture ;
 8. stop sous le bas du FVG et le plus bas du jour (2 pips de marge), à 50 pips au minimum ;
 9. objectif : la cible du point 4 ; ratio d'au moins 1:3 (playbook) ; sortie au plus tard après 10 jours de bourse.
Un seul trade par FVG. Dans une même heure, le stop passe avant l'objectif ; spread déduit.

Le déclencheur de base (points 5, 7, 8, avec la cible du point 4 au-dessus de l'entrée) sert de témoin ; chaque
trade note quels autres critères (1, 2, 3, 4 ≤ 300 pips, 6, 9 ratio ≥ 3) sont remplis. On compare :
« checklist complète », « base sans les filtres », et la checklist privée d'un critère à la fois.

Deux rejeux :
- horaire Yahoo, 22 paires, 2024-2026 (toute la checklist) ;
- journalier Dukascopy, 10 paires, 2012-2026 (sans le point 7 : entrée par ordre limite au haut du FVG ; si le jour
  d'entrée touche le stop, la perte compte).
Sortie : data/checklist_a_plus/{horaire,journalier}.csv, resultats.csv
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO, charger  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

SORTIE = 'data/checklist_a_plus'
CRITERES = ['orderflow_w', 'orderflow_d', 'discount', 'sous_weekly_open', 'cible_300', 'ote', 'ratio_3']
KILLZONES = {7, 8, 9, 12, 13, 14}
TENUE_JOURS = 10


def contexte_jour(d, i, s):
    """d : journalier en repère achat (colonnes o h l c, semaine, mois). Renvoie le contexte connu au début du jour i,
    ou None. s ne sert qu'à l'historique (déjà inversé)."""
    if i < 25:
        return None
    o, h, l, c = d['o'].to_numpy(), d['h'].to_numpy(), d['l'].to_numpy(), d['c'].to_numpy()
    sem = d['semaine'].to_numpy()
    semaines = pd.unique(sem[:i])
    if len(semaines) < 6:
        return None
    s_cour = sem[i]
    passees = [w for w in semaines if w != s_cour]
    if len(passees) < 5:
        return None
    m_w = {w: np.where(sem == w)[0] for w in passees[-5:]}
    cl_w = [c[m_w[w][-1]] for w in passees[-5:]]
    prev = m_w[passees[-1]]
    i_semaine = np.where(sem == s_cour)[0][0]
    # FVG haussier le plus récent, pas comblé, sous le prix
    fvg = None
    for k in range(i - 1, i - 21, -1):
        if k < 2:
            break
        bas, haut = h[k - 2], l[k]
        if haut <= bas:
            continue
        apres = l[k + 1:i]
        if len(apres) and apres.min() <= bas:          # comblé
            continue
        if c[i - 1] <= haut:                            # le prix doit être au-dessus du FVG
            continue
        fvg = (bas, haut, k)
        break
    if fvg is None:
        return None
    # OTE de la dernière jambe : plus bas des 20 jours -> plus haut depuis
    j0 = i - 20 + int(np.argmin(l[i - 20:i]))
    hh = h[j0:i].max()
    ll = l[j0]
    ote_bas, ote_haut = hh - 0.79 * (hh - ll), hh - 0.62 * (hh - ll)
    r20h, r20l = h[i - 20:i].max(), l[i - 20:i].min()
    return dict(fvg_bas=fvg[0], fvg_haut=fvg[1], fvg_jour=fvg[2],
                orderflow_w=cl_w[-1] > cl_w[0], orderflow_d=c[i - 1] > c[i - 20:i].mean(),
                milieu_20j=(r20h + r20l) / 2, weekly_open=o[i_semaine], cible=h[prev].max(),
                ote=(fvg[0] <= ote_haut) and (fvg[1] >= ote_bas))


def journalier_depuis_horaire(h):
    g = h.groupby('jour')
    return pd.DataFrame({'jour': list(g.groups), 'o': g['open'].first().to_numpy(), 'h': g['high'].max().to_numpy(),
                         'l': g['low'].min().to_numpy(), 'c': g['close'].last().to_numpy(), 'n': g.size().to_numpy()})


def ajouter_calendrier(d, col):
    dt = pd.to_datetime(d[col])
    d['semaine'] = (dt - pd.to_timedelta(dt.dt.weekday, unit='D')).dt.strftime('%Y-%m-%d')
    return d


def criteres(ctx, e, sl, pp):
    R = e - sl
    return dict(orderflow_w=bool(ctx['orderflow_w']), orderflow_d=bool(ctx['orderflow_d']),
                discount=bool(e < ctx['milieu_20j']), sous_weekly_open=bool(e < ctx['weekly_open']),
                cible_300=bool(ctx['cible'] - e <= 300 * pp), ote=bool(ctx['ote']),
                ratio_3=bool(ctx['cible'] - e >= 3 * R))


def suivre(H, L, C, k0, k1, e, sl, tp):
    for k in range(k0, min(k1, len(C) - 1) + 1):
        if L[k] <= sl:
            return -1.0, 'stop', k
        if H[k] >= tp:
            return (tp - e) / (e - sl), 'objectif', k
    k = min(k1, len(C) - 1)
    if k1 > len(C) - 1:
        return np.nan, 'en cours', k
    return (C[k] - e) / (e - sl), 'échéance', k


def horaire():
    lignes = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if not os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            continue
        h0 = charger(p)
        pp, sp = pip(p), spread(p)
        heure = h0['date'].dt.hour.to_numpy()
        dates = h0['date'].dt.strftime('%Y-%m-%d %H:%M').to_numpy()
        jour_h = h0['jour'].to_numpy()
        for s in (1, -1):
            O, H, L, C = ((h0['open'], h0['high'], h0['low'], h0['close']) if s > 0 else
                          (-h0['open'], -h0['low'], -h0['high'], -h0['close']))
            O, H, L, C = (x.to_numpy() for x in (O, H, L, C))
            h = pd.DataFrame({'jour': jour_h, 'open': O, 'high': H, 'low': L, 'close': C})
            d = ajouter_calendrier(journalier_depuis_horaire(h), 'jour')
            idx = {j: np.where(jour_h == j)[0] for j in d['jour']}
            utilises = set()                               # un seul trade par FVG
            for i in range(25, len(d)):
                if d['n'][i] < 18:
                    continue
                ctx = contexte_jour(d, i, s)
                if ctx is None or ctx['fvg_jour'] in utilises:
                    continue
                fb, fh = ctx['fvg_bas'], ctx['fvg_haut']
                touche, bas_jour = False, np.inf
                for k in idx[d['jour'][i]]:
                    bas_jour = min(bas_jour, L[k])
                    if C[k] < fb:                          # FVG invalidé
                        break
                    if L[k] <= fh:
                        touche = True
                    if touche and heure[k] in KILLZONES and C[k] > O[k] and C[k] > fh:
                        e = C[k]
                        sl = min(fb, bas_jour) - 2 * pp
                        sl = min(sl, e - 50 * pp)
                        tp = ctx['cible']
                        if tp <= e:
                            break
                        fin_jour = d['jour'][min(i + TENUE_JOURS, len(d) - 1)]
                        k1 = idx[fin_jour][-1] if i + TENUE_JOURS < len(d) else len(C)
                        r, motif, ks = suivre(H, L, C, k + 1, k1, e, sl, tp)
                        utilises.add(ctx['fvg_jour'])
                        R = e - sl
                        lignes.append(dict(rejeu='horaire 22 paires 2024-2026', paire=p,
                                           sens='achat' if s > 0 else 'vente', entree_date_heure=dates[k],
                                           entree=round(e * s, 5), stop=round(sl * s, 5), objectif=round(tp * s, 5),
                                           risque_pips=round(R / pp, 1), ratio=round((tp - e) / R, 2),
                                           sortie_date_heure=dates[ks], motif=motif,
                                           r=round(r - sp / R, 3) if not np.isnan(r) else np.nan,
                                           **criteres(ctx, e, sl, pp)))
                        break
    return pd.DataFrame(lignes)


def journalier():
    jd = pd.read_csv('data/prix/journalier_dukascopy.csv')
    lignes = []
    for p, d0 in jd[jd['paire'] != 'XAUUSD'].groupby('paire'):
        d0 = d0.reset_index(drop=True)
        pp, sp = pip(p), spread(p)
        for s in (1, -1):
            d = pd.DataFrame({'date': d0['date'],
                              'o': d0['open'] * s, 'h': (d0['high'] if s > 0 else d0['low']) * s,
                              'l': (d0['low'] if s > 0 else d0['high']) * s, 'c': d0['close'] * s})
            d = ajouter_calendrier(d, 'date')
            H, L, C = d['h'].to_numpy(), d['l'].to_numpy(), d['c'].to_numpy()
            utilises = set()
            for i in range(25, len(d)):
                ctx = contexte_jour(d, i, s)
                if ctx is None or L[i] > ctx['fvg_haut'] or ctx['fvg_jour'] in utilises:
                    continue
                utilises.add(ctx['fvg_jour'])
                e = min(ctx['fvg_haut'], d['o'][i])
                sl = min(ctx['fvg_bas'] - 2 * pp, e - 50 * pp)
                tp = ctx['cible']
                if tp <= e:
                    continue
                R = e - sl
                if L[i] <= sl:
                    r, motif, ks = -1.0, 'stop', i
                else:
                    k1 = i + TENUE_JOURS if i + TENUE_JOURS < len(d) else len(C)
                    r, motif, ks = suivre(H, L, C, i + 1, k1, e, sl, tp)
                lignes.append(dict(rejeu='journalier 10 paires 2012-2026', paire=p, sens='achat' if s > 0 else 'vente',
                                   entree_date_heure=d['date'][i], entree=round(e * s, 5), stop=round(sl * s, 5),
                                   objectif=round(tp * s, 5), risque_pips=round(R / pp, 1), ratio=round((tp - e) / R, 2),
                                   sortie_date_heure=d['date'][ks], motif=motif,
                                   r=round(r - sp / R, 3) if not np.isnan(r) else np.nan, **criteres(ctx, e, sl, pp)))
    return pd.DataFrame(lignes)


def bilan(x):
    x = x.dropna(subset=['r'])
    n = len(x)
    return dict(trades=n, gagnants=round((x['r'] > 0).mean(), 3) if n else np.nan,
                r_moyen=round(x['r'].mean(), 3) if n else np.nan,
                erreur_type=round(x['r'].std() / np.sqrt(n), 3) if n > 1 else np.nan,
                ratio_moyen=round(x['ratio'].mean(), 2) if n else np.nan,
                trades_par_an_et_paire=np.nan)


def main():
    os.makedirs(SORTIE, exist_ok=True)
    res = []
    for nom, f in [('horaire', horaire), ('journalier', journalier)]:
        t = f()
        t.to_csv(f'{SORTIE}/{nom}.csv', index=False)
        periodes = [('2024-2026', t)] if nom == 'horaire' else [
            ('2012-2019', t[t['entree_date_heure'] < '2020']), ('2020-2026', t[t['entree_date_heure'] >= '2020'])]
        annees = {'horaire': 2.8, 'journalier': None}
        for per, x in periodes:
            tout = np.ones(len(x), bool)
            groupes = {'checklist complète': x[CRITERES].all(axis=1).to_numpy(),
                       'base sans filtre (témoin)': tout}
            for c in CRITERES:
                autres = [k for k in CRITERES if k != c]
                groupes[f'checklist sans « {c} »'] = x[autres].all(axis=1).to_numpy()
            for c in CRITERES:
                groupes[f'base + « {c} » seul'] = x[c].to_numpy()
            for g, m in groupes.items():
                b = bilan(x[m])
                nb_paires = x['paire'].nunique()
                ans = annees[nom] or (8 if per == '2012-2019' else 6.8)
                b['trades_par_an_et_paire'] = round(b['trades'] / ans / max(nb_paires, 1), 1)
                res.append(dict(rejeu=x['rejeu'].iat[0] if len(x) else nom, periode=per, groupe=g, **b))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/resultats.csv', index=False)
    pd.set_option('display.width', 220)
    print(r.to_string(index=False))


if __name__ == '__main__':
    main()
