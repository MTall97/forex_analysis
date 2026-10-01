#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envoie les images du projet vers le bucket S3 « images-forex-analyse ».

Ce qui est envoyé (les chemins du dépôt sont conservés comme clés S3) :
    ChatExport_2026-10-01/photos/   photos du canal (après tri : trading + conversations)
    assets/tradingview/             captures des liens TradingView
    assets/trades/                  captures citées dans les analyses

Les fichiers déjà présents dans le bucket avec la même taille ne sont pas renvoyés,
on peut donc relancer le script sans risque.

Prérequis :
    pip install boto3
    identifiants AWS valides (aws configure, ou AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY),
    avec les droits s3:ListBucket et s3:PutObject sur le bucket.

Usage :
    python scripts/upload_images_s3.py                       # envoie tout
    python scripts/upload_images_s3.py --dry-run             # liste sans envoyer
    python scripts/upload_images_s3.py --dossiers assets/tradingview
Équivalent en ligne de commande AWS :
    aws s3 sync ChatExport_2026-10-01/photos s3://images-forex-analyse/ChatExport_2026-10-01/photos
"""

import argparse
import mimetypes
import os
from concurrent.futures import ThreadPoolExecutor

DOSSIERS = ['ChatExport_2026-10-01/photos', 'assets/tradingview', 'assets/trades']


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--bucket', default='images-forex-analyse')
    p.add_argument('--dossiers', nargs='+', default=DOSSIERS)
    p.add_argument('--workers', type=int, default=16)
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()

    import boto3
    s3 = boto3.client('s3')

    deja = {}
    for d in args.dossiers:
        for page in s3.get_paginator('list_objects_v2').paginate(Bucket=args.bucket, Prefix=d + '/'):
            for o in page.get('Contents', []):
                deja[o['Key']] = o['Size']

    a_envoyer = []
    for d in args.dossiers:
        for racine, _, fichiers in os.walk(d):
            for f in fichiers:
                chemin = os.path.join(racine, f)
                cle = chemin.replace(os.sep, '/')
                if deja.get(cle) != os.path.getsize(chemin):
                    a_envoyer.append((chemin, cle))

    print(f"{len(a_envoyer)} fichiers à envoyer ({len(deja)} déjà dans s3://{args.bucket})")
    if args.dry_run:
        return

    def envoyer(item):
        chemin, cle = item
        ctype = mimetypes.guess_type(chemin)[0] or 'application/octet-stream'
        s3.upload_file(chemin, args.bucket, cle, ExtraArgs={'ContentType': ctype})
        return cle

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for i, _ in enumerate(pool.map(envoyer, a_envoyer), 1):
            if i % 200 == 0:
                print(f"  {i}/{len(a_envoyer)}")
    print("Terminé.")


if __name__ == '__main__':
    main()
