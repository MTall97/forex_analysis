#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Confronte les trades du registre (data/trades.csv) à la saisonnalité et au mouvement réel du mois.

Pour chaque trade dont la paire et le sens sont connus :
- biais_exante : biais saisonnier du mois calculé sur les 10 années PRÉCÉDANT le trade
                 (ce qu'un trader pouvait connaître à la date du trade) ;
- biais_projet : biais 2020-2025 (celui des PDF du projet, donc partiellement rétrospectif) ;
- alignement   : « avec » si le sens du trade suit le biais ex-ante, « contre » s'il s'y oppose,
                 « neutre » si le mois n'a pas de biais ;
- alignement_moyenne : version plus souple, sens du trade comparé au signe de la moyenne 10 ans ;
- mois_reel    : rendement réel de la paire sur le mois du trade, et si ce mois a suivi son biais ;
- cause_sl     : pour les stops touchés, cause déduite du texte du canal (± 2 jours).

Sorties : data/trades_saisonnalite.csv et data/mois_hors_saisonnalite.csv
"""

import csv
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import mean, pstdev

GAGNANT = {'tp', 'gain'}
PERDANT = {'sl'}
CAUSES = [
    ('annonce économique', r"annonce|nfp|cpi|inflation|taux d'int|fed\b|fomc|bce|boe|boj|rba|powell|lagarde|ueda|news|nouvelle|discours|banque centrale|statement|chômage|chomage"),
    ('stop serré / chasse aux stops', r"quelques pips|de justesse|manipul|market makers?|chasse|spread|liquidit|avant de (changer|monter|s'envoler|partir|aller)|est (revenu|allé) dans notre sens|partir direct au tp|revenu dans notre sens"),
    ('entrée prématurée / sans confirmation', r"confirmation|contre[- ]tendance|trop t[oô]t|pas de confirm|notre propre faute|anticip"),
    ('géopolitique / politique', r"trump|guerre|tarif|douan|géopolit|geopolit|élection|election|brexit|iran|ormuz|covid|virus|crise"),
]


def biais(vals):
    if len(vals) < 4:
        return 'neutre'
    pos = sum(v > 0 for v in vals) / len(vals)
    m = mean(vals)
    return 'haussier' if pos >= 2 / 3 and m > 0 else 'baissier' if pos <= 1 / 3 and m < 0 else 'neutre'


def main():
    rend = defaultdict(dict)
    for r in csv.DictReader(open('data/rendements_mensuels.csv', encoding='utf-8')):
        rend[r['paire']][r['mois']] = float(r['rendement_pct'])
    projet = {}
    for r in csv.DictReader(open('data/saisonnalite.csv', encoding='utf-8')):
        if r['periode'] == 'projet':
            projet[(r['paire'], int(r['mois']))] = r['biais']
    msgs = [json.loads(l) for l in open('data/telegram_messages.jsonl', encoding='utf-8')]

    def contexte(date, paire):
        d = datetime.fromisoformat(date)
        txt = [m['text'] for m in msgs
               if abs(datetime.fromisoformat(m['date_utc']) - d) <= timedelta(days=2)
               and (paire.lower() in m['text'].lower() or re.search(r'stop|sl\b|sortir', m['text'], re.I))]
        return ' '.join(txt).lower()

    out = []
    for t in csv.DictReader(open('data/trades.csv', encoding='utf-8')):
        p, s = t['paire'], t['sens']
        an, mo = int(t['date_utc'][:4]), int(t['date_utc'][5:7])
        r = dict(t)
        if p in rend:
            hist = [rend[p][f"{y}-{mo:02d}"] for y in range(an - 10, an) if f"{y}-{mo:02d}" in rend[p]]
            b = biais(hist)
            reel = rend[p].get(f"{an}-{mo:02d}")
            r['biais_exante'] = b
            r['biais_projet'] = projet.get((p, mo), '')
            r['rendement_mois_pct'] = '' if reel is None else f"{reel:.2f}"
            if reel is not None and b != 'neutre':
                r['mois_suit_saison'] = 'oui' if (reel > 0) == (b == 'haussier') else 'non'
            else:
                r['mois_suit_saison'] = ''
            if s in ('achat', 'vente') and b != 'neutre':
                r['alignement'] = 'avec' if (s == 'achat') == (b == 'haussier') else 'contre'
            else:
                r['alignement'] = 'neutre' if s in ('achat', 'vente') else ''
            r['moyenne_10_ans_pct'] = f"{mean(hist):.2f}" if hist else ''
            if s in ('achat', 'vente') and hist:
                r['alignement_moyenne'] = 'avec' if (s == 'achat') == (mean(hist) > 0) else 'contre'
            if s in ('achat', 'vente') and reel is not None:
                r['sens_vs_mois'] = 'avec' if (s == 'achat') == (reel > 0) else 'contre'
            else:
                r['sens_vs_mois'] = ''
        if t['issue'] in PERDANT:
            ctx = contexte(t['date_utc'] if not t['ids_issue'] else
                           next(m['date_utc'] for m in msgs if m['id'] == int(t['ids_issue'].split()[0])), p)
            r['cause_sl'] = next((nom for nom, rx in CAUSES if re.search(rx, ctx)), 'non expliquée')
        out.append(r)

    champs = list(out[0].keys())
    for c in ['biais_exante', 'biais_projet', 'moyenne_10_ans_pct', 'rendement_mois_pct', 'mois_suit_saison',
              'alignement', 'alignement_moyenne', 'sens_vs_mois', 'cause_sl']:
        if c not in champs:
            champs.append(c)
    with open('data/trades_saisonnalite.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=champs, restval='')
        w.writeheader()
        w.writerows(out)

    # Mois qui contredisent nettement leur biais saisonnier (2019-2026), paires principales
    principales = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'NZDUSD', 'USDCAD', 'USDCHF',
                   'EURJPY', 'GBPJPY', 'AUDJPY', 'EURGBP', 'GBPAUD', 'EURAUD', 'XAUUSD']
    lignes = []
    for p in principales:
        for mois, v in rend[p].items():
            an, mo = int(mois[:4]), int(mois[5:])
            if an < 2019:
                continue
            hist = [rend[p][f"{y}-{mo:02d}"] for y in range(an - 10, an) if f"{y}-{mo:02d}" in rend[p]]
            b = biais(hist)
            if b == 'neutre':
                continue
            sd = pstdev(hist) or 1
            ecart = (v - mean(hist)) / sd
            contraire = (v > 0) != (b == 'haussier')
            if contraire and abs(ecart) >= 1:
                lignes.append([p, mois, b, f"{mean(hist):.2f}", f"{v:.2f}", f"{ecart:.1f}"])
    lignes.sort(key=lambda l: (l[1], l[0]))
    with open('data/mois_hors_saisonnalite.csv', 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(['paire', 'mois', 'biais_10_ans', 'moyenne_10_ans_pct', 'rendement_reel_pct', 'ecart_en_sigma'])
        w.writerows(lignes)
    print(f"{len(out)} trades -> data/trades_saisonnalite.csv ; {len(lignes)} mois atypiques -> data/mois_hors_saisonnalite.csv")


if __name__ == '__main__':
    main()
