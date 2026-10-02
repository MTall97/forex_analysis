#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrait le biais fondamental exprimé par Amirou, devise par devise, à partir :
- des messages du canal (data/telegram_messages.jsonl) ;
- des rapports SignalX en PDF (ChatExport_2026-09-17/rapport Amirou/*.pdf et rapports_pdf/21sep.pdf),
  datés d'après leur nom de fichier.

Méthode (lexique, sans modèle de langage, donc reproductible) :
- on découpe le texte en phrases ;
- une phrase qui cite UNE devise (ou ses synonymes) et contient des mots haussiers
  (haussier, bullish, hawkish, se renforce, acheter, monter…) ou baissiers (baissier, bearish,
  dovish, faiblesse, couler, vendre…) donne +1 ou -1 à cette devise ;
- une phrase qui cite une PAIRE avec un sens (« vendre EURUSD », « EURUSD va couler ») donne
  ±1 à la devise de base et l'inverse à la devise de cotation ;
- les négations simples (« pas haussier ») inversent le signe ;
- les phrases conditionnelles ou interrogatives (« si », « pourrait », « ? ») sont ignorées.

Sortie : data/fondamental/biais_amirou.csv (date, devise, score, nb_phrases, source).
"""

import csv
import glob
import json
import os
import re
import subprocess
from datetime import datetime

DEVISES = {
    'USD': r"dollar am[ée]ricain|\bdollar\b(?! (australien|canadien|n[ée]o))|\busd\b|\bdxy\b|greenback|billet vert",
    'EUR': r"\beuro\b|\beur\b|\bbce\b|\becb\b",
    'GBP': r"\blivre\b|sterling|\bgbp\b|\bboe\b|\bcable\b",
    'JPY': r"\byen\b|\bjpy\b|\bboj\b",
    'AUD': r"dollar australien|\baud\b|\baussie\b|\brba\b",
    'NZD': r"dollar n[ée]o[- ]z[ée]landais|\bnzd\b|\bkiwi\b|\brbnz\b",
    'CAD': r"dollar canadien|\bcad\b|\bloonie\b|banque du canada|\bboc\b",
    'CHF': r"franc suisse|\bchf\b|\bsnb\b|\bbns\b",
}
HAUSSE = r"(?:à|a) la hausse|hausse|haussi[eè]re?s?|bullish|hawkish|se renforc\w*|renforcement|vigueur|appr[ée]ci\w*|rebond\w*|\bacheter\b|\bachat\b|\bmonter\b|va monter|surperform\w*|soutenu|fort(e|s)?\b|solide"
BAISSE = r"(?:à|a) la baisse|baisse|baissi[eè]re?s?|bearish|dovish|faiblesse|affaibli\w*|d[ée]pr[ée]ci\w*|\bcouler\b|chuter|chute|\bvendre\b|\bvente\b|sous pression|plomb[ée]\w*|recul\w*|faible"
NEGATION = r"\b(pas|plus|jamais|ni)\b"
PAIRE = re.compile(r"\b(EUR|GBP|AUD|NZD|USD|CAD|CHF|JPY)(EUR|GBP|AUD|NZD|USD|CAD|CHF|JPY)\b", re.I)
MOIS = {'janvier': 1, 'fevrier': 2, 'février': 2, 'fev': 2, 'fév': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
        'juillet': 7, 'aout': 8, 'août': 8, 'septembre': 9, 'sep': 9, 'octobre': 10, 'novembre': 11, 'decembre': 12}


CONDITION = re.compile(r"laisse[zr]? (le|la|les) (trade|march[ée]|position)|\bsi\b|\bs'il\b|\?|pourrait|pourraient|au cas o[uù]|sinon\b|imaginez|scénario|scenario", re.I)


def score_phrase(ph):
    t = ph.lower()
    if CONDITION.search(t):
        return {}  # phrases conditionnelles ou interrogatives : pas un avis tranché
    h = len(re.findall(HAUSSE, t))
    b = len(re.findall(BAISSE, t))
    if h == b:
        return {}
    signe = 1 if h > b else -1
    if re.search(NEGATION + r"\s+\w*\s*(" + HAUSSE + "|" + BAISSE + ")", t):
        signe = -signe
    out = {}
    sans_paire = PAIRE.sub(' ', ph).lower()
    cites = [d for d, rx in DEVISES.items() if re.search(rx, sans_paire)]
    if len(cites) == 1:          # devise nommée explicitement : prioritaire (« haussier sur le dollar »)
        out[cites[0]] = signe
        return out
    m = PAIRE.search(ph)
    if m and not cites:
        base, cot = m.group(1).upper(), m.group(2).upper()
        out[base] = signe
        out[cot] = -signe
    return out


def phrases(texte):
    return [p for p in re.split(r"(?<=[.!?;:\n])\s+", texte) if len(p) > 12]


def date_pdf(nom):
    n = os.path.basename(nom).lower()
    m = re.search(r"(\d{1,2})\s*([a-zéû]+)", n)
    if not m:
        return None
    mo = next((v for k, v in MOIS.items() if m.group(2).startswith(k)), None)
    if not mo:
        return None
    return datetime(2026, mo, int(m.group(1)))


def main():
    lignes = []
    for l in open('data/telegram_messages.jsonl', encoding='utf-8'):
        m = json.loads(l)
        if m.get('forwarded_from') and not re.search(r'amirou|halal|signalx', m['forwarded_from'], re.I):
            continue
        for ph in phrases(m['text']):
            for dev, s in score_phrase(ph).items():
                lignes.append((m['date_utc'][:10], dev, s, 'canal'))
    pdfs = glob.glob('ChatExport_2026-09-17/rapport Amirou/*.pdf') + glob.glob('rapports_pdf/21sep.pdf')
    for f in pdfs:
        d = date_pdf(f)
        if f.endswith('21sep.pdf'):
            d = datetime(2026, 9, 21)
        if not d:
            continue
        texte = subprocess.run(['pdftotext', '-layout', f, '-'], capture_output=True, text=True).stdout
        for ph in phrases(texte):
            for dev, s in score_phrase(ph).items():
                lignes.append((d.strftime('%Y-%m-%d'), dev, s, 'signalx'))
    agg = {}
    for d, dev, s, src in lignes:
        k = (d, dev, src)
        a = agg.setdefault(k, [0, 0])
        a[0] += s
        a[1] += 1
    os.makedirs('data/fondamental', exist_ok=True)
    with open('data/fondamental/biais_amirou.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['date', 'devise', 'score', 'nb_phrases', 'source'])
        for (d, dev, src), (s, n) in sorted(agg.items()):
            w.writerow([d, dev, s, n, src])
    print(f"{len(lignes)} phrases orientées, {len(agg)} lignes jour x devise -> data/fondamental/biais_amirou.csv")


if __name__ == '__main__':
    main()
