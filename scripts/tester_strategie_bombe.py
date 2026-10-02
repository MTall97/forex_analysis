#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste la « stratégie de la Bombe » (masterclass) sur les bougies horaires Yahoo (déc. 2023 -> sept. 2026).

Règles telles qu'enseignées, traduites en code (vente ; achat symétrique) :
1. Consolidation : les 12 bougies H1 avant l'impulsion tiennent dans 3 ATR horaires.
2. Impulsion : au moins 3 bougies baissières « pleines » d'affilée (corps >= 70 % du range), qui font
   sortir le prix du range de consolidation et parcourent au moins 2,5 ATR horaires.
3. « M » : le marché remonte (retracement interne) sans dépasser le haut de l'impulsion ; variante
   « Fibonacci » : retracement limité à 50 % de l'impulsion.
4. Entrée : à la clôture de la bougie qui casse le dernier creux du retracement.
   Stop initial : au-dessus du plus haut du retracement (+ 2 pips), entre 10 et 60 pips (sinon ignoré).
5. Sortie : pas d'objectif ; trailing stop déplacé au-dessus de chaque nouveau sommet H1 confirmé
   (pivot de 2 bougies de part et d'autre), sortie forcée après 5 jours. Spread déduit.

Témoin : des entrées au hasard (même paire, même heure de la semaine, même sens que l'impulsion
précédente), gérées avec exactement le même stop initial et le même trailing. Si la Bombe ne fait
pas mieux que le témoin, son résultat vient du trailing, pas du setup.

Revendiqué : > 90 % de réussite, 3-4 setups par mois sur l'ensemble des paires, ratios de 1:5 à 1:18,
mercredi meilleur jour.

Sorties : data/bombe_trades.csv, résumé à l'écran.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402
from modele_meta import SPREAD  # noqa: E402

PAIRES = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'EURJPY', 'GBPJPY', 'AUDJPY', 'EURGBP',
          'EURAUD', 'EURNZD', 'GBPAUD']
JOURS = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi', 'dimanche']


def pip(p):
    return 0.01 if p.endswith('JPY') else 0.0001


def pivots(h, l, k=2):
    """Sommets / creux confirmés : indice du pivot -> indice où il devient connu (pivot + k)."""
    n = len(h)
    ph = np.zeros(n, bool)
    pl = np.zeros(n, bool)
    for i in range(k, n - k):
        ph[i] = h[i] == h[i - k:i + k + 1].max()
        pl[i] = l[i] == l[i - k:i + k + 1].min()
    return ph, pl


def gerer(h, l, c, ph, pl, i, sens, entree, sl, pp, maxi=120):
    """Trailing stop sur pivots confirmés ; renvoie (prix de sortie, nombre de bougies)."""
    for j in range(i + 1, min(i + maxi, len(c))):
        if (sens < 0 and h[j] >= sl) or (sens > 0 and l[j] <= sl):
            return sl, j - i
        k = j - 2                                    # pivot confirmé à la bougie j
        if k > i:
            if sens < 0 and ph[k] and h[k] + 2 * pp < sl:
                sl = h[k] + 2 * pp
            if sens > 0 and pl[k] and l[k] - 2 * pp > sl:
                sl = l[k] - 2 * pp
    j = min(i + maxi, len(c)) - 1
    return c[j], j - i


def detecter(p, d, fib=False):
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    t = d.date.to_numpy()
    pp = pip(p)
    atr = pd.Series(h - l).rolling(50).mean().to_numpy()
    ph, pl = pivots(h, l)
    plein = np.abs(c - o) >= 0.7 * (h - l)
    trades = []
    i = 62
    while i < len(c) - 10:
        for sens in (-1, 1):
            n = 0
            while n < 8 and plein[i - n] and np.sign(c[i - n] - o[i - n]) == sens:
                n += 1
            if n < 3:
                continue
            deb = i - n + 1
            hc, lc = h[deb - 12:deb].max(), l[deb - 12:deb].min()
            if hc - lc > 3 * atr[deb]:
                continue
            haut, bas = (max(hc, h[deb]), l[deb:i + 1].min()) if sens < 0 else (h[deb:i + 1].max(), min(lc, l[deb]))
            if sens < 0 and not (c[i] < lc and haut - bas >= 2.5 * atr[i]):
                continue
            if sens > 0 and not (c[i] > hc and haut - bas >= 2.5 * atr[i]):
                continue
            # suivi de l'impulsion puis du « M » (ou « W ») pendant 48 bougies au plus
            ext = bas if sens < 0 else haut                     # extrême de l'impulsion (mis à jour)
            creux_m = None                                     # dernier creux (vente) / sommet (achat) du retracement
            sommet_m = None
            for j in range(i + 1, min(i + 48, len(c) - 1)):
                if sens < 0:
                    if l[j] < ext and creux_m is None:
                        ext = l[j]
                    if h[j] > haut:
                        break                                  # le retracement dépasse le haut de l'impulsion
                    k = j - 2
                    if k > i and ph[k] and h[k] > ext and creux_m is None:
                        sommet_m = h[k]
                    if k > i and pl[k] and sommet_m is not None and l[k] > ext:
                        creux_m = l[k]
                        sommet_m = max(h[k:j + 1].max(), sommet_m)
                    if creux_m is not None and c[j] < creux_m:
                        retr = (h[i + 1:j + 1].max() - ext) / (haut - ext)
                        if fib and retr > 0.5:
                            break
                        sl = h[i + 1:j + 1].max() + 2 * pp
                        risque = sl - c[j]
                        if 10 * pp <= risque <= 60 * pp:
                            sortie, duree = gerer(h, l, c, ph, pl, j, -1, c[j], sl, pp)
                            trades.append(dict(paire=p, date=t[j], sens=-1, entree=c[j], sl=sl, sortie=sortie,
                                               r=(c[j] - sortie) / risque - SPREAD.get(p, 2) * pp / risque,
                                               risque_pips=risque / pp, duree_h=duree, retracement=retr))
                        break
                else:
                    if h[j] > ext and creux_m is None:
                        ext = h[j]
                    if l[j] < bas:
                        break
                    k = j - 2
                    if k > i and pl[k] and l[k] < ext and creux_m is None:
                        sommet_m = l[k]
                    if k > i and ph[k] and sommet_m is not None and h[k] < ext:
                        creux_m = h[k]
                        sommet_m = min(l[k:j + 1].min(), sommet_m)
                    if creux_m is not None and c[j] > creux_m:
                        retr = (ext - l[i + 1:j + 1].min()) / (ext - bas)
                        if fib and retr > 0.5:
                            break
                        sl = l[i + 1:j + 1].min() - 2 * pp
                        risque = c[j] - sl
                        if 10 * pp <= risque <= 60 * pp:
                            sortie, duree = gerer(h, l, c, ph, pl, j, 1, c[j], sl, pp)
                            trades.append(dict(paire=p, date=t[j], sens=1, entree=c[j], sl=sl, sortie=sortie,
                                               r=(sortie - c[j]) / risque - SPREAD.get(p, 2) * pp / risque,
                                               risque_pips=risque / pp, duree_h=duree, retracement=retr))
                        break
            i += 1
            break
        i += 1
    return trades


def temoin(p, d, trades, rng):
    """Entrées au hasard avec le même stop (en pips) et le même trailing."""
    h, l, c = d.high.to_numpy(), d.low.to_numpy(), d.close.to_numpy()
    ph, pl = pivots(h, l)
    pp = pip(p)
    out = []
    for tr in trades:
        for _ in range(5):
            j = int(rng.integers(60, len(c) - 130))
            sens = tr['sens']
            risque = tr['risque_pips'] * pp
            sl = c[j] - sens * risque
            sortie, duree = gerer(h, l, c, ph, pl, j, sens, c[j], sl, pp)
            out.append(dict(paire=p, r=(sortie - c[j]) * sens / risque - SPREAD.get(p, 2) * pp / risque))
    return out


def stats(x):
    x = pd.DataFrame(x)
    if not len(x):
        return 'aucun trade'
    return (f"{len(x)} trades, {(x.r > 0).mean() * 100:.0f} % gagnants, R moyen {x.r.mean():+.2f}, "
            f"médiane {x.r.median():+.2f}, ≥ 5 R : {(x.r >= 5).mean() * 100:.1f} %, max {x.r.max():+.1f} R")


def main():
    rng = np.random.default_rng(0)
    tous, fibo, tem = [], [], []
    for p in PAIRES:
        d = prix_yahoo._charger(p, '1h').copy()
        d['date'] = pd.to_datetime(d.date)
        d = d.reset_index(drop=True)
        tr = detecter(p, d)
        tf = detecter(p, d, fib=True)
        tous += tr
        fibo += tf
        tem += temoin(p, d, tr, rng)
        print(f"  {p} : {len(tr)} setups ({len(tf)} avec retracement <= 50 %)", flush=True)
    df = pd.DataFrame(tous)
    df.to_csv('data/bombe_trades.csv', index=False)
    mois = (df.date.max() - df.date.min()).days / 30.4
    print(f"\nPériode : {df.date.min():%Y-%m-%d} -> {df.date.max():%Y-%m-%d} ({mois:.0f} mois), {len(PAIRES)} paires")
    print(f"Bombe                      : {stats(tous)}  ({len(df) / mois:.1f} setups par mois)")
    print(f"Bombe, retracement <= 50 % : {stats(fibo)}")
    print(f"Témoin (entrées au hasard) : {stats(tem)}")
    df['jour'] = pd.to_datetime(df.date).dt.weekday
    for j in range(5):
        print(f"  {JOURS[j]:<9}: {stats(df[df.jour == j].to_dict('records'))}")


if __name__ == '__main__':
    main()
