#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Englobante journalière : d'autres façons d'entrer que la clôture de la bougie, testées sur les mêmes signaux.

Suite de scripts/tester_englobante_fvg.py : les ordres limites sur repli (FVG, repli fixe) ne s'exécutent
que quand l'englobante échoue et ratent les trades qui partent directement. On teste donc des entrées qui
ne ratent aucun signal (repli tenté pendant la nuit, sinon entrée au marché) ou qui attendent une
confirmation. Liste fixée avant de lancer le test :
- clôture : à la clôture de J (règle actuelle, suivie en démo) ;
- Londres : au marché à l'ouverture de 07h UTC de J+1 ;
- stop au-dessus de J : ordre stop 1 pip au-delà de l'extrême de J (plus haut pour un achat), 24 h ou 48 h ;
- confirmation 1h : à la clôture de la première bougie 1h (J+1 ou J+2) qui clôture au-delà de l'extrême de J ;
- repli 30 % la nuit, sinon Londres : ordre limite à 30 % de la distance clôture-stop entre 00h et 07h UTC ;
  s'il n'est pas exécuté, entrée au marché à 07h ;
- FVG 4h la nuit, sinon Londres : même chose avec le haut du FVG 4h le plus récent (Londres seul sans FVG).
Pour toutes : même stop (2 pips au-delà de l'autre extrême de J), objectif 2 R depuis l'entrée réelle,
sortie à la clôture de J+3 ; rejeu horaire, stop prioritaire dans une même heure, spread déduit.

Mesure : R par signal (ordre non exécuté = 0) et différence avec la clôture **signal par signal**
(écart-type de la différence appariée), plus puissante qu'une comparaison de moyennes.
Sortie : data/englobante_fvg/entrees_trades.csv, data/englobante_fvg/entrees_resultats.csv
"""
import os
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from tester_englobante_fvg import PAIRES_AUTRES, PAIRES_DEMO, charger, fvgs  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

SORTIE = 'data/englobante_fvg'
VARIANTES = ['clôture', 'Londres 07h', 'stop au-delà de J 24h', 'stop au-delà de J 48h', 'confirmation 1h',
             'repli 30 % la nuit, sinon Londres', 'FVG 4h la nuit, sinon Londres']


def suivre(ah, al, ac, i0, entree, sl, tp):
    """Position ouverte à partir de la bougie i0 incluse. R brut."""
    risque = entree - sl
    for i in range(i0, len(ah)):
        if al[i] <= sl:
            return -1.0
        if ah[i] >= tp:
            return (tp - entree) / risque
    return (ac[-1] - entree) / risque


def signaux(p):
    h = charger(p)
    jours = sorted(h['jour'].unique())
    par_jour = {j: g for j, g in h.groupby('jour')}
    pp, sp = pip(p), spread(p)
    lignes = []
    for i in range(1, len(jours) - 3):
        g, g0 = par_jour[jours[i]], par_jour[jours[i - 1]]
        if len(g) < 18 or len(g0) < 18:
            continue
        O, C, O0, C0 = g['open'].iloc[0], g['close'].iloc[-1], g0['open'].iloc[0], g0['close'].iloc[-1]
        if abs(C - O) < abs(C0 - O0) or (C - O) * (C0 - O0) >= 0:
            continue
        sens = 1 if C > O else -1
        apres = pd.concat([par_jour[j] for j in jours[i + 1:i + 4]])
        n24 = len(par_jour[jours[i + 1]])
        n48 = n24 + len(par_jour[jours[i + 2]])
        heure = apres['date'].dt.hour.to_numpy()
        if sens == 1:
            jh, jl = g['high'].to_numpy(), g['low'].to_numpy()
            ao, ah, al, ac = (apres[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
        else:
            jh, jl = -g['low'].to_numpy(), -g['high'].to_numpy()
            ao, ah, al, ac = -apres['open'].to_numpy(), -apres['low'].to_numpy(), -apres['high'].to_numpy(), \
                -apres['close'].to_numpy()
        sl = jl.min() - 2 * pp
        c0 = C * sens
        risque0 = c0 - sl
        if risque0 < 5 * pp:
            continue
        pas = 250 * pp
        ext = abs(jl.min())
        mlq = abs(ext - round(ext / pas) * pas) <= 25 * pp
        base = dict(paire=p, date=jours[i], sens='achat' if sens == 1 else 'vente', mlq=mlq)
        i07 = next((k for k in range(n24) if heure[k] >= 7), 0)
        res = {}

        def net(r, e):
            return r - sp / (e - sl)

        res['clôture'] = net(suivre(ah, al, ac, 0, c0, sl, c0 + 2 * risque0), c0)
        e = ao[i07]
        res['Londres 07h'] = net(suivre(ah, al, ac, i07, e, sl, e + 2 * (e - sl)), e) if e > sl else net(-1.0, c0)
        niveau = jh.max() + pp
        for nom, n in [('stop au-delà de J 24h', n24), ('stop au-delà de J 48h', n48)]:
            r = 0.0
            for k in range(n):
                if ah[k] >= niveau:
                    e = max(niveau, ao[k])
                    r = net(-1.0 if al[k] <= sl else suivre(ah, al, ac, k + 1, e, sl, e + 2 * (e - sl)), e)
                    break
            res[nom] = r
        r = 0.0
        for k in range(n48):
            if al[k] <= sl:              # stop touché avant toute confirmation : pas de trade
                break
            if ac[k] > jh.max():
                e = ac[k]
                r = net(suivre(ah, al, ac, k + 1, e, sl, e + 2 * (e - sl)), e)
                break
        res['confirmation 1h'] = r

        def nuit_sinon_londres(limite):
            if limite is not None and sl < limite < c0:
                for k in range(i07):
                    if al[k] <= limite:
                        e = min(limite, ao[k])
                        if e <= sl:
                            return net(-1.0, c0)
                        return net(-1.0 if al[k] <= sl else suivre(ah, al, ac, k + 1, e, sl, e + 2 * (e - sl)), e)
            return res['Londres 07h']

        res['repli 30 % la nuit, sinon Londres'] = nuit_sinon_londres(c0 - 0.3 * risque0)
        b = g.assign(bloc=g['date'].dt.hour // 4).groupby('bloc')
        if sens == 1:
            h4 = b.agg(high=('high', 'max'), low=('low', 'min'))
            zones = fvgs(None, h4['high'].to_numpy(), h4['low'].to_numpy(), None)
        else:
            h4 = b.agg(high=('low', 'min'), low=('high', 'max'))
            zones = fvgs(None, -h4['high'].to_numpy(), -h4['low'].to_numpy(), None)
        zones = [z for z in zones if z[1] < c0]
        res['FVG 4h la nuit, sinon Londres'] = nuit_sinon_londres(max(z[1] for z in zones) if zones else None)
        for v in VARIANTES:
            lignes.append(dict(base, variante=v, r=round(res[v], 4)))
    return lignes


def main():
    lignes = []
    for p in PAIRES_DEMO + PAIRES_AUTRES:
        if os.path.exists(f'data/prix/yahoo/{p}_1h.csv'):
            lignes += signaux(p)
    t = pd.DataFrame(lignes)
    t['groupe'] = np.where(t['paire'].isin(PAIRES_DEMO), '10 paires', 'autres paires')
    t.to_csv(f'{SORTIE}/entrees_trades.csv', index=False)
    w = t.pivot_table(index=['paire', 'date', 'sens', 'mlq', 'groupe'], columns='variante', values='r').reset_index()
    sous = {'achats MLQ, 10 paires (règle en démo)': (w['sens'] == 'achat') & w['mlq'] & (w['groupe'] == '10 paires'),
            'achats MLQ, autres paires': (w['sens'] == 'achat') & w['mlq'] & (w['groupe'] == 'autres paires'),
            'toutes englobantes, 10 paires': w['groupe'] == '10 paires',
            'toutes englobantes, autres paires': w['groupe'] == 'autres paires'}
    res = []
    for nom, m in sous.items():
        s = w[m]
        for v in VARIANTES:
            d = s[v] - s['clôture']
            res.append(dict(sous_ensemble=nom, variante=v, signaux=len(s), trades=int((s[v] != 0).sum()),
                            r_par_signal=round(s[v].mean(), 3), ecart_vs_cloture=round(d.mean(), 3),
                            erreur_type_ecart=round(d.std() / np.sqrt(len(s)), 3)))
    r = pd.DataFrame(res)
    r.to_csv(f'{SORTIE}/entrees_resultats.csv', index=False)
    pd.set_option('display.width', 200)
    for nom in sous:
        print('\n==', nom)
        print(r[r['sous_ensemble'] == nom].drop(columns='sous_ensemble').to_string(index=False))


if __name__ == '__main__':
    main()
