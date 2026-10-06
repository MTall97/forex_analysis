#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trades de l'utilisateur sur un compte de prop firm de 10 000 $ (juin-juillet 2026) : évolution heure par heure.

Entrée : data/compte_propfirm/trades_2026.csv (relevé de la plateforme ; heures en UTC, vérifié en comparant les
prix aux bougies horaires : 18 prix sur 24 tombent dans la bougie de la même heure UTC, aucun autre décalage ne fait
mieux).
Les deux GBPUSD du 14/07/2026 sont notés BUY dans le relevé, mais leur résultat et leur TP (sous l'entrée)
correspondent à des ventes : ils sont traités comme des ventes.

Pour chaque trade, avec les bougies horaires Yahoo (data/prix/yahoo/) :
- gain latent maximal et perte latente maximale pendant le trade (en pips et en $), et l'heure du gain maximal ;
- après la fermeture, sur 72 h depuis l'entrée : l'objectif prévu est-il atteint, et quand ? le stop prévu ?
- prix de fermeture comparé à la bougie de la même heure (écart en pips hors de la bougie).
La bougie de l'heure d'entrée est exclue du gain et de la perte latents (on ne sait pas ce qui précède l'entrée).
Sortie : data/compte_propfirm/analyse.csv, figure assets/figures/compte_propfirm_trades.png
"""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
VENTES_MAL_NOTEES = {10335699, 10335700}


def pip(p):
    return 0.01 if p.endswith('JPY') else 0.0001


def main():
    t = pd.read_csv('data/compte_propfirm/trades_2026.csv', parse_dates=['ouverture', 'fermeture'])
    t['sens_reel'] = ['SELL' if i in VENTES_MAL_NOTEES else s for i, s in zip(t['id'], t['sens'])]
    H = {p: pd.read_csv(f'data/prix/yahoo/{p}_1h.csv', parse_dates=['date']).set_index('date')
         for p in t['paire'].unique()}
    lignes = []
    fig, axes = plt.subplots(4, 3, figsize=(15, 13))
    for ax, (_, r) in zip(axes.flat, t.iterrows()):
        p, s = r['paire'], (1 if r['sens_reel'] == 'BUY' else -1)
        pp = pip(p)
        pips_reels = (r['prix_fermeture'] - r['prix_ouverture']) * s / pp
        usd_pip = r['net'] / pips_reels
        h = H[p]
        debut = r['ouverture'].floor('h')
        pendant = h[(h.index > debut) & (h.index < r['fermeture'].floor('h'))]
        # bougie de fermeture incluse jusqu'à la fermeture (approximation horaire)
        pendant = pd.concat([pendant, h[h.index == r['fermeture'].floor('h')]]) if r['fermeture'].floor('h') > debut \
            else pendant
        fav = ((pendant['high'] if s > 0 else -pendant['low']) - r['prix_ouverture'] * s) / pp
        dfav = ((pendant['low'] if s > 0 else -pendant['high']) - r['prix_ouverture'] * s) / pp
        mfe = fav.max() if len(fav) else 0.0
        mae = dfav.min() if len(dfav) else 0.0
        t_mfe = fav.idxmax().strftime('%d/%m %Hh') if len(fav) else ''
        suite = h[(h.index > debut) & (h.index <= debut + pd.Timedelta(hours=72))]
        tp, sl = r['objectif'], r['stop']

        def atteint(niveau, fav_dir):
            if not niveau:
                return ''
            if (fav_dir and s > 0) or (not fav_dir and s < 0):
                x = suite[suite['high'] >= niveau]
            else:
                x = suite[suite['low'] <= niveau]
            return x.index[0].strftime('%d/%m %Hh') if len(x) else 'non'

        def recul_avant_tp():
            """Pire recul (pips) entre l'entrée et l'heure où l'objectif est atteint : le stop d'origine devait être plus loin."""
            if not tp:
                return None
            x = suite[(suite['high'] >= tp) if s > 0 else (suite['low'] <= tp)]
            if not len(x):
                return None
            av = suite[suite.index <= x.index[0]]
            return round(((av['low'] if s > 0 else -av['high']) - r['prix_ouverture'] * s).min() / pp, 1)

        b = h[h.index == r['fermeture'].floor('h')]
        hors = max(b['low'].iat[0] - r['prix_fermeture'], r['prix_fermeture'] - b['high'].iat[0], 0) / pp if len(b) else None
        tp_pips = (tp - r['prix_ouverture']) * s / pp if tp else None
        lignes.append(dict(
            id=r['id'], paire=p, sens=r['sens_reel'], ouverture=r['ouverture'], fermeture=r['fermeture'],
            lots=r['lots'], usd_par_pip=round(usd_pip, 2), resultat_pips=round(pips_reels, 1), resultat_usd=r['net'],
            gain_latent_max_pips=round(mfe, 1), gain_latent_max_usd=round(mfe * usd_pip, 0), heure_gain_max=t_mfe,
            perte_latente_max_pips=round(mae, 1), perte_latente_max_usd=round(mae * usd_pip, 0),
            objectif_pips=round(tp_pips, 1) if tp_pips else None,
            objectif_atteint_72h=atteint(tp, True), stop_final_touche_72h=atteint(sl, False) if sl else '',
            recul_max_avant_objectif_pips=recul_avant_tp(),
            fermeture_hors_bougie_pips=round(hors, 1) if hors is not None else None))
        # figure
        fen = h[(h.index >= debut - pd.Timedelta(hours=6)) & (h.index <= debut + pd.Timedelta(hours=72))]
        ax.plot(fen.index, fen['close'], color='#555', lw=1)
        ax.fill_between(fen.index, fen['low'], fen['high'], color='#bbb', alpha=0.4, lw=0)
        ax.axhline(r['prix_ouverture'], color='#1e88e5', lw=1, label='entrée')
        if sl:
            ax.axhline(sl, color='#ef5350', lw=1, ls='--', label='stop')
        if tp:
            ax.axhline(tp, color='#26a69a', lw=1, ls='--', label='objectif')
        ax.axvspan(r['ouverture'], r['fermeture'], color='#1e88e5', alpha=0.08)
        ax.plot([r['fermeture']], [r['prix_fermeture']], 'o', color='#ef5350' if r['net'] < 0 else '#26a69a', ms=6)
        ax.set_title(f"{p} {('achat' if s > 0 else 'vente')} {r['ouverture']:%d/%m %Hh%M} : {r['net']:+.0f} $ "
                     f"(max {mfe * usd_pip:+.0f} $)", fontsize=9)
        ax.tick_params(labelsize=7)
        ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%d/%m %Hh'))
    axes.flat[0].legend(fontsize=7)
    fig.suptitle('Vos trades heure par heure (bande grise : plage horaire ; zone bleue : durée du trade ; '
                 'point : fermeture)', fontsize=11)
    fig.tight_layout()
    fig.savefig('assets/figures/compte_propfirm_trades.png', dpi=110)
    a = pd.DataFrame(lignes)
    a.to_csv('data/compte_propfirm/analyse.csv', index=False)
    pd.set_option('display.width', 250)
    print(a.drop(columns=['fermeture', 'lots']).to_string(index=False))
    print('\nTotal :', a['resultat_usd'].sum().round(2), '$ ; somme des gains latents max :', a['gain_latent_max_usd'].sum())


if __name__ == '__main__':
    main()
