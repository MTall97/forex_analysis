#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suivi en démo du narratif d'Amirou, à côté du suivi englobante + MLQ (scripts/suivi_demo_englobante_mlq.py), sans
changer la règle de ce suivi : on ajoute seulement à chaque signal l'avis qu'Amirou avait écrit dans le canal.

Narratif d'un signal sur la paire A/B, le jour J :
  somme de son biais écrit sur A les 14 jours avant J (J exclu)  -  même somme sur B
  (data/fondamental/biais_amirou.csv, produit par scripts/biais_textuel.py à partir de data/telegram_messages.jsonl
  et des rapports SignalX en PDF).
  > 0 et signal à l'achat : « dans le sens » ; < 0 : « contre » ; 0 : « sans avis ».
Si le canal n'est pas à jour (dernier message plus ancien que la veille du signal), le narratif est « à compléter » :
il faut d'abord ajouter le nouvel export du canal.

Critère fixé à l'avance (analyses/SUIVI_DEMO.md) : quand chaque groupe (« dans le sens », « contre ou sans avis »)
compte au moins 30 trades clôturés, le narratif est jugé utile si le groupe « dans le sens » fait au moins 0,2 R de
plus par trade que l'autre ; sinon il n'apporte rien à cette stratégie.

Ordre de mise à jour :
    python scripts/prix_yahoo.py --mettre-a-jour AUDJPY AUDUSD EURJPY EURNZD EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDJPY
    python scripts/suivi_demo_englobante_mlq.py
    (nouvel export du canal -> data/telegram_messages.jsonl, voir CLAUDE.md)
    python scripts/biais_textuel.py
    python scripts/suivi_demo_narratif.py
Sortie : data/suivi_demo/journal_narratif.csv et bilan à l'écran.
"""
import json
import os

import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
JOURNAL = 'data/suivi_demo/journal_englobante_mlq.csv'
SORTIE = 'data/suivi_demo/journal_narratif.csv'
FENETRE = 14


def dernier_message():
    d = None
    with open('data/telegram_messages.jsonl', encoding='utf-8') as f:
        for l in f:
            d = json.loads(l)['date_utc']
    return pd.Timestamp(d[:10])


def main():
    j = pd.read_csv(JOURNAL)
    b = pd.read_csv('data/fondamental/biais_amirou.csv', parse_dates=['date'])
    fin_canal = dernier_message()
    lignes = []
    for _, s in j.iterrows():
        jour = pd.Timestamp(s['date_signal'])
        fen = b[(b['date'] >= jour - pd.Timedelta(days=FENETRE)) & (b['date'] < jour)]
        base, cote = s['paire'][:3], s['paire'][3:]
        sb, sc = fen.loc[fen['devise'] == base, 'score'].sum(), fen.loc[fen['devise'] == cote, 'score'].sum()
        score = int(sb - sc)
        sens = 1 if s['sens'] == 'achat' else -1
        if fin_canal < jour - pd.Timedelta(days=1):
            narratif = 'à compléter'
        elif score == 0:
            narratif = 'sans avis'
        else:
            narratif = 'dans le sens' if score * sens > 0 else 'contre'
        lignes.append(dict(s, biais_base=int(sb), biais_cote=int(sc), score_narratif=score, narratif=narratif))
    d = pd.DataFrame(lignes)
    d.to_csv(SORTIE, index=False)
    pd.set_option('display.width', 220)
    print(d[['date_signal', 'paire', 'sens', 'statut', 'r_net', 'biais_base', 'biais_cote', 'narratif']].to_string(index=False))
    print(f"\nCanal à jour jusqu'au {fin_canal:%d/%m/%Y}.")
    d['r'] = pd.to_numeric(d['r_net'], errors='coerce')
    d['groupe'] = d['narratif'].map({'dans le sens': 'dans le sens', 'contre': 'contre ou sans avis',
                                     'sans avis': 'contre ou sans avis'}).fillna('à compléter')
    for g, x in d.groupby('groupe'):
        c = x['r'].dropna()
        print(f"{g:20s} : {len(x)} signaux, {len(c)} clôturés" + (f", R moyen {c.mean():+.2f}" if len(c) else ''))


if __name__ == '__main__':
    main()
