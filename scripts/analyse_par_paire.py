#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyse chaque stratégie PAR PAIRE et PAR ANNÉE, et liste chaque occurrence datée avec son résultat.

Stratégies (fichiers produits par les scripts de test) :
- lundi-mardi-mercredi (« trois barres », filtre 60 pips et RR >= 1,2) et variante #14577 : data/masterclass_trades.csv ;
- MLQ ±25 / 50 / 250 pips : data/masterclass_trades.csv ;
- englobante des flashcards (trade de la « rupture ») : data/flashcards_englobante_detail.csv ;
- bébé abandonné (horaire et journalier) : data/bebe_abandonne_horaire.csv, data/bebe_abandonne_journalier.csv ;
- Bombe (H1) : data/bombe_trades.csv ;
- combinaisons englobante / mercredi / MLQ : data/strategie_combinee_trades.csv.

Pour chaque stratégie :
1. tableau paire x année (nombre de trades, % de gagnants, R moyen) ;
2. validation : on classe les paires sur la première moitié de la période, puis on regarde si les
   « meilleures » restent meilleures sur la seconde moitié (sinon, la préférence pour une paire est du bruit) ;
3. carte de chaleur paire x année (assets/figures/paire_<stratégie>.png) ;
4. liste des occurrences : data/par_paire/occurrences_<stratégie>.csv.

Sorties : data/par_paire/resume_paire_annee.csv, data/par_paire/validation.csv,
analyses/annexes/STRATEGIES_PAR_PAIRE_TABLEAUX.md (tableaux et listes complètes), figures.
"""

import os
import re

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

DOSSIER = 'data/par_paire'
ANNEXE = 'analyses/annexes/STRATEGIES_PAR_PAIRE_TABLEAUX.md'
JPY = ('JPY',)


def slug(t):
    t = t.lower()
    for a, b in [('é', 'e'), ('è', 'e'), ('ê', 'e'), ('à', 'a'), ('ç', 'c'), ('ô', 'o'), ('û', 'u'), ('î', 'i')]:
        t = t.replace(a, b)
    return re.sub(r'[^a-z0-9]+', '_', t).strip('_')[:40]


def strategies():
    s = {}
    if os.path.exists('data/masterclass_trades.csv'):
        m = pd.read_csv('data/masterclass_trades.csv')
        m['sens'] = m.sens.map({1: 'achat', -1: 'vente'})
        t2 = m[(m.test == 'T2') & (m.filtre == 1)]
        s['Lundi-mardi-mercredi (trois barres)'] = (t2, 'journalier', ['entree', 'sl', 'tp', 'issue', 'depasse', 'londres'])
        s['Lundi et mardi haussiers, mercredi prend le high (#14577)'] = (m[m.test == 'T3'], 'journalier',
                                                                          ['entree', 'sl', 'tp', 'issue'])
        s['MLQ ±25 / 50 / 250 pips'] = (m[m.test == 'T5'], 'journalier', ['entree', 'sl', 'tp', 'issue'])
    if os.path.exists('data/flashcards_englobante_detail.csv'):
        f = pd.read_csv('data/flashcards_englobante_detail.csv')
        f = f[f.corps == 1].rename(columns={'gain_r': 'r'})
        f['sens'] = f.sens.map({1: 'achat', -1: 'vente'})
        s['Englobante (rupture des flashcards)'] = (f, 'horaire', ['issue', 'heures', 'objectif_pips', 'stop_pips'])
    for nom, fic, res in [('Bébé abandonné (horaire)', 'data/bebe_abandonne_horaire.csv', 'horaire'),
                          ('Bébé abandonné (journalier)', 'data/bebe_abandonne_journalier.csv', 'journalier')]:
        if os.path.exists(fic):
            b = pd.read_csv(fic)
            b = b[b.meches == True].rename(columns={'1R': 'r'})  # noqa: E712
            b['sens'] = b.sens.map({1: 'achat', -1: 'vente'})
            s[nom] = (b, res, ['b4_dans_le_sens', 'risque_pips'])
    if os.path.exists('data/bombe_trades.csv'):
        b = pd.read_csv('data/bombe_trades.csv')
        b['sens'] = b.sens.map({1: 'achat', -1: 'vente'})
        s['Bombe (H1)'] = (b, 'horaire', ['entree', 'sl', 'sortie', 'risque_pips', 'duree_h'])
    if os.path.exists('data/strategie_combinee_trades.csv'):
        c = pd.read_csv('data/strategie_combinee_trades.csv', parse_dates=['date'])
        c['sens'] = c.sens.map({1: 'achat', -1: 'vente'})
        c = c.rename(columns={'2R': 'r'})
        s['Englobante du mercredi (objectif 2 R)'] = (c[c.E & (c.jour == 2)], 'journalier', ['1R', '3 jours'])
        s['Englobante + MLQ (objectif 2 R)'] = (c[c.E & c.M], 'journalier', ['1R', '3 jours'])
    return s


def coupe(annees):
    a = sorted(annees)
    return a[: len(a) // 2], a[len(a) // 2:]


def tableau(x):
    piv_r = x.pivot_table(index='paire', columns='an', values='r', aggfunc='mean')
    piv_n = x.pivot_table(index='paire', columns='an', values='r', aggfunc='size')
    lignes = ['| Paire | ' + ' | '.join(str(a) for a in piv_r.columns) + ' | **Total** | Gagnants | t |',
              '|---|' + '---|' * (len(piv_r.columns) + 3)]
    for p in piv_r.index:
        g = x[x.paire == p].r
        t = g.mean() / (g.std(ddof=1) / np.sqrt(len(g))) if len(g) >= 5 and g.std() > 0 else np.nan
        cells = [f"{piv_r.at[p, a]:+.2f} ({int(piv_n.at[p, a])})" if not np.isnan(piv_r.at[p, a]) else '' for a in piv_r.columns]
        lignes.append(f"| {p} | " + ' | '.join(cells) + f" | **{g.mean():+.2f} ({len(g)})** | {(g > 0).mean() * 100:.0f} % | {'—' if np.isnan(t) else f'{t:+.1f}'} |")
    tot = x.groupby('an').r
    lignes.append('| **Toutes** | ' + ' | '.join(f"{tot.mean()[a]:+.2f} ({tot.size()[a]})" for a in piv_r.columns) +
                  f" | **{x.r.mean():+.2f} ({len(x)})** | {(x.r > 0).mean() * 100:.0f} % | |")
    return '\n'.join(lignes), piv_r


def carte(piv, nom, fichier):
    fig, ax = plt.subplots(figsize=(1.2 + 0.7 * len(piv.columns), 0.9 + 0.35 * len(piv)))
    v = np.nanmax(np.abs(piv.values)) if np.isfinite(piv.values).any() else 1
    v = min(v, 1.5)
    im = ax.imshow(piv.values, cmap='RdYlGn', vmin=-v, vmax=v, aspect='auto')
    ax.set_xticks(range(len(piv.columns)), piv.columns, rotation=45)
    ax.set_yticks(range(len(piv)), piv.index)
    for i in range(piv.shape[0]):
        for j in range(piv.shape[1]):
            if np.isfinite(piv.values[i, j]):
                ax.text(j, i, f'{piv.values[i, j]:+.1f}', ha='center', va='center', fontsize=6.5)
    fig.colorbar(im, ax=ax, label='R moyen par trade')
    ax.set_title(f'{nom} : R moyen par paire et par année', fontsize=10)
    fig.tight_layout()
    fig.savefig(fichier, facecolor='white', dpi=110)
    plt.close(fig)


def main():
    os.makedirs(DOSSIER, exist_ok=True)
    os.makedirs(os.path.dirname(ANNEXE), exist_ok=True)
    resume, valid, md = [], [], ['# Annexe : stratégies par paire et par année (tableaux complets)\n',
                                  '> Généré par [`scripts/analyse_par_paire.py`](../../scripts/analyse_par_paire.py). '
                                  'Cellule = R moyen par trade (nombre de trades). Spread déduit. Les listes complètes '
                                  'des occurrences datées sont dans [`data/par_paire/`](../../data/par_paire/).\n']
    for nom, (x, res, cols) in strategies().items():
        x = x.copy()
        x['date'] = pd.to_datetime(x.date)
        x['an'] = x.date.dt.year
        x = x.dropna(subset=['r'])
        sl = slug(nom)
        garder = ['date', 'paire', 'sens'] + [c for c in cols if c in x.columns] + ['r']
        x.sort_values('date')[garder].to_csv(f'{DOSSIER}/occurrences_{sl}.csv', index=False, float_format='%.5f')
        g = x.groupby(['paire', 'an']).r
        resume.append(pd.DataFrame({'strategie': nom, 'n': g.size(), 'gagnants_pct': (g.apply(lambda r: (r > 0).mean() * 100)).round(1),
                                    'r_moyen': g.mean().round(3)}).reset_index())
        tab, piv = tableau(x)
        carte(piv, nom, f'assets/figures/paire_{sl}.png')
        # validation première moitié -> seconde moitié
        a1, a2 = coupe(x.an.unique())
        p1 = x[x.an.isin(a1)].groupby('paire').r.agg(['mean', 'size'])
        p2 = x[x.an.isin(a2)].groupby('paire').r.agg(['mean', 'size'])
        both = p1.join(p2, lsuffix='_1', rsuffix='_2').dropna()
        both = both[(both.size_1 >= 5) & (both.size_2 >= 5)]
        if len(both) >= 4:
            corr = both.mean_1.corr(both.mean_2, method='spearman')
            top = both.sort_values('mean_1', ascending=False).head(max(2, len(both) // 3))
            reste = both.drop(top.index)
            v = dict(strategie=nom, periode_1=f'{min(a1)}-{max(a1)}', periode_2=f'{min(a2)}-{max(a2)}',
                     correlation_rangs=round(corr, 2), meilleures_paires_p1=', '.join(top.index),
                     leur_r_p2=round((top.mean_2 * top.size_2).sum() / top.size_2.sum(), 3),
                     autres_r_p2=round((reste.mean_2 * reste.size_2).sum() / reste.size_2.sum(), 3) if len(reste) else np.nan)
            valid.append(v)
        jpy = x[x.paire.str.contains('JPY')].r
        autres = x[~x.paire.str.contains('JPY')].r
        md += [f'\n## {nom}\n', f'![{nom}](../../assets/figures/paire_{sl}.png)\n', tab, '',
               f"Paires en yen : {jpy.mean():+.2f} R ({len(jpy)} trades) ; autres paires : {autres.mean():+.2f} R ({len(autres)} trades).",
               f"Liste datée : [`data/par_paire/occurrences_{sl}.csv`](../../data/par_paire/occurrences_{sl}.csv)."]
        if valid and valid[-1]['strategie'] == nom:
            v = valid[-1]
            md.append(f"Validation : meilleures paires sur {v['periode_1']} = {v['meilleures_paires_p1']} ; sur {v['periode_2']}, "
                      f"elles font {v['leur_r_p2']:+.2f} R contre {v['autres_r_p2']:+.2f} R pour les autres "
                      f"(corrélation des classements : {v['correlation_rangs']:+.2f}).")
        print(f"{nom}: {len(x)} trades, {x.r.mean():+.3f} R", flush=True)
    pd.concat(resume).to_csv(f'{DOSSIER}/resume_paire_annee.csv', index=False)
    pd.DataFrame(valid).to_csv(f'{DOSSIER}/validation.csv', index=False)
    open(ANNEXE, 'w').write('\n'.join(md) + '\n')
    print(pd.DataFrame(valid).to_string())


if __name__ == '__main__':
    main()
