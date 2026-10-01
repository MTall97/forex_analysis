#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Télécharge les captures TradingView (liens https://www.tradingview.com/x/<ID>/)
publiées dans le canal, pour une période donnée.

Chaque lien /x/<ID>/ correspond à une image statique :
    https://s3.tradingview.com/snapshots/<première lettre de l'ID en minuscule>/<ID>.png

Usage :
    # septembre 2026 uniquement
    python scripts/fetch_tradingview_snapshots.py --start 2026-09-01 --end 2026-10-01 --out assets/tradingview
    # tout le canal (~1 300 liens), 16 téléchargements en parallèle
    python scripts/fetch_tradingview_snapshots.py --start 2019 --end 2027 --workers 16

Les images sont nommées d'après le premier message qui publie le lien :
    <out>/<AAAA-MM>/<AAAA-MM-JJ>_<HHhMM>_msg<id>_<idTradingView>.png   (heure UTC)
Un lien republié plus tard n'est téléchargé qu'une fois ; <out>/index.csv liste
toutes les occurrences : id_message, date_utc, id_tradingview, fichier, statut, texte.
Relancer le script ne retélécharge pas les images déjà présentes.
Nécessite l'accès réseau à s3.tradingview.com.
"""

import argparse
import csv
import json
import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor

LINK_RE = re.compile(r'tradingview\.com/x/([A-Za-z0-9]+)/?')


def snapshot_url(tv_id: str) -> str:
    return f"https://s3.tradingview.com/snapshots/{tv_id[0].lower()}/{tv_id}.png"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch_snapshot(tv_id: str) -> bytes:
    """Essaie l'URL directe ; à défaut, lit l'image annoncée (og:image) par la page du lien."""
    try:
        return fetch(snapshot_url(tv_id))
    except Exception:
        page = fetch(f"https://www.tradingview.com/x/{tv_id}/").decode('utf-8', 'replace')
        m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', page)
        if not m:
            raise
        return fetch(m.group(1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--messages', default='data/telegram_messages.jsonl')
    p.add_argument('--start', default='2026-09-01')
    p.add_argument('--end', default='2026-10-01T23:59:59')
    p.add_argument('--out', default='assets/tradingview')
    p.add_argument('--workers', type=int, default=16)
    args = p.parse_args()

    os.makedirs(args.out, exist_ok=True)
    with open(args.messages, encoding='utf-8') as fh:
        msgs = [json.loads(l) for l in fh]
    refs = [(m, tv_id) for m in msgs if args.start <= m['date_utc'] <= args.end
            for tv_id in LINK_RE.findall(m['text'])]

    # chemin de chaque image = date du premier message qui publie le lien
    first = {}
    for m, tv_id in refs:
        if tv_id not in first:
            d = m['date_utc']
            name = f"{d[:10]}_{d[11:13]}h{d[14:16]}_msg{m['id']}_{tv_id}.png"
            first[tv_id] = os.path.join(args.out, d[:7], name)

    def download(tv_id):
        path = first[tv_id]
        if os.path.exists(path):
            return tv_id, 'deja_present'
        try:
            data = fetch_snapshot(tv_id)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as out:
                out.write(data)
            return tv_id, 'ok'
        except Exception as e:  # réseau bloqué, lien supprimé, etc.
            return tv_id, f'echec: {e}'

    unique = list(first)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        status = dict(pool.map(download, unique))
    rows = [[m['id'], m['date_utc'], tv_id, first[tv_id], status[tv_id],
             m['text'][:120].replace('\n', ' ')] for m, tv_id in refs]

    with open(os.path.join(args.out, 'index.csv'), 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['id_message', 'date_utc', 'id_tradingview', 'fichier', 'statut', 'texte'])
        w.writerows(rows)
    ok = sum(1 for v in status.values() if v in ('ok', 'deja_present'))
    print(f"{len(unique)} liens uniques, {ok} images disponibles -> {args.out}")


if __name__ == '__main__':
    main()
