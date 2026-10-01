#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repère dans le canal les messages qui décrivent un événement de trade
(entrée, take profit, stop loss, breakeven, trade raté / annulé) et en tire
des statistiques par année et par mois.

C'est une extraction par mots-clés : elle sert à compter et à retrouver les
messages, pas à reconstituer chaque trade. Un même trade peut produire plusieurs
événements (entrée, BE, TP), et un message ambigu peut être mal classé. Les
résultats de septembre ont été vérifiés à la main (analyses/TRADES_SEPTEMBRE.md).

Usage :
    python scripts/extract_trade_events.py            # écrit data/trade_events.csv + résumé
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict

PAIRS = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CAD', 'CHF', 'JPY']
PAIR_RE = re.compile(r'\b(' + '|'.join(a + b for a in PAIRS for b in PAIRS if a != b)
                     + r'|XAUUSD|GOLD|US30|GJ)\b', re.I)

# L'ordre compte : le premier motif trouvé donne le type de l'événement.
EVENT_PATTERNS = [
    ('rate', r"rat[ée] (notre |le |ce )?trade|rat[ée] de (quelques|justesse|\d+ ?pips)|n'a pas (eu|donné) d'entr|pas eu d'entr|"
             r"refus[ée] de toucher|annulez|sans (être|etre) d[ée]clench|non ex[ée]cut|avort[ée]|plus revenu a notre point|"
             r"sans qu'on puisse|pas (eu |de )?(de )?point d'entr|n'a pas (ete|été) touch|je n'ai pas pris|ne plus le faire|"
             r"que je n'ai pas pris|sans nous|(on |nous )?(n')?a(vons)? pas pris (de )?position"),
    ('sl', r"\b(sl|stop ?loss) (a |à )?(été )?touch|touch[ée]r? (notre |mon |le )?(sl|stop)|\bsl touch|dommage,? sl|"
           r"nous a fait sortir|m'a fait sortir|fait du mal"),
    ('tp', r"\b(tp|take ?profit) (a |à )?(été )?(touch|atteint|hit)|touch[ée] (le |notre |mon )?(tp|take profit|profit)|"
           r"tp sur |tp hit|premier tp|a touché profit|cashout|parti direct au tp"),
    ('be', r"(?<!youtu\.)\bBE\b|(?i:\b(a|à|au) be\b|breakeven|break even)|(?i:stop loss (a|à) l'entr|sl (a|à) l'entr|risque z[ée]ro)|"
           r"(?i:(bougez|mettez) (le |votre )?(sl|stop loss) en profit)"),
    ('entree', r"\b(sell|buy) (now|limit|stop)\b|\b(sell|buy) \w+ (now )?at market|vendez|achetez|je viens de me positionner|"
               r"je (vend|vends|ach[eè]te) \w+ maintenant|sell limit|buy limit|trades? (sont )?a prendre maintenant|"
               r"je me repositionne|reprenez position"),
    ('profit_flottant', r"en profit|floating|flottant|en route"),
]
# « BE » seul n'est compté qu'en majuscules (sinon l'anglais « be » est capté)
EVENT_RES = [(name, re.compile(p) if name == 'be' else re.compile(p, re.I)) for name, p in EVENT_PATTERNS]
MONEY_RE = re.compile(r'(-?\d[\d  ]*(?:[.,]\d+)?) ?(\$|usd|dollars)', re.I)
PIPS_RE = re.compile(r'(\d[\d  ]*) ?pips', re.I)


# Formulations qui décrivent un événement qui n'a PAS eu lieu (« presque touché le TP »…)
NEAR_MISS_RE = re.compile(r"presque touch|faillit|failli toucher|a deux doigts", re.I)


def classify(text):
    if NEAR_MISS_RE.search(text):
        return None
    for name, rx in EVENT_RES:
        if rx.search(text):
            return name
    return None


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'data/telegram_messages.jsonl'
    out = sys.argv[2] if len(sys.argv) > 2 else 'data/trade_events.csv'
    with open(src, encoding='utf-8') as fh:
        msgs = [json.loads(l) for l in fh]

    rows = []
    for m in msgs:
        if m.get('forwarded_from') and 'amirou' not in m['forwarded_from'].lower() \
                and 'halal' not in m['forwarded_from'].lower():
            continue  # résultats de membres transférés : exclus
        text = m['text']
        ev = classify(text) if text else None
        if not ev:
            continue
        pairs = sorted({p.upper().replace('GJ', 'GBPJPY').replace('GOLD', 'XAUUSD')
                        for p in PAIR_RE.findall(text)})
        money = MONEY_RE.search(text)
        pips = PIPS_RE.search(text)
        rows.append({
            'id_message': m['id'], 'date_utc': m['date_utc'], 'evenement': ev,
            'paires': ' '.join(pairs), 'photo': m.get('photo') or '',
            'montant': money.group(0) if money else '', 'pips': pips.group(0) if pips else '',
            'texte': text[:200].replace('\n', ' '),
        })

    with open(out, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    by_year = defaultdict(Counter)
    for r in rows:
        by_year[r['date_utc'][:4]][r['evenement']] += 1
    cols = ['entree', 'tp', 'sl', 'be', 'rate', 'profit_flottant']
    print(f"{len(rows)} messages-événements -> {out}\n")
    print('| Année | ' + ' | '.join(cols) + ' | TP / (TP+SL) |')
    print('|---|' + '---|' * (len(cols) + 1))
    for y in sorted(by_year):
        c = by_year[y]
        ratio = c['tp'] / (c['tp'] + c['sl']) if c['tp'] + c['sl'] else 0
        print(f"| {y} | " + ' | '.join(str(c[k]) for k in cols) + f" | {ratio:.0%} |")
    tot = sum(by_year.values(), Counter())
    ratio = tot['tp'] / (tot['tp'] + tot['sl'])
    print('| **Total** | ' + ' | '.join(f"**{tot[k]}**" for k in cols) + f" | **{ratio:.0%}** |")


if __name__ == '__main__':
    main()
