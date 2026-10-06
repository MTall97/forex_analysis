#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Télécharge les billets du blog Marc to Market (Marc Chandler, marctomarket.com, plateforme Blogger)
depuis mars 2019, date d'ouverture du canal d'Amirou, via le flux public
/feeds/posts/default?alt=json (150 billets par page).

Sortie : data/marc_to_market/billets.jsonl.gz, une ligne par billet :
  date_utc, titre, url, categories, texte (HTML retiré).
Usage : python scripts/collecter_marc_to_market.py
"""
import gzip
import html
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, 'data', 'marc_to_market', 'billets.jsonl.gz')
URL = 'https://www.marctomarket.com/feeds/posts/default?alt=json&max-results=150&start-index={}'
DEBUT = datetime(2019, 3, 1, tzinfo=timezone.utc)


def texte(h):
    h = re.sub(r'(?is)<(script|style).*?</\1>', ' ', h)
    h = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>', '\n', h)
    h = html.unescape(re.sub(r'<[^>]+>', ' ', h))
    return re.sub(r'[ \t\xa0]+', ' ', re.sub(r'\n\s*\n+', '\n', h)).strip()


def main():
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    billets, debut = [], 1
    while True:
        for essai in range(5):
            try:
                req = urllib.request.Request(URL.format(debut), headers={'User-Agent': 'Mozilla/5.0'})
                d = json.load(urllib.request.urlopen(req, timeout=60))
                break
            except Exception as ex:
                print('nouvel essai', debut, ex)
                time.sleep(5 * (essai + 1))
        entrees = d['feed'].get('entry', [])
        if not entrees:
            break
        fini = False
        for e in entrees:
            date = datetime.fromisoformat(e['published']['$t']).astimezone(timezone.utc)
            if date < DEBUT:
                fini = True
                continue
            url = next((l['href'] for l in e['link'] if l['rel'] == 'alternate'), '')
            billets.append(dict(date_utc=date.strftime('%Y-%m-%dT%H:%M:%S'), titre=e['title']['$t'], url=url,
                                categories=[c['term'] for c in e.get('category', [])],
                                texte=texte(e.get('content', {}).get('$t', ''))))
        print(debut, billets[-1]['date_utc'] if billets else '', flush=True)
        if fini:
            break
        debut += len(entrees)
        time.sleep(1)
    billets.sort(key=lambda b: b['date_utc'])
    with gzip.open(SORTIE, 'wt', encoding='utf-8') as fh:
        for b in billets:
            fh.write(json.dumps(b, ensure_ascii=False) + '\n')
    print(f'{len(billets)} billets -> {SORTIE}')


if __name__ == '__main__':
    main()
