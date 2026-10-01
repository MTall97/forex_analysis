#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lit par OCR (Tesseract) les niveaux des trades dessinés sur les captures TradingView et
les captures d'écran du canal : paire, unité de temps, date de publication, entrée, stop, objectif.

Principe : l'outil « position longue / courte » de TradingView affiche trois étiquettes de
couleur sur l'axe des prix : objectif (vert-bleu), entrée (gris), stop (rouge). Le script lit
les nombres de l'axe de droite et classe chaque étiquette d'après la couleur de son fond.
Le sens se déduit de la position de l'objectif par rapport à l'entrée.

Entrée : liste des captures à lire (chemin, id du message, date du message), par défaut toutes
les captures TradingView (assets/tradingview/index.csv) et les photos « trading »
(data/photos_classification.csv) à partir de 2021.

Sortie : data/captures_niveaux.csv
Prérequis : apt install tesseract-ocr ; pip install pytesseract pillow numpy

Usage :
    python scripts/lire_captures_ocr.py [--depuis 2021] [--processus 8]
"""

import argparse
import csv
import os
import re
from datetime import datetime, timedelta
from multiprocessing import Pool

os.environ.setdefault('OMP_THREAD_LIMIT', '1')  # un fil par processus Tesseract
import numpy as np
import pytesseract
from PIL import Image

NOMS = {'euro': 'EUR', 'british pound': 'GBP', 'pound': 'GBP', 'australian dollar': 'AUD',
        'new zealand dollar': 'NZD', 'u.s. dollar': 'USD', 'us dollar': 'USD', 'canadian dollar': 'CAD',
        'swiss franc': 'CHF', 'japanese yen': 'JPY', 'gold': 'XAU', 'silver': 'XAG'}
DEV = ['EUR', 'GBP', 'AUD', 'NZD', 'USD', 'CAD', 'CHF', 'JPY', 'XAU']
SYMB = re.compile(r'\b(' + '|'.join(a + b for a in DEV for b in DEV if a != b) + r'|GOLD|US30|NAS100|SPX500)\b')
COULEURS = {  # fond des étiquettes de l'axe des prix
    'tp': [(0, 150, 136), (8, 153, 129), (34, 171, 148), (38, 166, 154), (0, 137, 123)],
    'sl': [(244, 67, 54), (242, 54, 69), (247, 82, 95), (229, 57, 53)],
    'entree': [(120, 123, 134), (93, 96, 107), (134, 137, 147), (106, 109, 120)],
}
MOIS = {m: i + 1 for i, m in enumerate(['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec'])}


def classe_couleur(c):
    best, dist = None, 40
    for nom, refs in COULEURS.items():
        for r in refs:
            d = max(abs(int(c[i]) - r[i]) for i in range(3))
            if d < dist:
                best, dist = nom, d
    return best


def paire_depuis(texte):
    t = texte.lower()
    m = re.search(r'([a-z. ]+?)\s*/\s*([a-z. ]+?)\s*[,·\-]', t)
    if m:
        a = next((v for k, v in NOMS.items() if m.group(1).strip().endswith(k)), None)
        b = next((v for k, v in NOMS.items() if m.group(2).strip().startswith(k)), None)
        if a and b:
            return a + b
    m = SYMB.search(texte.upper().replace(' ', ''))
    if m:
        return m.group(1).replace('GOLD', 'XAUUSD')
    return ''


def date_publication(texte):
    m = re.search(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+(\d{1,2}),\s*(\d{4})\s+(\d{1,2}):(\d{2})(?::\d{2})?\s*(?:(UTC|GMT)\s*([+-]\d{1,2})?|([A-Z]{3}))?', texte, re.I)
    if not m:
        return ''
    d = datetime(int(m.group(3)), MOIS[m.group(1).lower()[:3]], int(m.group(2)), int(m.group(4)), int(m.group(5)))
    off = 0
    if m.group(7):
        off = int(m.group(7))
    elif m.group(8):
        off = {'CDT': -5, 'CST': -6, 'EDT': -4, 'EST': -5, 'BST': 1, 'CET': 1, 'CEST': 2}.get(m.group(8).upper(), 0)
    return (d - timedelta(hours=off)).isoformat()


def lire(item):
    chemin, id_msg, date_msg = item
    try:
        im = Image.open(chemin).convert('RGB')
    except Exception:
        return None
    W, H = im.size
    a = np.asarray(im)
    tete = pytesseract.image_to_string(im.crop((0, 0, int(W * 0.8), max(40, int(H * 0.1)))).resize(
        (int(W * 0.8 * 1.5), int(max(40, H * 0.1) * 1.5))))
    paire = paire_depuis(tete)
    if not paire:  # captures de téléphone : symbole souvent en haut ou en bas de l'image
        paire = paire_depuis(pytesseract.image_to_string(im.crop((0, int(H * 0.8), W, H))) + ' ' +
                             pytesseract.image_to_string(im.crop((0, 0, W, int(H * 0.2)))))
    x0 = int(W * 0.80)
    ax = im.crop((x0, 0, W, H))
    niveaux = {'tp': [], 'sl': [], 'entree': []}
    for psm in ('11', '6'):
        d = pytesseract.image_to_data(ax.resize((ax.width * 2, ax.height * 2)), config=f'--psm {psm}',
                                      output_type=pytesseract.Output.DICT)
        for i, t in enumerate(d['text']):
            t = t.strip().replace(',', '.').lstrip('O0') if t.strip().startswith('0.') is False else t.strip()
            t = t.strip().replace(',', '.')
            if not re.fullmatch(r'\d{1,6}\.\d{2,5}', t):
                continue
            x, y, w, h = [d[k][i] // 2 for k in ('left', 'top', 'width', 'height')]
            reg = a[max(0, y - 2):y + h + 2, x0 + max(0, x - 6):x0 + x + w + 6].reshape(-1, 3)
            if not len(reg):
                continue
            # couleur dominante non blanche/noire du fond de l'étiquette
            fond = [p for p in reg if not (min(p) > 235 or max(p) < 30)]
            if not fond:
                continue
            nom = classe_couleur(np.median(np.array(fond), axis=0))
            if nom and float(t) not in niveaux[nom]:
                niveaux[nom].append(float(t))
        if all(niveaux.values()):
            break
    tp, sl, en = (niveaux[k][0] if len(niveaux[k]) == 1 else '' for k in ('tp', 'sl', 'entree'))
    sens = ''
    if tp != '' and en != '':
        sens = 'achat' if tp > en else 'vente'
    elif tp != '' and sl != '':
        sens = 'achat' if tp > sl else 'vente'
    tf = ''
    m = re.search(r'[,·]\s*(\d+[hHDdWwMm]?|1D|4h|1h)\s*[,·]', tete)
    if m:
        tf = m.group(1)
    return [chemin, id_msg, date_msg, paire, tf, date_publication(tete), en, sl, tp, sens,
            ' '.join(map(str, niveaux['tp'])), ' '.join(map(str, niveaux['sl'])), ' '.join(map(str, niveaux['entree']))]


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--depuis', default='2021')
    p.add_argument('--processus', type=int, default=4)
    args = p.parse_args()
    items, vus = [], set()
    with open('assets/tradingview/index.csv', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            f = r['fichier'].replace('\\', '/')
            if r['date_utc'] >= args.depuis and os.path.exists(f) and f not in vus:
                vus.add(f)
                items.append((f, r['id_message'], r['date_utc']))
    with open('data/photos_classification.csv', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            f = 'ChatExport_2026-10-01/' + r['photo']
            if r['categorie'] == 'trading' and r['date_utc'] >= args.depuis and os.path.exists(f):
                items.append((f, r['id_message'], r['date_utc']))
    lignes = []
    with Pool(args.processus) as pool:
        for n, l in enumerate(pool.imap(lire, items, chunksize=4), 1):
            if l:
                lignes.append(l)
            if n % 100 == 0:
                print(f"  {n}/{len(items)}", flush=True)
    lignes.sort(key=lambda l: l[2])
    with open('data/captures_niveaux.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['fichier', 'id_message', 'date_message', 'paire', 'unite_temps', 'publication_utc',
                    'entree', 'stop', 'objectif', 'sens', 'tp_lus', 'sl_lus', 'entrees_lues'])
        w.writerows(lignes)
    complets = sum(1 for l in lignes if l[3] and l[6] != '' and l[7] != '' and l[8] != '')
    print(f"{len(lignes)} captures lues, {complets} avec paire + entrée + stop + objectif -> data/captures_niveaux.csv")


if __name__ == '__main__':
    main()
