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
- epoques_style.png, epoques_courbes.png.

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


def main():
    os.makedirs(SORTIE, exist_ok=True)
    schema_englobante()
    schema_fvg()
    schema_mlq()
    flashcards()
    amirou()
    epoques()


if __name__ == '__main__':
    main()
