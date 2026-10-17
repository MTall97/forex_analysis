#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fiches mensuelles janvier 2023 - octobre 2026, sur le modèle de la fiche « Septembre 2025 » de l'utilisateur :
ce que le marché a fait, ce que disaient les données (banques centrales, annonces, positionnement COT), ce qu'Amirou a
écrit (lien vers chaque message) et ce que ses avis et ses trades ont donné sur les cours.

- Avis d'Amirou : chaque message du canal est découpé en phrases ; une phrase qui donne un sens à une devise (lexique
  de scripts/biais_textuel.py, phrases conditionnelles exclues) compte comme un avis. On mesure ensuite la force de la
  devise contre la moyenne des 8 (scripts/contexte_marche.py) entre la clôture du jour du message et 5 jours de bourse
  (1 semaine) ou 21 jours (1 mois) plus tard : ✓ si la devise a bougé dans le sens annoncé.
- Trades : data/verification_trades.csv (rejeu sur les cours ; statut annoncé / après coup).
- Saisonnalité du projet : moyenne du même mois sur les années précédentes (data/rendements_mensuels.csv, Fed H.10).
Sortie : analyses/fiches_mensuelles/AAAA-MM.md, data/fiches_mensuelles/avis.csv, analyses/FICHES_MENSUELLES.md
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from biais_textuel import phrases, score_phrase  # noqa: E402
from contexte_marche import DEVISES, LIEN, calendrier, cot, force, taux, valeurs_usd  # noqa: E402

DEBUT, FIN = '2023-01', '2026-10'
DOSSIER = 'analyses/fiches_mensuelles'
CLES = ['Interest Rate Decision', 'Non Farm Payrolls', 'Inflation Rate YoY', 'Core Inflation Rate YoY',
        'Unemployment Rate', 'GDP Growth Rate QoQ']
MOIS_FR = ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre',
           'novembre', 'décembre']
PAIRES_SAISON = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD']


def avis_amirou(v):
    jours = v.index
    lignes = []
    for l in open('data/telegram_messages.jsonl', encoding='utf-8'):
        m = json.loads(l)
        if m['date_utc'][:7] < DEBUT or not m['text']:
            continue
        if m.get('forwarded_from') and not re.search(r'amirou|halal|signalx', m['forwarded_from'], re.I):
            continue
        sc, extrait = {}, {}
        for ph in phrases(m['text']):
            for dev, s in score_phrase(ph).items():
                sc[dev] = sc.get(dev, 0) + s
                extrait.setdefault(dev, ph.strip().replace('\n', ' ')[:140])
        d = pd.Timestamp(m['date_utc'][:10])
        i0 = jours.searchsorted(d, side='right') - 1
        for dev, s in sc.items():
            if s == 0 or i0 < 0:
                continue
            res = {}
            for nom, h in [('1 semaine', 5), ('1 mois', 21)]:
                if i0 + h < len(jours):
                    f = force(v, jours[i0], jours[i0 + h])[dev]
                    res[nom] = round(f, 2)
                    res['juste ' + nom] = bool(np.sign(f) == np.sign(s))
            lignes.append(dict(id=m['id'], date=m['date_utc'][:16], devise=dev, sens='haussier' if s > 0 else 'baissier',
                               extrait=extrait[dev], **res))
    return pd.DataFrame(lignes)


def saisonnalite(mois):
    r = pd.read_csv('data/rendements_mensuels.csv')
    r['annee'] = r['mois'].str[:4].astype(int)
    r['m'] = r['mois'].str[5:7]
    y, mm = int(mois[:4]), mois[5:7]
    out = {}
    for p in PAIRES_SAISON:
        x = r[(r['paire'] == p) & (r['m'] == mm)]
        passe = x[(x['annee'] < y) & (x['annee'] >= y - 10)]['rendement_pct']
        reel = x[x['annee'] == y]['rendement_pct']
        out[p] = (passe.mean() if len(passe) else np.nan, (passe > 0).mean() if len(passe) else np.nan,
                  reel.iat[0] if len(reel) else np.nan)
    return out


def fmt(x, n=2, signe=True):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return '—'
    return f'{x:+.{n}f}'.replace('.', ',') if signe else f'{x:.{n}f}'.replace('.', ',')


def fiche(mois, v, tx, ct, cal, av, tr):
    debut = pd.Timestamp(mois + '-01')
    fin = debut + pd.offsets.MonthEnd(0)
    L = [f'# {MOIS_FR[debut.month - 1].capitalize()} {debut.year}', '',
         f'*Fiche générée par `scripts/fiches_mensuelles.py`. Liens : messages du canal. Les résultats « 1 semaine » et '
         f'« 1 mois » mesurent la force de la devise contre la moyenne des 8 grandes devises, après la clôture du jour du '
         f'message. Méthode et limites : [`analyses/FICHES_MENSUELLES.md`](../FICHES_MENSUELLES.md).*', '']
    # 1. marché
    f = force(v, debut - pd.Timedelta(days=1), fin)
    L += ['## 1. Ce que le marché a fait', '']
    if f is not None:
        o = f.sort_values(ascending=False)
        L += ['Force des devises sur le mois (contre la moyenne des 8, en %) : ' +
              ', '.join(f'**{d}** {fmt(x)}' for d, x in o.items()), '']
    s = saisonnalite(mois)
    L += ['| Paire | Saisonnalité du mois (10 années précédentes) | Mois réel | Saisonnalité dans le bon sens ? |',
          '|---|---|---|---|']
    for p, (moy, pos, reel) in s.items():
        ok = '—' if np.isnan(reel) or np.isnan(moy) else ('oui' if np.sign(moy) == np.sign(reel) else 'non')
        L.append(f'| {p} | {fmt(moy)} % ({fmt(pos * 100 if not np.isnan(pos) else np.nan, 0, False)} % de mois positifs) | '
                 f'{fmt(reel)} % | {ok} |')
    L.append('')
    # 2. banques centrales et annonces
    L += ['## 2. Banques centrales et annonces', '']
    t0 = tx[tx.index < debut].iloc[-1] if len(tx[tx.index < debut]) else None
    t1 = tx[tx.index <= fin].iloc[-1]
    chg = [f'{d} {fmt(t0[d], 2, False)} → {fmt(t1[d], 2, False)} %' for d in DEVISES
           if t0 is not None and d in t1 and not np.isnan(t1[d]) and abs(t1[d] - t0[d]) > 1e-9]
    L += ['- Taux directeurs modifiés : ' + ('; '.join(chg) if chg else 'aucun') + ' (BIS).']
    ev = cal[(cal['date'] >= debut) & (cal['date'] <= fin + pd.Timedelta(days=1)) & (cal['importance'] == 1)
             & cal['devise'].isin(DEVISES) & cal['titre'].str.contains('|'.join(CLES), regex=True, na=False)
             & ~cal['titre'].str.contains('Flash|Prel|MoM', regex=True, na=False)]
    if len(ev):
        L += ['', '| Date (UTC) | Devise | Annonce | Réel | Consensus | Surprise |', '|---|---|---|---|---|---|']
        for _, e in ev.sort_values('date').iterrows():
            sur = '—'
            if not np.isnan(e['actuel']) and not np.isnan(e['consensus']):
                dd = e['actuel'] - e['consensus']
                sur = 'en ligne' if abs(dd) < 1e-9 else ('au-dessus' if dd > 0 else 'en dessous')
            L.append(f"| {e['date']:%d/%m %H:%M} | {e['devise']} | {e['titre']} | {fmt(e['actuel'], 2, False)} | "
                     f"{fmt(e['consensus'], 2, False)} | {sur} |")
    L.append('')
    # 3. COT
    L += ['## 3. Positionnement des gérants d\'actifs (COT)', '']
    c0 = ct[ct.index < debut]
    c1 = ct[ct.index <= fin]
    if len(c0) and len(c1):
        hist = ct[(ct.index <= fin) & (ct.index > fin - pd.Timedelta(days=3 * 365))]
        lig = []
        for d in DEVISES:
            if d not in ct or np.isnan(c1[d].iloc[-1]):
                continue
            pct = (hist[d] <= c1[d].iloc[-1]).mean() * 100
            extreme = ' (extrême acheteur sur 3 ans)' if pct >= 90 else (' (extrême vendeur sur 3 ans)' if pct <= 10 else '')
            lig.append(f"{d} {int(c1[d].iloc[-1]):+,} ({int(c1[d].iloc[-1] - c0[d].iloc[-1]):+,} sur le mois){extreme}"
                       .replace(',', ' '))
        L += ['- ' + '; '.join(lig), '']
    # 4. avis
    a = av[av['date'].str[:7] == mois]
    L += ['## 4. Ce qu\'Amirou a écrit (avis directionnels)', '']
    if len(a):
        L += ['| Date (UTC) | Message | Devise | Sens | Extrait | 1 semaine | 1 mois |', '|---|---|---|---|---|---|---|']
        for _, x in a.iterrows():
            def res(n):
                if n not in x or pd.isna(x.get(n)):
                    return 'en cours'
                return ('✓ ' if x['juste ' + n] else '✗ ') + fmt(x[n]) + ' %'
            L.append(f"| {x['date'][8:10]}/{x['date'][5:7]} {x['date'][11:16]} | [#{x['id']}]({LIEN.format(x['id'])}) | "
                     f"{x['devise']} | {x['sens']} | {x['extrait'].replace('|', '/')} | {res('1 semaine')} | {res('1 mois')} |")
        for n in ['1 semaine', '1 mois']:
            k = a['juste ' + n].dropna() if 'juste ' + n in a else pd.Series(dtype=float)
            if len(k):
                L.append(f'\nAvis justes à {n} : **{int(k.sum())} sur {len(k)}** ({k.mean():.0%}).')
    else:
        L.append('Aucun avis directionnel repéré par le lexique ce mois-ci.')
    L.append('')
    # 5. trades
    t = tr[tr['mois'] == mois]
    L += ['## 5. Ses trades du mois (rejoués sur les cours)', '']
    if len(t):
        L += ['| Date (UTC) | Message | Paire | Sens | Publication | Selon les cours | R |', '|---|---|---|---|---|---|---|']
        for _, x in t.iterrows():
            lien = f"[#{int(x['id_message'])}]({LIEN.format(int(x['id_message']))})" if not pd.isna(x['id_message']) else '—'
            L.append(f"| {x['date'][8:10]}/{x['date'][5:7]} {x['date'][11:16]} | {lien} | {x['paire']} | {x['sens']} | "
                     f"{x['statut_rejeu'] if isinstance(x['statut_rejeu'], str) else '—'} | "
                     f"{x['issue_rejeu'] if isinstance(x['issue_rejeu'], str) else '—'} | {fmt(x['r'])} |")
        an = t[(t['statut_rejeu'] == 'annoncé') & t['r'].notna()]
        if len(an):
            L.append(f"\nTrades annoncés avant l'entrée et exécutés : {len(an)}, gagnants {int((an['r'] > 0).sum())}, "
                     f"total **{fmt(an['r'].sum())} R**.")
    else:
        L.append('Aucun trade relevé ce mois-ci.')
    L += ['', '## 6. À retenir', '', '*(à compléter : ce qui a marché, ce qui n\'a pas marché, et pourquoi)*', '']
    return '\n'.join(L), a, t


def main():
    v = valeurs_usd()
    tx, ct, cal = taux(), cot(), calendrier()
    av = avis_amirou(v)
    os.makedirs('data/fiches_mensuelles', exist_ok=True)
    av.to_csv('data/fiches_mensuelles/avis.csv', index=False)
    tr = pd.read_csv('data/verification_trades.csv')
    tr['date'] = tr['date'].astype(str)
    os.makedirs(DOSSIER, exist_ok=True)
    bilan = []
    for mois in pd.period_range(DEBUT, FIN, freq='M').astype(str):
        texte, a, t = fiche(mois, v, tx, ct, cal, av, tr)
        open(f'{DOSSIER}/{mois}.md', 'w', encoding='utf-8').write(texte)
        an = t[(t['statut_rejeu'] == 'annoncé') & t['r'].notna()]
        f = force(v, pd.Timestamp(mois + '-01') - pd.Timedelta(days=1), pd.Timestamp(mois + '-01') + pd.offsets.MonthEnd(0))
        bilan.append(dict(mois=mois, forte=f.idxmax() if f is not None else '', faible=f.idxmin() if f is not None else '',
                          avis=len(a), justes_1s=a['juste 1 semaine'].mean() if 'juste 1 semaine' in a and len(a) else np.nan,
                          justes_1m=a['juste 1 mois'].mean() if 'juste 1 mois' in a and len(a) else np.nan,
                          trades=len(an), r=an['r'].sum() if len(an) else 0.0))
    b = pd.DataFrame(bilan)
    b.to_csv('data/fiches_mensuelles/bilan.csv', index=False)
    print(b.to_string(index=False))
    for n in ['1 semaine', '1 mois']:
        k = av['juste ' + n].dropna()
        print(n, len(k), round(k.mean(), 3))


if __name__ == '__main__':
    main()
