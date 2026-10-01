#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Construit un registre des trades du canal (2019-2026) à partir de data/telegram_messages.jsonl :
chaque annonce d'entrée est reliée aux messages d'issue (TP, SL, BE, raté, profit flottant)
qui citent la même paire dans les 10 jours, ou qui y répondent directement.

Règles :
- entrée   : ordre explicite (sell/buy now, vendez/achetez, sell/buy limit, « je viens de me
             positionner », « je vends X maintenant »…) avec une paire identifiable ;
- issue    : messages classés par scripts/extract_trade_events.py (même vocabulaire) ;
- issue finale : TP > SL > BE > raté (non déclenché) > profit flottant > inconnue,
  en prenant le dernier événement décisif (un SL après un passage à BE compte comme BE).
- un message d'issue sans paire est rattaché au trade auquel il répond (reply_to), sinon
  au seul trade ouvert s'il n'y en a qu'un.

Limites : extraction par mots-clés. Les trades annoncés seulement en image (paire non écrite)
ou seulement dans les groupes payants n'apparaissent pas. Les septembres ont été vérifiés
à la main dans analyses/TRADES_SEPTEMBRE.md, qui fait foi en cas d'écart.

Corrections manuelles : data/trades_corrections.csv (clé E<id entrée> ou I<id 1re issue>),
appliquées à la fin ; issue « gain » = SL remonté en profit puis position fermée.

Sortie : data/trades.csv
"""

import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from extract_trade_events import classify  # noqa: E402

DEV = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CAD', 'CHF', 'JPY']
PAIRES = [a + b for a in DEV for b in DEV if a != b]
PAIR_RE = re.compile(r'\b(' + '|'.join(PAIRES) + r'|XAUUSD|GOLD|GJ|US30)\b|\b(l\'or|or)\b(?= (va|est|a |sera))', re.I)
ALIAS = {'GOLD': 'XAUUSD', 'GJ': 'GBPJPY', "L'OR": 'XAUUSD', 'OR': 'XAUUSD'}
VENTE = re.compile(r"\b(sell|vend\w*|vente|short|baiss\w*)\b", re.I)
ACHAT = re.compile(r"\b(buy|ach[eè]t\w*|achat|long|hauss\w*)\b", re.I)
ENTREE = re.compile(
    r"\b(sell|buy) (now|limit|stop|at market)|\b(sell|buy) \w+ (now )?at market|\bvendez\b|\bachetez\b|"
    r"je viens de me positionner|je me repositionne|reprenez position|je (vend|vends|ach[eè]te) \w+ (maintenant|now)|"
    r"\b(sell|buy) limit\b|trades? (sont )?a prendre maintenant|je rentre (en|sur)|"
    r"(il est temps|temps) (mtn |maintenant )?d'(acheter|vendre)|\b(sell|buy) \w+\b(?=.*(stop loss|sl|tp))", re.I)
DECISIFS = ('tp', 'sl', 'be', 'rate')
PLUSIEURS = re.compile(r"\b(\d|deux|trois|tous|toutes|les) (nos |mes |les )?(\d )?trades\b|tous nos trades|nos \dtrades", re.I)


def paires(texte):
    out = []
    for m in PAIR_RE.finditer(texte):
        p = (m.group(1) or m.group(2) or '').upper()
        p = ALIAS.get(p, p)
        if p and p not in out:
            out.append(p)
    return out


def sens(texte):
    v, a = VENTE.search(texte), ACHAT.search(texte)
    if v and not a:
        return 'vente'
    if a and not v:
        return 'achat'
    if v and a:
        return 'vente' if v.start() < a.start() else 'achat'
    return '?'


def main():
    msgs = [json.loads(l) for l in open('data/telegram_messages.jsonl', encoding='utf-8')]
    par_id = {m['id']: m for m in msgs}
    trades, ouverts = [], []

    def sens_avant(paire, d):
        """Sens annoncé dans le dernier message citant la paire (10 jours avant)."""
        for m2 in reversed(msgs):
            d2 = datetime.fromisoformat(m2['date_utc'])
            if d2 >= d:
                continue
            if d - d2 > timedelta(days=10):
                break
            if paire in paires(m2['text']):
                s2 = sens(m2['text'])
                if s2 != '?':
                    return s2
        return '?'
    for m in msgs:
        if m.get('forwarded_from') and not re.search(r'amirou|halal', m['forwarded_from'], re.I):
            continue
        t = m['text']
        if not t:
            continue
        d = datetime.fromisoformat(m['date_utc'])
        ouverts = [tr for tr in ouverts if d - tr['_d'] <= timedelta(days=10)]
        ps = paires(t)
        ev = classify(t)
        if ENTREE.search(t) and ps and ev in (None, 'entree', 'profit_flottant'):
            for p in ps[:1]:
                tr = {'id_entree': m['id'], 'date_utc': m['date_utc'], 'paire': p, 'sens': sens(t),
                      'evenements': [], 'ids_issue': [], 'texte_entree': t[:160].replace('\n', ' '), '_d': d}
                trades.append(tr)
                ouverts.append(tr)
            continue
        if ev in DECISIFS + ('profit_flottant',):
            cible = []
            if m.get('reply_to') in par_id:
                cible = [tr for tr in ouverts if tr['id_entree'] == m['reply_to']]
            if not cible and ps:
                cible = [tr for tr in ouverts if tr['paire'] in ps]
            if not cible and not ps and (len(ouverts) == 1 or PLUSIEURS.search(t)):
                cible = [tr for tr in ouverts if not any(e in DECISIFS for e in tr['evenements'])] or ouverts
            if not cible and ps and ev in DECISIFS:
                # issue annoncée sans entrée retrouvée : le trade existe quand même
                for p in ps[:1]:
                    tr = {'id_entree': '', 'date_utc': m['date_utc'], 'paire': p, 'sens': sens_avant(p, d),
                          'evenements': [], 'ids_issue': [], 'texte_entree': '(entrée non retrouvée)', '_d': d}
                    trades.append(tr)
                    cible = [tr]
            for tr in cible:
                tr['evenements'].append(ev)
                tr['ids_issue'].append(m['id'])

    corr = {}
    if os.path.exists('data/trades_corrections.csv'):
        with open('data/trades_corrections.csv', encoding='utf-8') as fh:
            corr = {r['cle']: r for r in csv.DictReader(fh)}

    ecrits = 0
    with open('data/trades.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['id_entree', 'date_utc', 'paire', 'sens', 'issue', 'evenements', 'ids_issue', 'texte_entree'])
        for tr in trades:
            ev = tr['evenements']
            dec = [e for e in ev if e in DECISIFS]
            if dec:
                issue = dec[0]
                if issue == 'be' and 'tp' in dec:
                    issue = 'tp'
            elif 'profit_flottant' in ev:
                issue = 'profit_flottant'
            else:
                issue = 'inconnue'
            c = corr.get(f"E{tr['id_entree']}") or (corr.get(f"I{tr['ids_issue'][0]}") if tr['ids_issue'] else None)
            if c and c['exclure'] == 'oui':
                continue
            if c:
                issue = c['issue'] or issue
                tr['sens'] = c['sens'] or tr['sens']
            ecrits += 1
            w.writerow([tr['id_entree'], tr['date_utc'], tr['paire'], tr['sens'], issue, ' '.join(ev),
                        ' '.join(map(str, tr['ids_issue'])), tr['texte_entree']])
    print(f"{ecrits} trades -> data/trades.csv")


if __name__ == '__main__':
    main()
