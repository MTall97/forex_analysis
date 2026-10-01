#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figures des rapports d'analyse (assets/figures/*.png).

Schémas (stratégies) :
- schema_englobante.png   : l'englobante baissière, la « rupture », l'objectif et le stop ;
- schema_fvg.png          : pourquoi le FVG « du lendemain » voit la rupture avant de la prédire ;
- schema_mlq.png          : zones de 1 000 pips découpées en MLQ de 250 pips, sur l'EURUSD réel.

Résultats :
- flashcards_cartes_vs_mesure.png, flashcards_reussite_vs_gain.png, flashcards_duree.png ;
- amirou_duree_tp.png, amirou_jours_mlq.png ;
- epoques_style.png, epoques_courbes.png ;
- septembres_bilan.png, septembres_tp_sl_canal.png, septembre_2026_eurusd.png ;
- saison_eurusd_heatmap.png, saison_affirmations.png, saison_reussite_causes.png, saison_hors_saison.png ;
- strategie_concepts.png, strategie_captures.png, strategie_algos.png ;
- fond_test_a.png, fond_tests_b_c.png ; verification_taux.png, stockage_photos.png ;
- algos_carry_momentum.png, algos_intraday_profil.png.

Données : data/flashcards_englobante*.csv (scripts/tester_flashcards_englobante.py),
data/epoques_trades.csv (scripts/analyse_par_epoque.py), data/trades_simules.csv, cache Yahoo.
Usage : python scripts/figures_rapports.py
"""

import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402

SORTIE = 'assets/figures'
VERT, ROUGE, GRIS, BLEU, ORANGE = '#26a69a', '#ef5350', '#9e9e9e', '#1e88e5', '#fb8c00'
plt.rcParams.update({'figure.dpi': 110, 'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})


def bougie(ax, x, o, h, l, c, largeur=0.6, alpha=1.0):
    coul = VERT if c >= o else ROUGE
    ax.plot([x, x], [l, h], color=coul, lw=1.4, alpha=alpha, zorder=2)
    ax.add_patch(Rectangle((x - largeur / 2, min(o, c)), largeur, abs(c - o) or 0.02, color=coul, alpha=alpha, zorder=3))


def sauver(fig, nom):
    fig.tight_layout()
    fig.savefig(f'{SORTIE}/{nom}', bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print('  ', nom)


# ------------------------------------------------------------------ schémas
def schema_englobante():
    fig, ax = plt.subplots(figsize=(8, 4.6))
    bougies = [(0, 10, 10.8, 9.7, 10.5), (1, 10.5, 11.6, 10.3, 11.3), (2, 11.3, 12.3, 11.1, 12.0),
               (3, 12.05, 12.6, 10.9, 11.05)]
    for b in bougies:
        bougie(ax, *b)
    suite = [(4, 11.05, 11.3, 10.6, 10.75), (5, 10.75, 11.0, 10.2, 10.4), (6, 10.4, 10.9, 10.1, 10.8)]
    for b in suite:
        bougie(ax, *b, alpha=0.45)
    ax.axhline(10.9, xmin=0.42, xmax=0.98, color=VERT, ls='--', lw=1.2)
    ax.axhline(12.6, xmin=0.42, xmax=0.98, color=ROUGE, ls='--', lw=1.2)
    ax.axhline(11.05, xmin=0.42, xmax=0.98, color=GRIS, ls=':', lw=1.2)
    ax.annotate('', xy=(6.6, 10.9), xytext=(6.6, 11.05), arrowprops=dict(arrowstyle='<->', color=VERT))
    ax.annotate('', xy=(7.0, 12.6), xytext=(7.0, 11.05), arrowprops=dict(arrowstyle='<->', color=ROUGE))
    ax.text(6.7, 10.97, 'objectif ≈ 10-35 pips', color=VERT, va='center', fontsize=9)
    ax.text(7.1, 11.8, 'stop ≈ 40-130 pips', color=ROUGE, va='center', fontsize=9)
    ax.text(3.35, 12.62, 'stop : plus haut\nde l\'englobante', color=ROUGE, fontsize=8, va='bottom')
    ax.text(3.35, 10.65, 'cible : cassure du plus bas\n(« rupture »)', color=VERT, fontsize=8, va='top')
    ax.text(3.35, 11.1, 'entrée : clôture', color='#555', fontsize=8, va='bottom')
    ax.annotate('englobante baissière :\nson corps recouvre\ncelui de la veille', xy=(3, 11.8), xytext=(0.2, 12.5),
                fontsize=9, arrowprops=dict(arrowstyle='->', color='#555'))
    ax.text(5, 9.75, 'jours 1 à 3 : le plus bas est cassé\n81 % des fois (carte : 71-83 %)\n…et 79 % après N\'IMPORTE QUELLE bougie',
            ha='center', fontsize=9, color='#333')
    ax.set_xlim(-0.6, 9.2)
    ax.set_ylim(9.4, 13.1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Stratégie des flashcards : la « rupture » d\'une englobante en 3 jours', fontsize=11)
    sauver(fig, 'schema_englobante.png')


def schema_fvg():
    fig, ax = plt.subplots(figsize=(8, 4.4))
    bougie(ax, 0, 11.0, 11.8, 10.9, 11.6)          # veille (haussière)
    bougie(ax, 1, 11.6, 11.7, 10.6, 10.75)         # englobante baissière
    bougie(ax, 2, 10.75, 10.85, 9.9, 10.05)        # lendemain : FVG + rupture
    ax.add_patch(Rectangle((-0.3, 10.85), 2.6, 0.05, color=ORANGE, alpha=0.6))
    ax.add_patch(Rectangle((-0.3, 10.85), 2.6, 10.9 - 10.85, color=ORANGE, alpha=0.6))
    ax.fill_between([-0.3, 2.3], 10.85, 10.9, color=ORANGE, alpha=0.5)
    ax.axhline(10.6, xmin=0.25, xmax=0.95, color=VERT, ls='--', lw=1.2)
    ax.text(2.45, 10.6, 'plus bas de l\'englobante\n= cible de la « rupture »', color=VERT, va='center', fontsize=9)
    ax.text(2.45, 10.88, 'FVG : trou entre le plus bas de la veille\net le plus haut du lendemain', color=ORANGE,
            va='center', fontsize=9)
    ax.annotate('pour créer le FVG, le lendemain doit\ndescendre franchement… et il casse\ndéjà la cible (plus de 8 fois sur 10)',
                xy=(2, 10.0), xytext=(2.45, 9.75), fontsize=9, arrowprops=dict(arrowstyle='->', color='#555'))
    for x, t in [(0, 'veille'), (1, 'englobante'), (2, 'lendemain')]:
        ax.text(x, 9.55, t, ha='center', fontsize=8, color='#555')
    ax.set_xlim(-0.7, 5.6)
    ax.set_ylim(9.4, 12.0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title('Variante « + FVG » : le FVG du lendemain arrive APRÈS la rupture', fontsize=11)
    sauver(fig, 'schema_fvg.png')


def schema_mlq():
    hh = prix_yahoo._charger('EURUSD', '1h')
    d = hh.set_index('date').close.resample('D').last().dropna()
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(d.index, d.values, color='#37474f', lw=1)
    bas, haut = np.floor(d.min() / 0.025) * 0.025, np.ceil(d.max() / 0.025) * 0.025
    for niv in np.arange(bas, haut + 1e-9, 0.025):
        majeur = abs(niv / 0.1 - round(niv / 0.1)) < 1e-6
        ax.axhline(niv, color=BLEU if majeur else ORANGE, lw=1.6 if majeur else 1, ls='-' if majeur else '--', alpha=0.8)
        ax.text(d.index[-1] + pd.Timedelta(days=8), niv, f'{niv:.5f}' + ('  zone de 1 000 pips' if majeur else '  MLQ'),
                va='center', fontsize=8, color=BLEU if majeur else ORANGE)
    ax.set_title('Les MLQ d\'Amirou : zones de 1 000 pips (bleu) découpées en quarts de 250 pips (orange), EURUSD', fontsize=10)
    ax.set_ylabel('EURUSD (clôture quotidienne)')
    ax.set_xlim(d.index[0], d.index[-1] + pd.Timedelta(days=120))
    sauver(fig, 'schema_mlq.png')


# ------------------------------------------------------------------ résultats flashcards
def flashcards():
    df = pd.read_csv('data/flashcards_englobante.csv')
    det = pd.read_csv('data/flashcards_englobante_detail.csv')
    c = df[df.configuration == 'corps'].groupby('paire').apply(
        lambda x: pd.Series({'carte': x.carte_pct.mean(), 'mesure': np.average(x.rupture_3j_pct, weights=x.n)}))
    t = df[df.configuration == 'toutes'].groupby('paire').apply(lambda x: np.average(x.rupture_3j_pct, weights=x.n))
    c['toutes'] = t
    c = c.sort_values('mesure')
    fig, ax = plt.subplots(figsize=(9, 4.2))
    x = np.arange(len(c))
    ax.bar(x - 0.27, c.carte, 0.27, label='annoncé sur la carte', color=ORANGE)
    ax.bar(x, c.mesure, 0.27, label='mesuré : englobantes', color=BLEU)
    ax.bar(x + 0.27, c.toutes, 0.27, label='mesuré : n\'importe quelle bougie', color=GRIS)
    ax.set_xticks(x, c.index)
    ax.set_ylim(50, 100)
    ax.set_ylabel('rupture en 3 jours (%)')
    ax.legend(loc='upper left', fontsize=8, ncol=3)
    ax.set_title('Ses pourcentages sont justes… mais une bougie quelconque fait presque pareil (2024-2026)', fontsize=10)
    sauver(fig, 'flashcards_cartes_vs_mesure.png')

    e = det[det.corps == 1]
    g, p = e[e.gain_r > 0], e[e.gain_r <= 0]
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.8))
    axs[0].bar(['trades gagnants'], [len(g) / len(e) * 100], color=VERT)
    axs[0].bar(['trades perdants'], [len(p) / len(e) * 100], color=ROUGE)
    axs[0].set_ylabel('% des trades')
    axs[0].set_title(f'Taux de réussite : {len(g) / len(e) * 100:.0f} %', fontsize=10)
    contrib = [len(g) / len(e) * g.gain_r.mean(), len(p) / len(e) * p.gain_r.mean()]
    axs[1].bar([f'gains\n({len(g) / len(e) * 100:.0f} % × {g.gain_r.mean():+.2f} R)',
                f'pertes\n({len(p) / len(e) * 100:.0f} % × {p.gain_r.mean():+.2f} R)'], contrib,
               color=[VERT, ROUGE])
    axs[1].axhline(sum(contrib), color='black', lw=1)
    axs[1].text(0.5, sum(contrib) + 0.01, f'espérance = {sum(contrib):+.2f} R', ha='center', va='bottom', fontsize=9)
    axs[1].set_ylabel('contribution à l\'espérance (R)')
    axs[1].set_title('…mais petits gains, grosses pertes', fontsize=10)
    sauver(fig, 'flashcards_reussite_vs_gain.png')

    fig, ax = plt.subplots(figsize=(8, 3.6))
    bins = np.arange(0, 75, 3)
    ax.hist(e[e.issue == 'objectif'].heures, bins=bins, color=VERT, alpha=0.75, label='objectif atteint')
    ax.hist(e[e.issue == 'stop'].heures, bins=bins, color=ROUGE, alpha=0.6, label='stop touché')
    mo, ms = e[e.issue == 'objectif'].heures.median(), e[e.issue == 'stop'].heures.median()
    ax.axvline(mo, color=VERT, ls='--')
    ax.axvline(ms, color=ROUGE, ls='--')
    ax.text(mo + 0.5, ax.get_ylim()[1] * 0.9, f'médiane TP : {mo:.0f} h', color=VERT, fontsize=9)
    ax.text(ms + 0.5, ax.get_ylim()[1] * 0.7, f'médiane SL : {ms:.0f} h', color=ROUGE, fontsize=9)
    ax.set_xlabel('heures après la clôture de l\'englobante')
    ax.set_ylabel('trades')
    ax.legend(fontsize=8)
    ax.set_title('Flashcards : délai avant l\'objectif ou le stop', fontsize=10)
    sauver(fig, 'flashcards_duree.png')


# ------------------------------------------------------------------ trades d'Amirou
def amirou():
    s = pd.read_csv('data/trades_simules.csv')
    s = s[(s.resolution == '1h') & (s.statut == 'annoncé') & s.issue.isin(['objectif', 'stop'])].copy()
    s['h'] = (pd.to_datetime(s.sortie_utc) - pd.to_datetime(s.entree_utc)).dt.total_seconds() / 3600
    fig, ax = plt.subplots(figsize=(8, 3.6))
    bins = [0, 5, 12, 24, 48, 72, 120, 240, 500]
    lab = ['<5 h', '5-12 h', '12-24 h', '1-2 j', '2-3 j', '3-5 j', '5-10 j', '>10 j']
    for iss, coul, dx in [('objectif', VERT, -0.2), ('stop', ROUGE, 0.2)]:
        cnt = pd.cut(s[s.issue == iss].h, bins, labels=lab).value_counts().reindex(lab)
        ax.bar(np.arange(len(lab)) + dx, cnt.values, 0.4, color=coul,
               label=f"{iss} (médiane {s[s.issue == iss].h.median():.0f} h)")
    ax.set_xticks(range(len(lab)), lab)
    ax.axvline(0.5, color=ORANGE, ls='--')
    ax.text(0.55, ax.get_ylim()[1] * 0.92, '« money likes speed » : objectif en moins de 5 h (#13746)', color=ORANGE, fontsize=8)
    ax.set_ylabel('trades')
    ax.set_xlabel('durée entre le déclenchement et la sortie')
    ax.legend(fontsize=8, loc='upper right')
    ax.set_title('Ses trades annoncés (2024-2026, données horaires) : délai avant TP ou SL', fontsize=10)
    sauver(fig, 'amirou_duree_tp.png')

    e = pd.read_csv('data/epoques_trades.csv')
    e = e[(e.statut == 'annoncé') & e.issue.isin(['objectif', 'stop'])]
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    jours = ['lun', 'mar', 'mer', 'jeu', 'ven']
    for k, (ep, coul) in enumerate([('2021-2022', GRIS), ('2023-2026', BLEU)]):
        x = e[e.epoque == ep]
        taux = [x[x.jour == j].gagnant.mean() * 100 for j in range(5)]
        axs[0].bar(np.arange(5) + (k - 0.5) * 0.4, taux, 0.4, color=coul, label=ep)
    axs[0].set_xticks(range(5), jours)
    axs[0].set_ylabel('% de trades gagnants')
    axs[0].set_title('Par jour de déclenchement', fontsize=10)
    axs[0].legend(fontsize=8)
    x = e[(e.epoque == '2023-2026') & (e.ratio_rr <= 8)]
    b = pd.cut(x.mlq_dist, [-1, 25, 75, 126], labels=['< 25 pips', '25-75', '> 75'])
    g = x.groupby(b, observed=True).agg(n=('r_net', 'size'), r=('r_net', 'mean'), w=('gagnant', 'mean'))
    axs[1].bar(g.index.astype(str), g.r, color=[ORANGE, GRIS, GRIS])
    for i, (n, r, w) in enumerate(g.itertuples(index=False)):
        axs[1].text(i, r + 0.02, f'{r:+.2f} R\n{w * 100:.0f} % gagn.\n{n} trades', ha='center', fontsize=8)
    axs[1].set_ylabel('R net moyen')
    axs[1].set_ylim(0, max(g.r) * 1.6)
    axs[1].set_title('2023-2026 : distance de l\'entrée au MLQ (hors ratios > 8)', fontsize=10)
    sauver(fig, 'amirou_jours_mlq.png')


# ------------------------------------------------------------------ époques
def epoques():
    e = pd.read_csv('data/epoques_trades.csv')
    e = e[(e.statut == 'annoncé') & e.issue.isin(['objectif', 'stop'])].sort_values('date')
    g = e.groupby('an').agg(stop=('stop_p', 'median'), rr=('ratio_rr', 'median'), w=('gagnant', 'mean'))
    ac = pd.read_csv('data/epoques_trades.csv').groupby('an').statut.apply(lambda x: (x == 'après coup').mean() * 100)
    fig, axs = plt.subplots(1, 4, figsize=(12, 3.3))
    col = [GRIS if a <= 2022 else BLEU for a in g.index]
    for ax, v, t in [(axs[0], g.stop, 'stop médian (pips)'), (axs[1], g.rr, 'ratio médian (1:x)'),
                     (axs[2], g.w * 100, '% de trades gagnants'), (axs[3], ac.reindex(g.index), '% de captures après coup')]:
        ax.bar(g.index.astype(str), v, color=col)
        ax.set_title(t, fontsize=10)
        ax.tick_params(axis='x', rotation=45)
    fig.suptitle('Deux manières de trader : 2021-2022 (gris) et 2023-2026 (bleu)', fontsize=11)
    sauver(fig, 'epoques_style.png')

    fig, ax = plt.subplots(figsize=(9, 3.8))
    for ep, coul in [('2021-2022', GRIS), ('2023-2026', BLEU)]:
        x = e[(e.epoque == ep)]
        ax.plot(np.arange(1, len(x) + 1), x.r_net.clip(upper=8).cumsum().values, color=coul, lw=2,
                label=f'{ep} : {len(x)} trades, gains plafonnés à 8 R')
    ax.axhline(0, color='black', lw=0.8)
    ax.set_xlabel('trades annoncés, dans l\'ordre')
    ax.set_ylabel('R cumulés (spread déduit)')
    ax.legend(fontsize=8)
    ax.set_title('Résultat cumulé de ses trades annoncés à l\'avance', fontsize=10)
    sauver(fig, 'epoques_courbes.png')


# ------------------------------------------------------------------ septembres
def septembres():
    # valeurs du tableau de synthèse de analyses/TRADES_SEPTEMBRE.md (vérification manuelle)
    t = pd.DataFrame({'gains': [7, 1, 2, 1, 3, 2, 3, 10], 'pertes': [9, 1, 1, 1, 0, 2, 0, 2],
                      'BE': [2, 1, 0, 0, 1, 1, 1, 2], 'non déclenchés': [0, 1, 1, 1, 2, 4, 2, 5],
                      'non documentés / après coup': [5, 6, 2, 3, 1, 1, 3, 3]}, index=range(2019, 2027))
    fig, ax = plt.subplots(figsize=(9, 4))
    bas = np.zeros(len(t))
    for col, coul in zip(t.columns, [VERT, ROUGE, BLEU, GRIS, '#d7ccc8']):
        ax.bar(t.index.astype(str), t[col], bottom=bas, color=coul, label=col)
        bas += t[col].values
    ax.set_ylabel('trades relevés en septembre')
    ax.legend(fontsize=8, ncol=3, loc='upper center')
    ax.set_ylim(0, 30)
    ax.set_title('Trades de septembre vérifiés à la main : issue documentée par le canal', fontsize=10)
    sauver(fig, 'septembres_bilan.png')

    ev = pd.read_csv('data/trade_events.csv')
    ev['an'] = ev.date_utc.str[:4].astype(int)
    c = ev.pivot_table(index='an', columns='evenement', values='id_message', aggfunc='count').fillna(0)
    fig, ax = plt.subplots(figsize=(9, 3.8))
    x = np.arange(len(c))
    ax.bar(x - 0.2, c['tp'], 0.4, color=VERT, label='messages « TP touché »')
    ax.bar(x + 0.2, c['sl'], 0.4, color=ROUGE, label='messages « SL touché »')
    ax2 = ax.twinx()
    ax2.plot(x, c['tp'] / (c['tp'] + c['sl']) * 100, color='black', marker='o', label='TP / (TP + SL)')
    ax2.set_ylim(0, 100)
    ax2.set_ylabel('% de TP')
    ax.set_xticks(x, c.index)
    ax.set_ylabel('messages')
    ax.legend(loc='upper left', fontsize=8)
    ax2.legend(loc='upper right', fontsize=8)
    ax.set_title('Tout le canal : les SL disparaissent du canal public à partir de 2021', fontsize=10)
    sauver(fig, 'septembres_tp_sl_canal.png')

    hh = prix_yahoo._charger('EURUSD', '1h')
    h = hh[(hh.date >= '2026-08-28') & (hh.date < '2026-10-01')]
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.plot(h.date, h.close, color='#37474f', lw=0.9)
    trades = [('2026-09-01 10:00', 1.16110, 'vente limite 1.16110\n« raté de 3 pips » : non déclenché', ORANGE, -0.008),
              ('2026-09-10 11:00', 1.16142, 'vente 1.16142 (BCE)\nTP 1.15843 atteint', VERT, -0.010),
              ('2026-09-16 23:00', 1.14999, 'vente limite 1.14999\n« à 2 pips » : non déclenché', ORANGE, 0.008)]
    for d, niv, txt, coul, dy in trades:
        d = pd.Timestamp(d)
        ax.plot([d, d + pd.Timedelta(days=2)], [niv, niv], color=coul, lw=2)
        ax.annotate(txt, xy=(d, niv), xytext=(d + pd.Timedelta(hours=12), niv + dy), fontsize=8, color=coul,
                    arrowprops=dict(arrowstyle='->', color=coul))
    bas = h.close.min()
    for d, txt in [('2026-08-31', '31/08 : « dollar haussier »'), ('2026-09-10', 'BCE'),
                   ('2026-09-16', 'Fed'), ('2026-09-17', 'BoE')]:
        ax.axvline(pd.Timestamp(d), color=GRIS, ls=':', lw=1)
        ax.text(pd.Timestamp(d), bas - 0.001, txt, fontsize=7, color='#555', ha='right' if d == '2026-09-16' else 'left',
                rotation=90, va='bottom')
    import matplotlib.dates as mdates
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
    ax.set_ylabel('EURUSD (horaire)')
    ax.set_title('Septembre 2026 : l\'appel « dollar haussier » était juste, mais 2 des 3 ordres EURUSD ne sont jamais déclenchés',
                 fontsize=10)
    sauver(fig, 'septembre_2026_eurusd.png')


# ------------------------------------------------------------------ saisonnalité
def saisonnalite():
    r = pd.read_csv('data/rendements_mensuels.csv')
    r['an'] = r.mois.str[:4].astype(int)
    r['m'] = r.mois.str[5:].astype(int)
    noms = ['jan', 'fév', 'mar', 'avr', 'mai', 'juin', 'juil', 'août', 'sep', 'oct', 'nov', 'déc']
    e = r[(r.paire == 'EURUSD') & (r.an >= 2010)].pivot(index='an', columns='m', values='rendement_pct')
    fig, ax = plt.subplots(figsize=(9, 5.4))
    im = ax.imshow(e.values, cmap='RdYlGn', vmin=-4, vmax=4, aspect='auto')
    ax.set_xticks(range(12), noms)
    ax.set_yticks(range(len(e)), e.index)
    for i in range(e.shape[0]):
        for j in range(e.shape[1]):
            v = e.values[i, j]
            if not np.isnan(v):
                ax.text(j, i, f'{v:+.1f}', ha='center', va='center', fontsize=6.5)
    moy = e.loc[2016:2025].mean()
    ax.set_xlabel('moyenne 2016-2025 : ' + '  '.join(f'{v:+.1f}' for v in moy.values), fontsize=7)
    fig.colorbar(im, ax=ax, label='rendement du mois (%)')
    ax.set_title('Saisonnalité EURUSD : rendement de chaque mois (%) — septembre souvent rouge, mais pas toujours', fontsize=10)
    sauver(fig, 'saison_eurusd_heatmap.png')

    # affirmations saisonnières (tableau de la section 4 de TRADES_VS_SAISONNALITE.md)
    aff = [('#8591 07/2023 EURUSD ↑', 0.64, 0.93, 1), ('#9817 11/2023 AUDJPY ↑', 0.99, 1.98, 1),
           ('#9783 12/2023 EURUSD ↑', 1.15, 1.42, 1), ('#10892 04/2024 EURUSD ↑', 0.29, -0.99, 0),
           ('#11946 09/2024 EURUSD ↓', -1.36, 0.77, 0), ('#13180 04/2025 AUDJPY ↑', 0.78, -2.36, 0),
           ('#14662 04/2026 AUDJPY ↑', 0.23, 3.21, 1), ('#14815 05/2026 EURUSD ↓', -0.06, -0.42, 2),
           ('#14907 06/2026 EURJPY ↑', 2.19, -0.17, 0), ('#15204 08/2026 USD ↑ (EURUSD)', 0.02, 0.85, 0),
           ('#15269 09/2026 USD ↑ (EURUSD)', -0.82, -1.87, 1)]
    fig, ax = plt.subplots(figsize=(9, 5))
    y = np.arange(len(aff))
    ax.barh(y + 0.2, [a[1] for a in aff], 0.4, color=GRIS, label='moyenne des 10 années précédentes')
    ax.barh(y - 0.2, [a[2] for a in aff], 0.4, color=[[ROUGE, VERT, ORANGE][a[3]] for a in aff],
            label='mois réel (vert : juste, rouge : faux, orange : sans statistique)')
    ax.set_yticks(y, [a[0] for a in aff], fontsize=8)
    ax.invert_yaxis()
    ax.axvline(0, color='black', lw=0.8)
    ax.set_xlabel('rendement du mois (%)')
    ax.legend(fontsize=8, loc='lower right')
    ax.set_title('Ses 11 affirmations saisonnières : 6 justes, souvent sur un biais faible', fontsize=10)
    sauver(fig, 'saison_affirmations.png')

    fig, axs = plt.subplots(1, 2, figsize=(12, 4), gridspec_kw={'width_ratios': [1.6, 1]})
    cat = ['avec la saison\n(biais net)', 'contre la saison\n(biais net)', 'avec la\nmoyenne 10 ans',
           'contre la\nmoyenne 10 ans', 'avec le mois\nréel', 'contre le mois\nréel']
    val = [33, 57, 39, 38, 38, 40]
    axs[0].bar(cat, val, color=[VERT, ROUGE] * 3)
    axs[0].axhline(40, color='black', ls='--', lw=0.8)
    axs[0].text(5.4, 41, 'moyenne 40 %', fontsize=8, ha='right')
    axs[0].set_ylabel('% de TP parmi TP + SL')
    axs[0].tick_params(axis='x', labelsize=7.5)
    axs[0].set_title('La saisonnalité ne change pas la réussite', fontsize=10)
    axs[1].pie([12, 10, 14], labels=['stop serré /\nchasse aux stops (12)', 'annonce\néconomique (10)', 'non expliquée (14)'],
               colors=[ORANGE, BLEU, GRIS], autopct='%d%%', textprops={'fontsize': 8})
    axs[1].set_title('Causes des 36 SL du registre', fontsize=10)
    sauver(fig, 'saison_reussite_causes.png')

    m = pd.read_csv('data/mois_hors_saisonnalite.csv')
    m['d'] = pd.to_datetime(m.mois + '-01')
    c = m.groupby('d').size()
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.bar(c.index, c.values, width=25, color=BLEU)
    for d, txt in [('2019-12-01', 'élections UK'), ('2020-03-01', 'COVID'), ('2020-11-01', 'vaccins'),
                   ('2021-06-01', 'Fed restrictive'), ('2022-03-01', 'Ukraine'), ('2022-11-01', 'BoJ, CPI US'),
                   ('2024-08-01', 'krach du 5 août'), ('2025-04-01', 'droits de douane'), ('2026-03-01', 'Iran'),
                   ('2026-06-01', 'Fed, yen à 162')]:
        d = pd.Timestamp(d)
        ax.annotate(txt, xy=(d, c.get(d, 0)), xytext=(d, c.max() + 1.5), fontsize=7, ha='center', rotation=30,
                    arrowprops=dict(arrowstyle='-', color=GRIS, lw=0.6))
    ax.set_ylim(0, c.max() + 5)
    ax.set_ylabel('paires hors saison')
    ax.set_title('Mois où des paires ont fait l\'inverse de leur saisonnalité (≥ 1 écart-type) : ils suivent les chocs macro',
                 fontsize=10)
    sauver(fig, 'saison_hors_saison.png')


# ------------------------------------------------------------------ stratégie, algorithmes, fondamentaux
def strategie():
    concepts = pd.DataFrame({
        'Wyckoff': [6, 20, 39, 25, 15, 7, 9, 4], 'Smart money / OB': [7, 1, 19, 25, 15, 18, 6, 0],
        'Offre et demande': [18, 29, 18, 16, 40, 28, 35, 20], 'Quarter points / MLQ': [0, 0, 1, 21, 8, 9, 6, 2],
        'Price & Time': [0, 0, 0, 3, 16, 27, 4, 3], 'Sessions': [41, 24, 23, 24, 55, 93, 95, 29],
        'Fondamental': [3, 2, 18, 31, 121, 57, 82, 26], 'Sentiment / COT': [0, 2, 0, 7, 21, 21, 74, 31],
        'Annonces': [3, 2, 10, 23, 59, 65, 57, 20], 'Saisonnalité': [0, 0, 0, 0, 15, 7, 5, 4],
        'Playbook / stats': [20, 13, 6, 10, 51, 56, 48, 27]}, index=range(2019, 2027)).T
    fig, ax = plt.subplots(figsize=(9, 4.8))
    im = ax.imshow(concepts.values, cmap='Blues', aspect='auto')
    ax.set_xticks(range(8), concepts.columns)
    ax.set_yticks(range(len(concepts)), concepts.index)
    for i in range(concepts.shape[0]):
        for j in range(concepts.shape[1]):
            v = concepts.values[i, j]
            ax.text(j, i, v, ha='center', va='center', fontsize=7, color='white' if v > 60 else 'black')
    fig.colorbar(im, ax=ax, label='messages')
    ax.set_title('Ce dont il parle, année par année : de la technique pure (2019-2022) au fondamental (2023-2026)', fontsize=10)
    sauver(fig, 'strategie_concepts.png')

    s = pd.read_csv('data/trades_simules.csv')
    lab = {'objectif': 'objectif atteint', 'stop': 'stop touché', 'non déclenché': 'jamais déclenché',
           'non déclenché (objectif atteint sans entrée)': 'jamais déclenché', 'ouvert après 20 jours': 'encore ouvert'}
    a = s[s.statut == 'annoncé'].issue.map(lab).value_counts()
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.8))
    axs[0].pie(s.statut.value_counts().values, labels=[f'{k} ({v})' for k, v in s.statut.value_counts().items()],
               colors=[BLEU, ORANGE, GRIS], autopct='%d%%', textprops={'fontsize': 8})
    axs[0].set_title('518 captures lues : quand ont-elles été publiées ?', fontsize=10)
    axs[1].bar(a.index, a.values, color=[ROUGE if 'stop' in k else VERT if 'objectif' in k else GRIS for k in a.index])
    axs[1].set_title('Les 350 trades annoncés à l\'avance', fontsize=10)
    axs[1].tick_params(axis='x', labelsize=8)
    sauver(fig, 'strategie_captures.png')

    b = pd.read_csv('data/backtest_algo.csv')
    m = pd.read_csv('data/backtest_mlq.csv')
    e = pd.read_csv('data/epoques_trades.csv')
    e = e[(e.statut == 'annoncé') & e.issue.isin(['objectif', 'stop'])]
    lignes = [('Ses trades annoncés 2023-2026', e[e.epoque == '2023-2026'].r_net.mean(), len(e[e.epoque == '2023-2026']))]
    for v, g in b.groupby('variante'):
        lignes.append((f'Algo « prise de liquidité » : {v}', g.resultat_r.mean(), len(g)))
    for nom, g in [('Algo MLQ : tous les jours', m), ('Algo MLQ : mercredi', m[m.jour == 2]),
                   ('Algo MLQ : mardi-jeudi', m[m.jour.isin([1, 2, 3])]), ('Algo MLQ : + tendance', m[m.tendance == 1]),
                   ('Algo MLQ : + fondamental', m[m.fond == 1])]:
        lignes.append((nom, g.r.mean(), len(g)))
    fig, ax = plt.subplots(figsize=(9, 4.4))
    y = np.arange(len(lignes))
    ax.barh(y, [l[1] for l in lignes], color=[VERT if l[1] > 0 else ROUGE for l in lignes])
    for i, l in enumerate(lignes):
        ax.text(max(l[1], 0) + 0.01, i, f'{l[1]:+.2f} R ({l[2]} trades)', va='center', ha='left', fontsize=8)
    ax.set_yticks(y, [l[0] for l in lignes], fontsize=8)
    ax.invert_yaxis()
    ax.axvline(0, color='black', lw=0.8)
    ax.set_xlim(-0.45, 0.75)
    ax.set_xlabel('espérance par trade, spread déduit (R)')
    ax.set_title('Ses règles appliquées par un robot perdent ; seuls ses trades choisis à la main gagnent', fontsize=10)
    sauver(fig, 'strategie_algos.png')


def fondamental():
    import json
    d = json.load(open('data/fondamental/resultats_tests.json'))
    a = d['A_lecture_macro_amirou']
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    ans = sorted(a['par_annee'])
    axs[0].bar(ans, [a['par_annee'][k] * 100 for k in ans], color=BLEU)
    axs[0].axhline(50, color='black', ls='--', lw=0.8)
    axs[0].set_ylim(30, 70)
    axs[0].set_title(f"Test A : ses avis macro justes à 5 jours ({a['taux_juste'] * 100:.1f} %, n={a['n']})", fontsize=10)
    axs[0].set_ylabel('% d\'avis dans le bon sens')
    dev = sorted(a['par_devise'], key=lambda k: -a['par_devise'][k][1])
    axs[1].bar([f"{k}\n({a['par_devise'][k][1]})" for k in dev], [a['par_devise'][k][0] * 100 for k in dev], color=BLEU)
    axs[1].axhline(50, color='black', ls='--', lw=0.8)
    axs[1].set_ylim(30, 70)
    axs[1].set_title('Par devise (nombre d\'avis)', fontsize=10)
    sauver(fig, 'fond_test_a.png')

    b = d['B_ses_trades_vs_fondamentaux']['univarie']
    noms = {'surprise_30j': 'surprises\néco 30 j', 'taux': 'différentiel\nde taux', 'taux_90j': 'taux\n90 j',
            'cot': 'COT', 'cot_4s': 'COT\n4 sem.', 'amirou_14j': 'son biais\nécrit'}
    fig, axs = plt.subplots(1, 2, figsize=(10, 3.6))
    x = np.arange(len(b))
    axs[0].bar(x - 0.2, [v['avec'][2] for v in b.values()], 0.4, color=VERT, label='trade dans le sens du fondamental')
    axs[0].bar(x + 0.2, [v['contre'][2] for v in b.values()], 0.4, color=ROUGE, label='trade contre')
    axs[0].set_xticks(x, [noms[k] for k in b], fontsize=8)
    axs[0].set_ylabel('R moyen')
    axs[0].legend(fontsize=8)
    axs[0].set_title('Test B : ses trades ne gagnent pas plus avec le fondamental', fontsize=10)
    c = d['C_modele_fondamental_hebdo']['par_annee']
    ans = sorted(c['gradient_boosting'])
    axs[1].bar(np.arange(len(ans)) - 0.2, [c['logistique'][k]['gain_total_pct'] for k in ans], 0.4, color=GRIS, label='logistique')
    axs[1].bar(np.arange(len(ans)) + 0.2, [c['gradient_boosting'][k]['gain_total_pct'] for k in ans], 0.4, color=BLEU,
               label='gradient boosting')
    axs[1].axhline(0, color='black', lw=0.8)
    axs[1].set_xticks(range(len(ans)), ans)
    axs[1].set_ylabel('gain de l\'année (% cumulés)')
    axs[1].legend(fontsize=8)
    axs[1].set_title('Test C : modèle purement fondamental, instable', fontsize=10)
    sauver(fig, 'fond_tests_b_c.png')


# ------------------------------------------------------------------ docs
def docs():
    fig, ax = plt.subplots(figsize=(9, 3.8))
    lab = ['Audit Antigravity\n(167 gains / 41 pertes)', 'Messages du canal\n« TP » / « SL »', 'Registre texte\n(281 trades)',
           'Captures : trades\nannoncés à l\'avance', 'Captures : trades\npubliés après coup', 'Flashcards\n(annoncé)']
    val = [167 / 208 * 100, 54 / 126 * 100, 40, 40, 65, 77]
    ax.bar(lab, val, color=[ROUGE, BLEU, BLEU, BLEU, ORANGE, ORANGE])
    for i, v in enumerate(val):
        ax.text(i, v + 1.5, f'{v:.0f} %', ha='center', fontsize=9)
    ax.set_ylim(0, 100)
    ax.set_ylabel('% de trades gagnants')
    ax.tick_params(axis='x', labelsize=8)
    ax.set_title('Taux de réussite : affiché (rouge, orange) contre mesuré (bleu)', fontsize=10)
    sauver(fig, 'verification_taux.png')

    cl = pd.read_csv('data/photos_classification.csv')
    c = cl.categorie.value_counts()
    tailles = {'trading': 274, 'conversation': 24, 'certificat': 18, 'autre': 86}
    fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
    coul = {'trading': BLEU, 'conversation': GRIS, 'certificat': ORANGE, 'autre': ROUGE}
    axs[0].bar(c.index, c.values, color=[coul[k] for k in c.index])
    axs[0].set_title('Photos du canal par catégorie', fontsize=10)
    axs[1].bar(list(tailles), list(tailles.values()), color=[coul[k] for k in tailles])
    axs[1].set_title('Taille (Mo) — orange et rouge : à supprimer', fontsize=10)
    sauver(fig, 'stockage_photos.png')


# ------------------------------------------------------------------ carry, momentum, intrajournalier
def autres_algos():
    m = pd.read_csv('data/carry_momentum_mensuel.csv', parse_dates=['mois']).set_index('mois')
    fig, ax = plt.subplots(figsize=(10, 4.4))
    for col, coul in [('carry (3 contre 3)', ORANGE), ('momentum tendance 12 mois', BLEU),
                      ('momentum transversal 3 mois', GRIS), ('carry + momentum 12 mois', VERT)]:
        ax.plot(m.index, (1 + m[col]).cumprod() * 100, label=col, color=coul, lw=2 if 'carry +' in col else 1.3)
    ax.axhline(100, color='black', lw=0.7)
    for d, txt in [('2008-09-15', 'Lehman'), ('2015-01-15', 'BNS lâche le plancher'), ('2020-03-15', 'COVID'),
                   ('2024-08-05', 'krach du carry')]:
        ax.axvline(pd.Timestamp(d), color=GRIS, ls=':', lw=0.8)
        ax.text(pd.Timestamp(d), ax.get_ylim()[1] * 0.98, txt, fontsize=7, rotation=90, va='top', ha='right')
    ax.set_ylabel('valeur de 100 investis (sans levier)')
    ax.legend(fontsize=8, loc='upper left')
    ax.set_title('Carry et momentum sur 8 devises du G10, 2000-2026 (coûts déduits)', fontsize=10)
    sauver(fig, 'algos_carry_momentum.png')

    p = pd.read_csv('data/saisonnalite_intraday_profil.csv').set_index('heure_utc')
    fig, ax = plt.subplots(figsize=(10, 3.8))
    moy = p[['EUR', 'GBP', 'JPY', 'AUD', 'NZD']].mean(axis=1)
    ax.bar(moy.index, moy.values, color=[VERT if v > 0 else ROUGE for v in moy.values])
    for a, b, t, c in [(23, 24, 'Asie', '#fff3e0'), (0, 7, '', '#fff3e0'), (7, 12, 'Europe', '#e3f2fd'),
                       (13, 20, 'États-Unis', '#e8f5e9')]:
        ax.axvspan(a - 0.5, b - 0.5, color=c, zorder=0)
        if t:
            ax.text((a + b) / 2 - 0.5, moy.max() * 1.05, t, ha='center', fontsize=8)
    ax.axhline(0, color='black', lw=0.7)
    ax.set_xticks(range(24))
    ax.set_xlabel('heure UTC')
    ax.set_ylabel('points de base par heure')
    ax.set_title('Rendement moyen de 5 devises contre le dollar selon l\'heure (2024-2026) : '
                 'pas de cycle « heures locales » exploitable', fontsize=10)
    sauver(fig, 'algos_intraday_profil.png')


def main():
    os.makedirs(SORTIE, exist_ok=True)
    schema_englobante()
    schema_fvg()
    schema_mlq()
    flashcards()
    amirou()
    epoques()
    septembres()
    saisonnalite()
    strategie()
    fondamental()
    docs()
    autres_algos()


if __name__ == '__main__':
    main()
