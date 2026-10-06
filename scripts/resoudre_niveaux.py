#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transforme les lectures OCR brutes (data/captures_niveaux.csv) en trades cohérents.

Pour chaque capture :
1. candidats « objectif » (étiquettes vert-bleu), « stop » (rouges : le vrai stop ou le prix
   courant) et « entrée » (grises : la vraie entrée, mais aussi des graduations de l'axe) ;
2. on écarte les graduations : nombres « ronds » (moins de décimales que les autres) ;
3. on garde la combinaison (entrée, stop, objectif) où le stop et l'objectif sont de part et
   d'autre de l'entrée, avec un ratio objectif/risque entre 0,5 et 30 ;
4. la paire est vérifiée (ou retrouvée si l'OCR ne l'a pas lue) en comparant l'entrée au prix
   réel du jour (Yahoo, à 1,5 % près) parmi 27 instruments ; en cas d'ambiguïté, on garde la
   paire lue par l'OCR ou celle citée dans les messages voisins.

Sortie : data/captures_trades.csv (même colonnes que captures_niveaux.csv, niveaux résolus).
"""

import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402

INSTRUMENTS = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'USDCHF', 'EURJPY', 'GBPJPY',
               'AUDJPY', 'NZDJPY', 'CADJPY', 'CHFJPY', 'EURGBP', 'GBPAUD', 'EURAUD', 'EURNZD', 'EURCAD',
               'EURCHF', 'GBPNZD', 'GBPCAD', 'GBPCHF', 'AUDNZD', 'AUDCAD', 'NZDCAD', 'XAUUSD', 'US30']


def decimales(x):
    s = repr(float(x))
    return len(s.split('.')[1].rstrip('0')) if '.' in s else 0


def prix_du_jour(paire, date):
    df = prix_yahoo._charger(paire, '1d')
    d = df[(df['date'] <= date) & (df['date'] >= date - timedelta(days=5))]
    return None if d.empty else (float(d['low'].min()), float(d['high'].max()))


def paires_compatibles(e, date):
    out = []
    for p in INSTRUMENTS:
        r = prix_du_jour(p, date)
        if r and r[0] * 0.985 <= e <= r[1] * 1.015:
            out.append(p)
    return out


def main():
    msgs = [json.loads(l) for l in open('data/telegram_messages.jsonl', encoding='utf-8')]
    pos = {m['id']: i for i, m in enumerate(msgs)}
    rx = re.compile(r'\b(' + '|'.join(INSTRUMENTS) + r'|GOLD|GJ)\b', re.I)

    def paires_voisines(id_msg):
        i = pos.get(int(id_msg))
        if i is None:
            return []
        out = []
        for m in msgs[max(0, i - 4):i + 4]:
            for x in rx.findall(m['text']):
                x = {'GOLD': 'XAUUSD', 'GJ': 'GBPJPY'}.get(x.upper(), x.upper())
                if x not in out:
                    out.append(x)
        return out

    lignes = list(csv.DictReader(open('data/captures_niveaux.csv', encoding='utf-8')))
    sortie, n_ok = [], 0
    for l in lignes:
        tps = [float(x) for x in l['tp_lus'].split()]
        sls = [float(x) for x in l['sl_lus'].split()]
        ens = [float(x) for x in l['entrees_lues'].split()]
        meilleur = None
        if tps and sls and ens:
            dmax = max(decimales(x) for x in ens + tps + sls)
            ens_f = [x for x in ens if decimales(x) >= dmax - 1] or ens
            for e in ens_f:
                for tp in tps:
                    for sl in sls:
                        if not ((sl < e < tp) or (tp < e < sl)):
                            continue
                        rr = abs(tp - e) / abs(e - sl)
                        if not 0.5 <= rr <= 30:
                            continue
                        score = decimales(e) + decimales(sl) + decimales(tp)
                        if meilleur is None or score > meilleur[0]:
                            meilleur = (score, e, sl, tp)
        l = dict(l)
        if meilleur:
            _, e, sl, tp = meilleur
            date = datetime.fromisoformat(l['publication_utc'] or l['date_message'])
            compat = paires_compatibles(e, date)
            paire = l['paire']
            if paire not in compat:
                voisines = [p for p in paires_voisines(l['id_message']) if p in compat]
                paire = voisines[0] if voisines else (compat[0] if len(compat) == 1 else '')
            if paire:
                l.update(paire=paire, entree=e, stop=sl, objectif=tp, sens='achat' if tp > e else 'vente')
                n_ok += 1
            else:
                l.update(entree='', stop='', objectif='', sens='')
        else:
            l.update(entree='', stop='', objectif='', sens='')
        sortie.append(l)
    with open('data/captures_trades.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(sortie[0]))
        w.writeheader()
        w.writerows(sortie)
    print(f"{n_ok} captures avec un trade complet et cohérent -> data/captures_trades.csv")


if __name__ == '__main__':
    main()
