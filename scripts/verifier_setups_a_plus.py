#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Les trades qu'Amirou qualifie de « setup A+ » : son playbook leur fixe un taux de réussite de 90 % ou plus
(« Dans mon playbook le setup A+ signifie un trade qui a plus de 90 % de... », #12503 ; « setup A+ donc 90 % de
probabilité », #15562). Que donnent-ils ?

Méthode : chaque message contenant « A+ » est rapproché du trade vérifié le plus proche (data/verification_trades.csv,
écart d'au plus 6 messages) ; on ne garde le rapprochement que si la paire du trade est citée dans le message, ou si
le message ne cite aucune paire et suit le trade de 2 messages au plus. Les trades d'octobre 2026, vérifiés à part
(data/octobre_2026/trades.csv), sont ajoutés à la main. Le rapprochement est automatique : chaque ligne donne l'id du
message et celui du trade pour pouvoir la contrôler.
Sortie : data/setups_a_plus.csv et bilan à l'écran.
"""
import json
import os
import re

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
P = r'(EUR|GBP|AUD|NZD|USD|CAD|CHF|JPY|XAU|NOK)'
# octobre 2026 : message « A+ » -> trade (data/octobre_2026/trades.csv)
OCTOBRE = {15562: 15560, 15580: 15576, 15625: 15624}


def paires(t):
    t = t.upper().replace('GOLD', 'XAUUSD')
    return {a + b for a, b in re.findall(P + r'\s?/?' + P, t)}


def main():
    msgs = [json.loads(l) for l in open('data/telegram_messages.jsonl', encoding='utf-8')]
    v = pd.read_csv('data/verification_trades.csv').dropna(subset=['id_message'])
    lignes = []
    for m in msgs:
        t = (m['text'] or '').replace('A +', 'A+')
        if 'A+' not in t or m['id'] in OCTOBRE:
            continue
        c = v[(v['id_message'] - m['id']).abs() <= 6]
        if not len(c):
            continue
        x = c.iloc[(c['id_message'] - m['id']).abs().argsort()[:1]].iloc[0]
        ps = paires(t)
        if not (x['paire'] in ps or (not ps and abs(x['id_message'] - m['id']) <= 2)):
            continue
        lignes.append(dict(id_message_a_plus=m['id'], date=m['date_utc'][:16], texte=t[:120].replace('\n', ' '),
                           id_trade=int(x['id_message']), paire=x['paire'], sens=x['sens'], statut=x['statut_rejeu'],
                           issue=x['issue_rejeu'], r=x['r']))
    o = pd.read_csv('data/octobre_2026/trades.csv')
    o['id'] = o['id'].astype(str)
    for ida, idt in OCTOBRE.items():
        x = o[o['id'] == str(idt)].iloc[0]
        m = next(mm for mm in msgs if mm['id'] == ida)
        issue = 'non déclenché' if 'déclenché' in str(x['issue']) else x['issue']
        lignes.append(dict(id_message_a_plus=ida, date=m['date_utc'][:16], texte=m['text'][:120].replace('\n', ' '),
                           id_trade=idt, paire=x['paire'], sens=x['sens'], statut=x['statut'], issue=issue, r=x['r']))
    d = pd.DataFrame(lignes).drop_duplicates('id_trade').sort_values('date')
    d.to_csv('data/setups_a_plus.csv', index=False)
    pd.set_option('display.width', 220)
    pd.set_option('display.max_colwidth', 50)
    print(d[['id_message_a_plus', 'date', 'id_trade', 'paire', 'statut', 'issue', 'r']].to_string(index=False))
    for st in ['annoncé', 'après coup']:
        x = d[d['statut'] == st]
        ex = x.dropna(subset=['r'])
        n, g = len(ex), int((ex['r'] > 0).sum())
        print(f"\n{st} : {len(x)} trades A+, {n} exécutés : {g} gagnants, {int((ex['r'] < 0).sum())} perdants, "
              f"{len(x) - n} non déclenchés ou invérifiables ; réussite {g / n:.0%}" + (f", R moyen {ex['r'].mean():+.2f}" if n else ''))
    from math import comb
    x = d[(d['statut'] == 'annoncé')].dropna(subset=['r'])
    n, g = len(x), int((x['r'] > 0).sum())
    p = sum(comb(n, k) * 0.9 ** k * 0.1 ** (n - k) for k in range(g + 1))
    print(f"Probabilité d'avoir {g} gagnants ou moins sur {n} si la réussite était de 90 % : {p:.1e}")


if __name__ == '__main__':
    main()
