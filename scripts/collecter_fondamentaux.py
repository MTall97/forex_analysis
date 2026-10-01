#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Collecte les données fondamentales utilisées par le modèle (data/fondamental/) :

1. calendrier.csv  : calendrier économique TradingView (actuel, consensus, précédent, importance)
                     pour US, EU, DE, GB, JP, AU, NZ, CA, CH, CN, de 2019 à aujourd'hui ;
2. cot.csv         : positionnement CFTC « Traders in Financial Futures » (fonds à effet de levier
                     et gérants d'actifs) sur les contrats de devises, hebdomadaire ;
3. taux.csv        : taux directeurs quotidiens des banques centrales (BIS, série WS_CBPOL).

Chaque série est datée à sa date de PUBLICATION (calendrier : heure de l'annonce ; COT : le
vendredi suivant le mardi de référence ; taux : date d'effet), pour éviter toute fuite d'information.

Usage :
    python scripts/collecter_fondamentaux.py [--debut 2019-01-01]
"""

import argparse
import csv
import io
import json
import os
import time
import urllib.request
import zipfile
from datetime import datetime, timedelta

DOSSIER = 'data/fondamental'
PAYS = 'US,EU,DE,GB,JP,AU,NZ,CA,CH,CN'
UA = {'User-Agent': 'Mozilla/5.0', 'Origin': 'https://www.tradingview.com', 'Referer': 'https://www.tradingview.com/'}


def lire(url, essais=5):
    for i in range(essais):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception:
            time.sleep(3 * (i + 1))
    raise RuntimeError(url)


def calendrier(debut):
    sortie = f'{DOSSIER}/calendrier.csv'
    champs = ['date', 'pays', 'devise', 'titre', 'indicateur', 'categorie', 'periode', 'importance',
              'actuel', 'consensus', 'precedent', 'unite']
    lignes, vus = [], set()
    d = debut
    while d < datetime.utcnow() + timedelta(days=7):
        f = d + timedelta(days=7)
        url = ('https://economic-calendar.tradingview.com/events?from=' + d.strftime('%Y-%m-%dT00:00:00.000Z') +
               '&to=' + f.strftime('%Y-%m-%dT00:00:00.000Z') + '&countries=' + PAYS)
        for e in json.loads(lire(url)).get('result', []):
            if e['id'] in vus:
                continue
            vus.add(e['id'])
            lignes.append([e.get('date'), e.get('country'), e.get('currency'), e.get('title'), e.get('indicator'),
                           e.get('category'), e.get('period'), e.get('importance'), e.get('actual'),
                           e.get('forecast'), e.get('previous'), e.get('scale') or e.get('unit') or ''])
        d = f
        time.sleep(0.3)
    lignes.sort(key=lambda l: l[0] or '')
    with open(sortie, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(champs)
        w.writerows(lignes)
    print(f"calendrier : {len(lignes)} annonces -> {sortie}")


CONTRATS = {'EURO FX': 'EUR', 'BRITISH POUND': 'GBP', 'JAPANESE YEN': 'JPY', 'AUSTRALIAN DOLLAR': 'AUD',
            'NZ DOLLAR': 'NZD', 'NEW ZEALAND DOLLAR': 'NZD', 'CANADIAN DOLLAR': 'CAD', 'SWISS FRANC': 'CHF',
            'USD INDEX': 'USD', 'U.S. DOLLAR INDEX': 'USD'}


def cot(debut):
    sortie = f'{DOSSIER}/cot.csv'
    lignes = []
    for an in range(debut.year, datetime.utcnow().year + 1):
        z = zipfile.ZipFile(io.BytesIO(lire(f'https://www.cftc.gov/files/dea/history/fut_fin_txt_{an}.zip')))
        texte = z.read(z.namelist()[0]).decode('latin-1')
        for r in csv.DictReader(io.StringIO(texte)):
            nom = r['Market_and_Exchange_Names'].split(' - ')[0].strip().upper()
            devise = CONTRATS.get(nom)
            if not devise:
                continue
            ref = datetime.strptime(r['Report_Date_as_YYYY-MM-DD'][:10], '%Y-%m-%d')
            def n(c):
                return float(r[c].replace(',', '') or 0)
            oi = n('Open_Interest_All')
            lev = n('Lev_Money_Positions_Long_All') - n('Lev_Money_Positions_Short_All')
            am = n('Asset_Mgr_Positions_Long_All') - n('Asset_Mgr_Positions_Short_All')
            lignes.append([(ref + timedelta(days=3)).strftime('%Y-%m-%d'), ref.strftime('%Y-%m-%d'), devise,
                           oi, lev, am, round(lev / oi, 4) if oi else 0, round(am / oi, 4) if oi else 0])
    lignes.sort()
    with open(sortie, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['publication', 'reference', 'devise', 'open_interest', 'fonds_levier_net', 'gerants_net',
                    'fonds_levier_net_oi', 'gerants_net_oi'])
        w.writerows(lignes)
    print(f"COT : {len(lignes)} lignes -> {sortie}")


BIS = {'US': 'USD', 'XM': 'EUR', 'GB': 'GBP', 'JP': 'JPY', 'AU': 'AUD', 'NZ': 'NZD', 'CA': 'CAD', 'CH': 'CHF'}


def taux(debut):
    sortie = f'{DOSSIER}/taux.csv'
    lignes = []
    for code, devise in BIS.items():
        url = f'https://stats.bis.org/api/v1/data/WS_CBPOL/D.{code}/all?startPeriod={debut:%Y-%m-%d}&format=csv'
        for r in csv.DictReader(io.StringIO(lire(url).decode('utf-8'))):
            v = r.get('OBS_VALUE')
            if v not in (None, '', 'NaN'):
                lignes.append([r['TIME_PERIOD'], devise, float(v)])
    lignes.sort()
    with open(sortie, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['date', 'devise', 'taux_directeur'])
        w.writerows(lignes)
    print(f"taux : {len(lignes)} lignes -> {sortie}")


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--debut', default='2019-01-01')
    a.add_argument('--seulement', nargs='*', default=['taux', 'cot', 'calendrier'])
    args = a.parse_args()
    os.makedirs(DOSSIER, exist_ok=True)
    debut = datetime.strptime(args.debut, '%Y-%m-%d')
    for f in args.seulement:
        globals()[f](debut)


if __name__ == '__main__':
    main()
