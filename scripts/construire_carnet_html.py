#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Données et captures du « Tracker Forex saisonnalité & fonda », version 2023-2026, sur le modèle exact de la base
Notion de l'utilisateur (Mois | statut | 3, 5, 10 et 20 dernières années | Explication fonda | Fichiers et médias),
pour EURUSD, GBPUSD, AUDUSD et USDJPY.

- statut : sens réel du mois (Fed H.10, data/rendements_mensuels.csv ; octobre 2026 : cours journaliers) ;
- 3/5/10/20 dernières années : même mois des années précédentes (données Fed depuis 2009 : « 20 ans » = depuis 2009) ;
  biais « Vente » si la moyenne est négative, « Achat » sinon ;
- explication fonda : décisions de la Fed et de l'autre banque centrale de la paire (BIS), annonces majeures avec réel
  et consensus (calendrier TradingView), positionnement COT des gérants d'actifs ; puis les messages d'Amirou sur les
  deux devises de la paire (lien vers chaque message, extrait) et ce que la paire a fait 1 semaine et 1 mois après
  (clôture du jour du message -> clôture 5 ou 21 jours de bourse plus tard) ;
- fichiers et médias : graphique journalier du mois (dessiné par la page) et captures des trades d'Amirou sur la paire
  (TradingView ou photo du canal), avec le résultat rejoué sur les cours (data/verification_trades.csv).

Usage : python scripts/construire_carnet_html.py DOSSIER_DE_SORTIE   (après scripts/fiches_mensuelles.py)
Écrit DOSSIER/data.json et DOSSIER/captures/<id>.jpg ; la page (tracker.html) intègre data.json dans une balise
<script type="application/json" id="donnees">.
"""
import glob
import json
import os
import re
import subprocess
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from contexte_marche import calendrier, cot, taux  # noqa: E402
from fiches_mensuelles import CLES, DEBUT, FIN, MOIS_FR  # noqa: E402
from tester_masterclass import pip  # noqa: E402

PAIRES = ['EURUSD', 'GBPUSD', 'AUDUSD', 'USDJPY']
FENETRES = [3, 5, 10, 20]


def journalier(p):
    d = pd.read_csv('data/prix/journalier_dukascopy.csv')
    d = d[d['paire'] == p][['date', 'open', 'high', 'low', 'close']]
    h = pd.read_csv(f'data/prix/yahoo/{p}_1h.csv', parse_dates=['date'])
    h = h[(h['date'].dt.weekday < 5) & (h['date'] >= '2026-10-02')]
    g = h.groupby(h['date'].dt.strftime('%Y-%m-%d'))
    y = pd.DataFrame({'date': list(g.groups), 'open': g['open'].first().to_numpy(), 'high': g['high'].max().to_numpy(),
                      'low': g['low'].min().to_numpy(), 'close': g['close'].last().to_numpy()})
    return pd.concat([d, y]).sort_values('date').reset_index(drop=True)


def source_capture(i, msgs, tv):
    if i in tv:
        return tv[i]
    ph = msgs.get(i, {}).get('photo')
    if ph:
        for d in ['ChatExport_2026-10-14', 'ChatExport_2026-10-01']:
            if os.path.exists(f'{d}/{ph}'):
                return f'{d}/{ph}'
    return None


def num(x, n=5):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), n)


def main():
    sortie = sys.argv[1]
    os.makedirs(f'{sortie}/captures', exist_ok=True)
    msgs = {}
    for l in open('data/telegram_messages.jsonl', encoding='utf-8'):
        m = json.loads(l)
        msgs[m['id']] = m
    tv = {}
    for f in glob.glob('assets/tradingview/*/*.png'):
        m = re.search(r'msg(\d+)_', f)
        if m:
            tv.setdefault(int(m.group(1)), f)
    tx, ct, cal = taux(), cot(), calendrier()
    av = pd.read_csv('data/fiches_mensuelles/avis.csv')
    tr = pd.read_csv('data/verification_trades.csv')
    tr = tr[tr['date'] >= '2023-01-01']
    rm = pd.read_csv('data/rendements_mensuels.csv')
    rm['pips'] = (rm['cloture'] - rm['cloture'] / (1 + rm['rendement_pct'] / 100)) / rm['paire'].map(pip)
    out = {}
    n_cap = 0
    for p in PAIRES:
        base, cote = p[:3], p[3:]
        d = journalier(p)
        jours = pd.to_datetime(d['date']).reset_index(drop=True)
        cl = d['close'].to_numpy()
        lignes = []
        for mois in pd.period_range(DEBUT, FIN, freq='M').astype(str):
            debut = pd.Timestamp(mois + '-01')
            fin = debut + pd.offsets.MonthEnd(0)
            y = int(mois[:4])
            x = rm[(rm['paire'] == p) & (rm['mois'].str[5:7] == mois[5:7])].copy()
            x['an'] = x['mois'].str[:4].astype(int)
            saison = {}
            for n in FENETRES:
                w = x[(x['an'] < y) & (x['an'] >= y - n)]
                saison[n] = dict(biais='Vente' if w['rendement_pct'].mean() < 0 else 'Achat', moy=num(w['rendement_pct'].mean(), 2),
                                 hausse=int((w['rendement_pct'] > 0).sum()), n=len(w),
                                 annees=[[int(a), round(r, 2), round(pp)] for a, r, pp in zip(w['an'], w['rendement_pct'], w['pips'])])
            dm = d[(d['date'] >= mois) & (d['date'] < (fin + pd.Timedelta(days=1)).strftime('%Y-%m-%d'))]
            reel = x[x['an'] == y]
            if len(reel):
                r_pct, r_pips = float(reel['rendement_pct'].iat[0]), float(reel['pips'].iat[0])
            elif len(dm):
                prev = d[d['date'] < mois]['close'].iat[-1]
                r_pct, r_pips = (dm['close'].iat[-1] / prev - 1) * 100, (dm['close'].iat[-1] - prev) / pip(p)
            else:
                r_pct = r_pips = None
            fondamental = []
            # banques centrales
            t0, t1 = tx[tx.index < debut].iloc[-1], tx[tx.index <= fin].iloc[-1]
            for dev in [base, cote]:
                if abs(t1[dev] - t0[dev]) > 1e-9:
                    fondamental.append(dict(k='taux', dev=dev, avant=num(t0[dev], 2), apres=num(t1[dev], 2)))
            ev = cal[(cal['date'] >= debut) & (cal['date'] <= fin + pd.Timedelta(days=1)) & (cal['importance'] == 1)
                     & cal['devise'].isin([base, cote]) & cal['titre'].str.contains('|'.join(CLES), regex=True, na=False)
                     & ~cal['titre'].str.contains('Flash|Prel|MoM', regex=True, na=False)].sort_values('date')
            for e in ev.itertuples():
                fondamental.append(dict(k='annonce', d=e.date.strftime('%d/%m'), dev=e.devise, t=e.titre,
                                        a=num(e.actuel, 3), c=num(e.consensus, 3)))
            c0, c1 = ct[ct.index < debut], ct[ct.index <= fin]
            hist = ct[(ct.index <= fin) & (ct.index > fin - pd.Timedelta(days=3 * 365))]
            for dev in [base, cote]:
                if len(c0) and len(c1) and dev in ct and not np.isnan(c1[dev].iloc[-1]):
                    fondamental.append(dict(k='cot', dev=dev, net=int(c1[dev].iloc[-1]), var=int(c1[dev].iloc[-1] - c0[dev].iloc[-1]),
                                            pct=round((hist[dev] <= c1[dev].iloc[-1]).mean() * 100)))
            # messages d'Amirou sur les deux devises, mesurés sur la paire
            a = av[(av['date'].str[:7] == mois) & av['devise'].isin([base, cote])]
            messages = []
            for mid, g in a.groupby('id', sort=False):
                net = sum((1 if r.sens == 'haussier' else -1) * (1 if r.devise == base else -1) for r in g.itertuples())
                if net == 0:
                    continue
                s = int(np.sign(net))
                dt = pd.Timestamp(g['date'].iat[0][:10])
                i0 = jours.searchsorted(dt, side='right') - 1
                res = {}
                for nom, h in [('s', 5), ('m', 21)]:
                    if 0 <= i0 and i0 + h < len(cl):
                        pips_ = (cl[i0 + h] - cl[i0]) / pip(p)
                        res[nom] = [round(pips_), bool(np.sign(pips_) == s)]
                messages.append(dict(id=int(mid), d=g['date'].iat[0], sens='hausse' if s > 0 else 'baisse',
                                     e=' / '.join(dict.fromkeys(g['extrait'])), prix=num(cl[i0]) if i0 >= 0 else None, **res))
            # trades d'Amirou sur la paire
            trades = []
            for t in tr[(tr['mois'] == mois) & (tr['paire'] == p)].to_dict('records'):
                i = None if pd.isna(t['id_message']) else int(t['id_message'])
                img = None
                if i is not None:
                    src = source_capture(i, msgs, tv)
                    if src:
                        dst = f'{sortie}/captures/{i}.jpg'
                        if not os.path.exists(dst):
                            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', "scale='min(760,iw)':-2",
                                            '-q:v', '7', dst])
                        if os.path.exists(dst):
                            img = f'captures/{i}.jpg'
                            n_cap += 1
                trades.append(dict(id=i, d=str(t['date'])[:16], s=t['sens'], e=num(t['entree']), sl=num(t['stop']),
                                   tp=num(t['objectif']), st=t['statut_rejeu'] if isinstance(t['statut_rejeu'], str) else None,
                                   iss=t['issue_rejeu'] if isinstance(t['issue_rejeu'], str) else None, r=num(t['r'], 2),
                                   canal=t['canal'] if isinstance(t['canal'], str) else '', img=img))
            lignes.append(dict(m=mois, nom=f'{MOIS_FR[debut.month - 1].capitalize()} {y}',
                               statut=None if r_pct is None else ('Haussier' if r_pct > 0 else 'Baissier'),
                               pct=num(r_pct, 2), pips=None if r_pips is None else round(r_pips), saison=saison,
                               fonda=fondamental, messages=messages, trades=trades,
                               ohlc=[[r.date[8:10], num(r.open), num(r.high), num(r.low), num(r.close)] for r in dm.itertuples()]))
        out[p] = lignes
    js = json.dumps(dict(paires=out, genere=pd.Timestamp.now().strftime('%d/%m/%Y')), ensure_ascii=False, separators=(',', ':'))
    open(f'{sortie}/data.json', 'w', encoding='utf-8').write(js)
    print(sum(len(v) for v in out.values()), 'lignes,', len(os.listdir(f'{sortie}/captures')), 'captures,',
          round(len(js) / 1e6, 2), 'Mo de données')


if __name__ == '__main__':
    main()
