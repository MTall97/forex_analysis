#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Biais directionnel de Marc Chandler (Marc to Market) par devise et par jour, tiré du texte de ses
billets, puis confrontation avec Amirou.

1. Extraction (lexique, sans modèle) : chaque phrase est découpée ; on repère la devise sujet
   (première devise citée : dollar/greenback, euro, yen, sterling/pound, Australian dollar/Aussie,
   Canadian dollar/loonie, Swiss franc, kiwi/New Zealand dollar) et le sens (mots de hausse ou de
   baisse). Quand le dollar est le sujet face à une autre devise citée (« the dollar rose against the
   yen »), la seconde devise reçoit le signe opposé.
   - phrases « regard vers l'avant » (expect, look for, anticipate, suspect, likely, risk, scope,
     target, favor, outlook, could, may, should, would…) -> biais_avant ;
   - autres phrases (description de ce qui s'est passé) -> biais_constat (sert de contrôle du
     lexique : il doit suivre le mouvement du jour).
   Score d'une devise un jour = somme des +1/-1 ; biais d'une paire = score base - score cotation.
2. Contrôles et tests :
   - le constat suit-il le mouvement du jour (sinon le lexique est mauvais) ?
   - le biais « avant » de Chandler prévoit-il le sens des 1 et 5 jours suivants ?
   - les trades d'Amirou (registre texte data/trades.csv, captures rejouées data/trades_simules.csv
     et data/revue_trades_simules.csv) vont-ils dans le sens du biais de Chandler des 3 jours
     précédents ? Et ceux qui vont dans son sens gagnent-ils plus ?
   - son biais écrit (data/fondamental/biais_amirou.csv) suit-il celui de Chandler ?

Sorties : data/marc_to_market/biais_chandler.csv (date, devise, avant, constat, phrases),
data/marc_to_market/confrontation_trades.csv, data/marc_to_market/resultats.json.
"""
import gzip
import json
import os
import re

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
SORTIE = 'data/marc_to_market'

DEVISES = {
    'USD': r"\b(?:dollar|greenback|usd|dxy|dollar index)\b",
    'EUR': r"\b(?:euro|eur)\b",
    'JPY': r"\b(?:yen|jpy)\b",
    'GBP': r"\b(?:sterling|pound|gbp|cable)\b",
    'AUD': r"\b(?:australian dollar|aussie|aud)\b",
    'CAD': r"\b(?:canadian dollar|loonie|cad)\b",
    'CHF': r"\b(?:swiss franc|franc|chf)\b",
    'NZD': r"\b(?:new zealand dollar|kiwi|nzd)\b",
}
# « Australian dollar » contient « dollar » : ces devises sont repérées en premier
ORDRE = ['AUD', 'CAD', 'NZD', 'EUR', 'JPY', 'GBP', 'CHF', 'USD']
HAUSSE = r"\b(?:rise[sn]?|rose|rising|gain(?:s|ed|ing)?|rall(?:y|ies|ied|ying)|recover(?:s|ed|ing|y)?|rebound(?:s|ed|ing)?|advanc(?:e|es|ed|ing)|climb(?:s|ed|ing)?|higher|firm(?:er|ed|s)?|strength(?:en|ened|ening)?|stronger|upside|bid|bullish|support(?:s|ed|ive)?|extend(?:s|ed)? (?:its |the )?gains|new highs?|outperform(?:s|ed)?|appreciat(?:e|ed|es|ing|ion))\b"
BAISSE = r"\b(?:fall(?:s|en|ing)?|fell|declin(?:e|es|ed|ing)|drop(?:s|ped|ping)?|slid(?:e|es|ing)?|slump(?:s|ed)?|lower|weak(?:er|ened|ening|ness)?|softer|pressure[d]?|downside|offered|bearish|sell(?:ing|-off|off)?|sold|loss(?:es)?|extend(?:s|ed)? (?:its |the )?losses|new lows?|underperform(?:s|ed)?|depreciat(?:e|ed|es|ing|ion)|retreat(?:s|ed|ing)?|pull(?:ed)? back)\b"
AVANT = r"\b(?:expect(?:s|ed|ation)?|look(?:ing)? for|anticipat(?:e|ed|es)|suspect|likely|unlikely|risk(?:s)?|scope|target|favor(?:s|ed)?|outlook|could|may|might|should|would|will|bias|next|potential|warn(?:s)?|seems poised|poised|forecast)\b"


def phrases(texte):
    return [p for p in re.split(r'(?<=[.!?])\s+|\n', texte) if len(p) > 30]


def sujet(p):
    """(devise sujet, autre devise citée après)."""
    pos = []
    reste = p
    for d in ORDRE:
        for m in re.finditer(DEVISES[d], reste, re.I):
            pos.append((m.start(), d))
        reste = re.sub(DEVISES[d], lambda m: ' ' * len(m.group(0)), reste, flags=re.I)
    pos.sort()
    if not pos:
        return None, None
    d0 = pos[0][1]
    autre = next((d for _, d in pos[1:] if d != d0), None)
    return d0, autre


def extraire():
    lignes = []
    for l in gzip.open(f'{SORTIE}/billets.jsonl.gz', 'rt', encoding='utf-8'):
        b = json.loads(l)
        jour = b['date_utc'][:10]
        for p in phrases(b['texte']):
            h, s = len(re.findall(HAUSSE, p, re.I)), len(re.findall(BAISSE, p, re.I))
            if h == s:
                continue
            d0, autre = sujet(p)
            if d0 is None:
                continue
            signe = 1 if h > s else -1
            genre = 'avant' if re.search(AVANT, p, re.I) else 'constat'
            lignes.append((jour, d0, genre, signe))
            if d0 == 'USD' and autre:
                lignes.append((jour, autre, genre, -signe))
    d = pd.DataFrame(lignes, columns=['date', 'devise', 'genre', 'signe'])
    t = d.pivot_table(index=['date', 'devise'], columns='genre', values='signe', aggfunc='sum', fill_value=0)
    t['phrases'] = d.groupby(['date', 'devise']).size()
    t = t.reset_index()
    t.to_csv(f'{SORTIE}/biais_chandler.csv', index=False)
    return t


def biais_paire(t, paire, fin, jours=3, col='avant'):
    """Somme du biais de la paire sur les `jours` jours calendaires jusqu'à `fin` exclu."""
    base, cot = paire[:3], paire[3:]
    debut = (pd.Timestamp(fin) - pd.Timedelta(days=jours)).strftime('%Y-%m-%d')
    fin = pd.Timestamp(fin).strftime('%Y-%m-%d')
    f = t[(t['date'] >= debut) & (t['date'] < fin)]
    sb = f.loc[f['devise'] == base, col].sum() if base != 'XAU' else 0
    sc = f.loc[f['devise'] == cot, col].sum()
    return sb - sc


def main():
    t = extraire()
    t['date'] = t['date'].astype(str)
    res = {}
    # prix journaliers (Dukascopy) : rendement du jour et des 5 jours suivants
    px = pd.read_csv('data/prix/journalier_dukascopy.csv')
    px['date'] = px['date'].astype(str)
    paires = ['EURUSD', 'GBPUSD', 'AUDUSD', 'NZDUSD', 'USDJPY', 'USDCAD', 'EURJPY', 'GBPJPY', 'AUDJPY', 'EURNZD']
    pivot = t.pivot_table(index='date', columns='devise', values=['avant', 'constat'], fill_value=0)
    lignes = []
    for p in paires:
        q = px[px['paire'] == p].sort_values('date').reset_index(drop=True)
        q = q[q['date'] >= '2019-03-01'].reset_index(drop=True)
        q['r0'] = np.log(q['close'] / q['open'])
        q['r1'] = np.log(q['close'].shift(-1) / q['close'])
        q['r5'] = np.log(q['close'].shift(-5) / q['close'])
        base, cot = p[:3], p[3:]
        for col in ['avant', 'constat']:
            s = pivot[col].reindex(q['date']).fillna(0)
            q[col] = (s[base].values if base in s else 0) - (s[cot].values if cot in s else 0)
        q['paire'] = p
        lignes.append(q)
    q = pd.concat(lignes)
    out = {}
    for col, hor in [('constat', 'r0'), ('avant', 'r0'), ('avant', 'r1'), ('avant', 'r5')]:
        x = q[(q[col] != 0) & q[hor].notna()]
        acc = float((np.sign(x[col]) == np.sign(x[hor])).mean())
        out[f'{col}->{hor}'] = dict(jours=int(len(x)), meme_sens_pct=round(100 * acc, 1))
        x2 = x.assign(annee=x['date'].str[:4]).groupby('annee').apply(
            lambda g: round(100 * float((np.sign(g[col]) == np.sign(g[hor])).mean()), 1))
        out[f'{col}->{hor}']['par_annee'] = x2.to_dict()
    res['previsions_chandler'] = out

    # trades d'Amirou
    tr = []
    reg = pd.read_csv('data/trades.csv')
    for _, r in reg.iterrows():
        tr.append(dict(source='registre texte', date=r['date_utc'], paire=r['paire'], sens=r['sens'],
                       issue=r['issue'], r=np.nan))
    for f, src in [('data/trades_simules.csv', 'captures OCR'), ('data/revue_trades_simules.csv', 'revue visuelle')]:
        s = pd.read_csv(f)
        for _, r in s.iterrows():
            if r['issue'] in ('objectif', 'stop', 'ouvert après 20 jours') and r['statut'] == 'annoncé':
                tr.append(dict(source=src, date=r['date_publication'], paire=r['paire'], sens=r['sens'],
                               issue=r['issue'], r=pd.to_numeric(r['resultat_r'], errors='coerce')))
    tr = pd.DataFrame(tr)
    tr = tr[tr['paire'].astype(str).str.fullmatch(r'(?:EUR|USD|GBP|JPY|AUD|NZD|CAD|CHF|XAU){2}')]
    tr['biais_chandler'] = [biais_paire(t, p, d[:10]) for p, d in zip(tr['paire'], tr['date'])]
    tr['signe_amirou'] = np.where(tr['sens'] == 'achat', 1, -1)
    tr['accord'] = np.where(tr['biais_chandler'] == 0, 'sans avis',
                            np.where(np.sign(tr['biais_chandler']) == tr['signe_amirou'], 'même sens', 'sens opposé'))
    tr.to_csv(f'{SORTIE}/confrontation_trades.csv', index=False)
    tr['annee'] = tr['date'].astype(str).str[:4]
    acc = {}
    for src, g in tr.groupby('source'):
        avis = g[g['accord'] != 'sans avis']
        acc[src] = dict(trades=int(len(g)), avec_avis=int(len(avis)),
                        meme_sens_pct=round(100 * float((avis['accord'] == 'même sens').mean()), 1) if len(avis) else None,
                        r_meme_sens=round(float(avis.loc[avis['accord'] == 'même sens', 'r'].mean()), 3) if avis['r'].notna().any() else None,
                        r_oppose=round(float(avis.loc[avis['accord'] == 'sens opposé', 'r'].mean()), 3) if avis['r'].notna().any() else None,
                        n_meme=int((avis['accord'] == 'même sens').sum()), n_oppose=int((avis['accord'] == 'sens opposé').sum()))
        if src == 'registre texte':
            for issue in ['tp', 'sl']:
                h = avis[avis['issue'].astype(str).str.startswith(issue)]
                acc[src][f'meme_sens_pct_{issue}'] = round(100 * float((h['accord'] == 'même sens').mean()), 1) if len(h) else None
    a2 = tr[tr['accord'] != 'sans avis'].groupby('annee').apply(
        lambda g: dict(n=int(len(g)), meme_sens_pct=round(100 * float((g['accord'] == 'même sens').mean()), 1)))
    res['trades_amirou'] = acc
    res['trades_amirou_par_annee'] = a2.to_dict()

    # biais écrit d'Amirou par devise
    ba = pd.read_csv('data/fondamental/biais_amirou.csv')
    ba = ba[ba['devise'].isin(DEVISES.keys())]
    ba['chandler'] = [t[(t['devise'] == dv) & (t['date'] < d) &
                        (t['date'] >= (pd.Timestamp(d) - pd.Timedelta(days=3)).strftime('%Y-%m-%d'))]['avant'].sum()
                      for d, dv in zip(ba['date'], ba['devise'])]
    x = ba[(ba['chandler'] != 0) & (ba['score'] != 0)]
    res['biais_ecrit'] = dict(cas=int(len(x)), meme_sens_pct=round(100 * float((np.sign(x['score']) == np.sign(x['chandler'])).mean()), 1))
    json.dump(res, open(f'{SORTIE}/resultats.json', 'w'), ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
