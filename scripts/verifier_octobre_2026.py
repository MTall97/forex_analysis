#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trades d'Amirou du 02/10 au 14/10/2026 (messages #15536 à #15629, export ChatExport_2026-10-14, plus les messages du
14/10 au soir transmis en capture par l'utilisateur) : niveaux lus sur
les captures, puis rejeu sur les cours horaires Yahoo à partir de l'heure de publication dans le canal.

Statut :
- « annoncé » : le plan est publié avant que le prix n'atteigne l'entrée ; on rejoue l'ordre (limite ou marché) ;
- « après coup » : le plan est publié alors que le prix a déjà passé l'entrée (capture d'une position en cours ou
  d'un objectif atteint) ; on rejoue quand même le plan depuis l'heure d'entrée visible sur la capture, pour
  savoir s'il a atteint l'objectif, mais il n'était pas copiable.
Dans une même heure, le stop compte avant l'objectif. Sortie : data/octobre_2026/trades.csv
"""
import os

import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)

# id, paire, sens, entrée, stop, objectif, publication (UTC), entrée visible sur la capture (UTC), source
TRADES = [
    (15541, 'EURAUD', 'vente', 1.62505, 1.62912, 1.61567, '2026-10-02 12:21', '2026-10-01 13:00', 'TradingView #15541'),
    (15548, 'USDJPY', 'achat', 157.503, 157.202, 158.106, '2026-10-02 16:35', '2026-10-02 14:45', 'TradingView #15548, MT5 #15549 (2,65 lots, +694,77 $)'),
    (15560, 'EURGBP', 'vente', 0.85000, 0.85149, 0.84694, '2026-10-05 01:22', None, 'capture #15561 (ordre limite)'),
    (15565, 'EURNZD', 'vente', 2.00217, 2.00723, 1.99063, '2026-10-05 14:19', None, 'TradingView #15565, « 0,5 % de risque »'),
    (15576, 'EURUSD', 'vente', 1.12509, 1.12766, 1.11998, '2026-10-07 07:30', '2026-10-06 23:00', 'captures #15576-#15578, MT5 #15584 (2,8 lots)'),
    (15591, 'GBPAUD', 'vente', 1.90001, 1.90414, 1.89069, '2026-10-09 15:50', '2026-10-07 06:00', 'récapitulatif #15591, #15598'),
    (15594, 'EURNZD', 'vente', 1.99982, 2.00332, 1.99235, '2026-10-09 15:50', '2026-10-07 09:00', 'récapitulatif #15594, #15597'),
    (15595, 'XAUUSD', 'achat', 4125.15, 4106.16, 4172.20, '2026-10-09 15:50', '2026-10-08 18:00', 'récapitulatif #15595, #15596'),
    (15615, 'GBPUSD', 'vente', 1.32371, None, None, '2026-10-12 18:38', '2026-10-12 08:00', 'MT5 #15615 (1,66 lots, +529,54 $)'),
    (15620, 'EURUSD', 'vente', 1.11923, 1.12279, 1.11032, '2026-10-14 12:33', '2026-10-13 14:00', 'TradingView #15620-#15621, MT5 #15623 (1,43 lots, +549,12 $)'),
    (15624, 'GBPJPY', 'vente', 209.997, 210.244, 209.455, '2026-10-14 12:40', None, 'TradingView #15624, #15626 (ordre limite sur le MLQ 210.000)'),
    # messages du 14/10 au soir et du 15/10, récupérés sur la version web du canal (scripts/collecter_canal_public.py)
    (15631, 'EURUSD', 'vente', 1.11617, 1.11967, 1.10890, '2026-10-14 18:14', None,
     'TradingView #15631 (4h), « continuation logique », « setup A+ » (#15633) ; « fermez sur eurusd pour l\'instant » (#15636)'),
    (15641, 'AUDJPY', 'vente', 110.002, 110.253, 109.485, '2026-10-15 00:32', None,
     'TradingView #15641 et #15642 (ordre limite sur le MLQ 110.000) ; « mieux vaut rater un bon trade » (#15643)'),
    (15649, 'EURJPY', 'vente', 177.090, 177.347, 176.570, '2026-10-15 12:24', None,
     '« je vais vendre l\'EURJPY tout de suite » (#15648) ; plan modifié #15650 (177.096 / 177.308 / 176.557) et #15653'),
    (15655, 'USDJPY', 'achat', 157.500, 157.150, 158.219, '2026-10-15 13:29', None,
     'annoncé dès #15639 (00h25), annulé #15647, repris #15656 ; #15661 ; « 4 pips » de l\'entrée (#15662, #15666)'),
    (15664, 'EURUSD', 'vente', 1.12084, 1.12340, 1.11565, '2026-10-15 14:48', None, '« Je vend EURUSD maintenant » (#15665)'),
]


def rejouer(h, sens, e, sl, tp, debut, limite):
    x = h[h['date'] >= pd.Timestamp(debut).floor('h')].reset_index(drop=True)
    if not len(x):
        return 'pas de cours', None, None
    s = 1 if sens == 'achat' else -1
    hh = x['high'] if s > 0 else -x['low']
    ll = x['low'] if s > 0 else -x['high']
    E, SL, TP = e * s, (sl * s if sl else None), (tp * s if tp else None)
    i0 = 0
    if limite:
        # ordre limite (repère achat) : exécuté quand le prix descend jusqu'à l'entrée, dans les 5 jours (120 h)
        k = next((i for i in range(min(len(x), 120)) if ll[i] <= E), None)
        if k is None:
            return ('non déclenché' if len(x) >= 120 else 'pas encore déclenché'), None, None
        i0 = k
    if SL is None or TP is None:
        return 'sans stop ni objectif', None, None
    for i in range(i0, len(x)):
        if ll[i] <= SL:
            return 'stop', x['date'][i], -1.0
        if hh[i] >= TP:
            return 'objectif', x['date'][i], round((TP - E) / (E - SL), 2)
    return 'en cours', None, round((x['close'].iat[-1] * s - E) / (E - SL), 2)


def main():
    lignes = []
    for tid, p, sens, e, sl, tp, pub, ent, src in TRADES:
        f = f'data/prix/yahoo/{p}_1h.csv'
        h = pd.read_csv(f, parse_dates=['date']).sort_values('date') if os.path.exists(f) else None
        s = 1 if sens == 'achat' else -1
        if h is None:
            lignes.append(dict(id=tid, paire=p, sens=sens, entree=e, stop=sl, objectif=tp, publication=pub, statut='pas de cours',
                               issue='pas de cours', source=src))
            continue
        # le prix avait-il déjà passé l'entrée à la publication ?
        avant = h[(h['date'] < pd.Timestamp(pub).floor('h'))].tail(1)
        prix_pub = float(avant['close'].iat[0]) if len(avant) else None
        apres_coup = ent is not None
        statut = 'après coup' if apres_coup else 'annoncé'
        # plan annoncé : suivi à partir de l'heure qui suit la publication (la bougie en cours contient des prix antérieurs)
        debut = ent if apres_coup else (pd.Timestamp(pub).floor('h') + pd.Timedelta(hours=1))
        issue, quand, r = rejouer(h, sens, e, sl, tp, debut, limite=not apres_coup)
        rr = round(abs(tp - e) / abs(e - sl), 2) if sl and tp else None
        lignes.append(dict(id=tid, paire=p, sens=sens, entree=e, stop=sl, objectif=tp, ratio=rr, publication=pub,
                           prix_a_la_publication=round(prix_pub, 5) if prix_pub else None, statut=statut, issue=issue,
                           heure_issue=quand, r=r, source=src))
    d = pd.DataFrame(lignes)
    os.makedirs('data/octobre_2026', exist_ok=True)
    d.to_csv('data/octobre_2026/trades.csv', index=False)
    pd.set_option('display.width', 250)
    print(d.drop(columns=['source']).to_string(index=False))


if __name__ == '__main__':
    main()
