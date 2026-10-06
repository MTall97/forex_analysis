#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Amirou reprend-il les analyses de Marc Chandler (Marc to Market) ?

Amirou écrit en français, Chandler en anglais : on compare le sens des paragraphes avec un modèle
multilingue (sentence-transformers « paraphrase-multilingual-MiniLM-L12-v2 », similarité cosinus
entre -1 et 1 ; une traduction donne en général plus de 0,8, deux textes sur la même actualité
0,5 à 0,7).

Textes d'Amirou :
- les 22 rapports PDF de 2026 (« SignalX » et autres), datés par leur message de publication ;
- ses messages de plus de 300 caractères dans le canal (2019-2026), hors messages transférés
  d'un tiers.
Pour chaque paragraphe d'Amirou publié à l'instant T, on cherche le paragraphe de Chandler le plus
proche :
- « avant » : billets publiés dans les 7 jours qui précèdent T ;
- « après » : billets publiés dans les 7 jours qui suivent T (témoin : même actualité, mais
  Amirou ne pouvait pas les avoir lus) ;
- « un an avant » : billets de la même semaine un an plus tôt (témoin : autre actualité).
Si Amirou s'inspire de Chandler, « avant » doit dépasser nettement « après ».

Sorties : data/marc_to_market/similarite_paragraphes.csv (un paragraphe d'Amirou par ligne, avec
le meilleur paragraphe de Chandler « avant ») et un résumé à l'écran.
Prérequis : pip install sentence-transformers (torch CPU) ; billets téléchargés par
scripts/collecter_marc_to_market.py ; PDF dans « ChatExport_2026-09-17/rapport Amirou/ ».
"""
import glob
import gzip
import json
import os
import re
import subprocess
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
MODELE = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
CACHE = 'data/marc_to_market/embeddings_chandler.npz'

# fichier PDF -> message de publication (#id, heure UTC)
PDF = {
    '20janvierpdf': (14346, '2026-01-20T17:30:42'), 'rapport_signalx_21janvier2026': (14347, '2026-01-21T13:59:22'),
    'rapport_signalx_22janvier': (14348, '2026-01-22T12:13:33'), 'Analyse_or_23janvier_2026': (14352, '2026-01-23T17:39:31'),
    'rapport_signalx_25janvier': (14354, '2026-01-25T16:53:17'), '26janvier2026': (14357, '2026-01-26T13:06:19'),
    '27janvier': (14359, '2026-01-27T09:35:29'), '28janvier': (14362, '2026-01-28T16:09:55'),
    'perspective sur le dollar': (14374, '2026-01-28T23:01:05'), '3fevrier': (14390, '2026-02-03T04:22:20'),
    'update_3fev': (14393, '2026-02-03T18:58:58'), '10fevrier': (14409, '2026-02-10T13:08:01'),
    '11fevrier': (14410, '2026-02-11T21:12:48'), '28fev': (14464, '2026-03-01T19:10:16'),
    '8mars': (14539, '2026-03-09T00:01:58'), '12mars': (14565, '2026-03-12T09:23:43'),
    '8avril': (14675, '2026-04-08T11:43:45'), '14 juin': (14935, '2026-06-14T23:29:22'),
    '22juin': (14955, '2026-06-22T00:59:34'), '30juin': (14973, '2026-06-30T13:55:48'),
    'post nfp': (15019, '2026-07-02T13:21:26'),
}


def paragraphes_pdf(chemin):
    txt = subprocess.run(['pdftotext', chemin, '-'], capture_output=True, text=True).stdout
    blocs = re.split(r'\n\s*\n', txt)
    out = []
    for b in blocs:
        b = re.sub(r'\s+', ' ', b).strip()
        if len(b) >= 150 and len(re.findall(r'[a-zà-ÿ]{3,}', b)) >= 20:
            out.append(b)
    return out


def textes_amirou():
    lignes = []
    for chemin in glob.glob('ChatExport_2026-09-17/rapport Amirou/*.pdf'):
        nom = os.path.splitext(os.path.basename(chemin))[0]
        if nom not in PDF:
            continue
        mid, date = PDF[nom]
        for p in paragraphes_pdf(chemin):
            lignes.append(dict(source='pdf', fichier=nom, id_message=mid, date_utc=date, texte=p))
    for l in open('data/telegram_messages.jsonl', encoding='utf-8'):
        m = json.loads(l)
        t = (m.get('text') or '').strip()
        tiers = m.get('forwarded_from') and 'amirou' not in m['forwarded_from'].lower()
        if len(t) >= 300 and not tiers:
            for p in [p for p in re.split(r'\n\s*\n', t) if len(p) >= 150] or [t]:
                lignes.append(dict(source='canal', fichier='', id_message=m['id'], date_utc=m['date_utc'],
                                   texte=re.sub(r'\s+', ' ', p)[:1500]))
    return pd.DataFrame(lignes)


def paragraphes_chandler():
    lignes = []
    for l in gzip.open('data/marc_to_market/billets.jsonl.gz', 'rt', encoding='utf-8'):
        b = json.loads(l)
        for p in b['texte'].split('\n'):
            p = p.strip()
            if len(p) >= 120:
                lignes.append(dict(date_utc=b['date_utc'], titre=b['titre'], url=b['url'], texte=p[:1500]))
    return pd.DataFrame(lignes)


def main():
    from sentence_transformers import SentenceTransformer
    modele = SentenceTransformer(MODELE, device='cpu')
    c = paragraphes_chandler()
    if os.path.exists(CACHE) and np.load(CACHE)['n'] == len(c):
        ec = np.load(CACHE)['e']
    else:
        ec = modele.encode(c['texte'].tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=True)
        np.savez_compressed(CACHE, e=ec.astype(np.float16), n=len(c))
    ec = ec.astype(np.float32)
    a = textes_amirou()
    ea = modele.encode(a['texte'].tolist(), batch_size=64, normalize_embeddings=True, show_progress_bar=True)
    tc = pd.to_datetime(c['date_utc']).values
    res = []
    for i, r in a.iterrows():
        t = np.datetime64(r['date_utc'])
        fen = {
            'avant': (tc >= t - np.timedelta64(7, 'D')) & (tc < t),
            'apres': (tc > t) & (tc <= t + np.timedelta64(7, 'D')),
            'un_an_avant': (tc >= t - np.timedelta64(372, 'D')) & (tc < t - np.timedelta64(358, 'D')),
        }
        ligne = dict(r)
        for nom, masque in fen.items():
            idx = np.where(masque)[0]
            if len(idx) == 0:
                ligne[f'sim_{nom}'] = np.nan
                continue
            s = ec[idx] @ ea[i]
            j = idx[int(np.argmax(s))]
            ligne[f'sim_{nom}'] = round(float(s.max()), 3)
            if nom == 'avant':
                ligne.update(chandler_date=c['date_utc'][j], chandler_titre=c['titre'][j], chandler_url=c['url'][j],
                             chandler_texte=c['texte'][j])
        res.append(ligne)
    d = pd.DataFrame(res)
    d.to_csv('data/marc_to_market/similarite_paragraphes.csv', index=False)
    d['annee'] = d['date_utc'].str[:4]
    d['groupe'] = np.where(d['source'] == 'pdf', 'rapports PDF 2026', 'canal ' + d['annee'])
    agg = d.groupby('groupe').agg(paragraphes=('texte', 'size'), avant=('sim_avant', 'mean'),
                                  apres=('sim_apres', 'mean'), un_an_avant=('sim_un_an_avant', 'mean'),
                                  avant_08=('sim_avant', lambda s: (s >= 0.8).mean()),
                                  apres_08=('sim_apres', lambda s: (s >= 0.8).mean()))
    print(agg.round(3).to_string())


if __name__ == '__main__':
    main()
