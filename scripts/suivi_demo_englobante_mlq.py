#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Suivi « en démo », hors échantillon, de la seule piste positive des tests de la masterclass
(analyses/MASTERCLASS_TRADES_DATES.md, section 4) : ACHAT sur englobante journalière haussière dont
le plus bas touche un niveau MLQ (multiple de 250 pips) à 25 pips près.

Règle, identique au test (scripts/strategie_combinee.py), sans rien changer :
- bougie J haussière qui englobe le corps de la bougie J-1 baissière ;
- plus bas de J à 25 pips ou moins d'un multiple de 250 pips ;
- entrée à la clôture de J, stop sous le plus bas de J (2 pips), objectif 2 R ;
- sortie au stop, à l'objectif, sinon à la clôture du 3e jour ; si stop et objectif sont touchés
  le même jour, on compte le stop ; spread déduit ;
- 10 paires : AUDJPY AUDUSD EURJPY EURNZD EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDJPY.
Les jours sont des bougies 00h-24h UTC reconstruites depuis l'horaire Yahoo, comme pour l'année en cours
dans les tests.

Le suivi commence le 2026-10-02, au lendemain des dernières données utilisées pour trouver la piste :
seuls ces trades disent si l'avantage est réel. À relancer chaque jour (ou chaque semaine) :
    python scripts/prix_yahoo.py --mettre-a-jour AUDJPY AUDUSD EURJPY EURNZD EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDJPY
    python scripts/suivi_demo_englobante_mlq.py
Sortie : data/suivi_demo/journal_englobante_mlq.csv (recalculé entièrement à chaque lancement) et bilan.
Critère fixé à l'avance : après 30 à 60 trades, la piste mérite d'être prise au sérieux si le R moyen
reste au-dessus de +0,1 R ; sous 0, elle est abandonnée.
"""
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)
sys.path.insert(0, os.path.join(RACINE, 'scripts'))
from prix_dukascopy_journalier import depuis_yahoo  # noqa: E402
from tester_masterclass import pip, spread  # noqa: E402

PAIRES = ['AUDJPY', 'AUDUSD', 'EURJPY', 'EURNZD', 'EURUSD', 'GBPJPY', 'GBPUSD', 'NZDUSD', 'USDCAD', 'USDJPY']
DEBUT_SUIVI = '2026-10-02'
SORTIE = 'data/suivi_demo/journal_englobante_mlq.csv'


def journalier(p):
    rows = depuis_yahoo(p, pd.Timestamp('2026-09-01'))
    d = pd.DataFrame(rows, columns=['paire', 'date', 'open', 'high', 'low', 'close'])
    aujourd_hui = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    return d[d['date'] < aujourd_hui].reset_index(drop=True)  # le jour en cours n'est pas terminé


def signaux(p, d):
    pp, pas = pip(p), 250 * pip(p)
    o, h, l, c = (d[k].to_numpy() for k in ['open', 'high', 'low', 'close'])
    out = []
    for i in range(1, len(d)):
        if d['date'][i] < DEBUT_SUIVI:
            continue
        if not (c[i] > o[i] and c[i - 1] < o[i - 1] and abs(c[i] - o[i]) >= abs(c[i - 1] - o[i - 1])):
            continue
        if abs(l[i] - round(l[i] / pas) * pas) > 25 * pp:
            continue
        sl = l[i] - 2 * pp
        risque = c[i] - sl
        if risque < 5 * pp:
            continue
        tp = c[i] + 2 * risque
        statut, sortie, r = 'ouvert', '', np.nan
        for j in range(i + 1, min(i + 4, len(d))):
            if l[j] <= sl:
                statut, sortie, r = 'stop', d['date'][j], -1.0
                break
            if h[j] >= tp:
                statut, sortie, r = 'objectif', d['date'][j], 2.0
                break
            if j == i + 3:
                statut, sortie, r = 'sortie 3e jour', d['date'][j], (c[j] - c[i]) / risque
        if not np.isnan(r):
            r -= spread(p) / risque
        out.append(dict(date_signal=d['date'][i], paire=p, sens='achat', entree=round(c[i], 5), stop=round(sl, 5),
                        objectif=round(tp, 5), niveau_mlq=round(round(l[i] / pas) * pas, 3),
                        risque_pips=round(risque / pp, 1), statut=statut, date_sortie=sortie,
                        r_net=round(r, 3) if not np.isnan(r) else ''))
    return out


def main():
    lignes = []
    for p in PAIRES:
        d = journalier(p)
        lignes += signaux(p, d)
    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    cols = ['date_signal', 'paire', 'sens', 'entree', 'stop', 'objectif', 'niveau_mlq', 'risque_pips', 'statut',
            'date_sortie', 'r_net']
    j = pd.DataFrame(lignes, columns=cols).sort_values(['date_signal', 'paire'])
    j.to_csv(SORTIE, index=False)
    fini = pd.to_numeric(j['r_net'], errors='coerce').dropna()
    print(j.to_string(index=False) if len(j) else 'Aucun signal depuis le ' + DEBUT_SUIVI)
    print(f"\n{len(j)} signaux depuis le {DEBUT_SUIVI}, {len(fini)} clôturés, "
          f"R moyen {fini.mean():+.2f} R" if len(fini) else f"\n{len(j)} signaux, aucun clôturé")


if __name__ == '__main__':
    main()
