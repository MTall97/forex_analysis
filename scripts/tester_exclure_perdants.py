#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Écarter, pour chaque stratégie, les trades « qui perdent le plus » : paires perdantes, mois perdants (saisonnalité
propre à la stratégie), paire x mois, paire x sens, jour de la semaine. Deux mesures :
- après coup (« dans l'échantillon ») : les cases perdantes sont repérées sur tous les trades, puis retirées de ces
  mêmes trades. C'est ce qu'on fait en regardant un tableau de résultats ; le gain est toujours positif par construction ;
- en conditions réelles (walk-forward) : pour chaque trimestre, les cases perdantes sont repérées sur les seuls trades
  entrés au moins 10 jours avant le début du trimestre, puis on regarde le trimestre. Test à partir de 2025 pour les
  stratégies 2024-2026 (au moins 12 mois d'historique), à partir de 2015 pour l'englobante journalière 2012-2026.
Une case n'est écartée que si elle a assez de trades dans l'historique (MIN) et une moyenne négative.
Trades : data/filtres_playbook/trades.csv.gz (les mêmes que le journal des stratégies).
Sortie : data/exclure_perdants/resultats.csv
"""
import os

import numpy as np
import pandas as pd

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(RACINE)

FILTRES = {'paires perdantes': (['paire'], 8), 'mois perdants': (['mois'], 8), 'paire x mois perdants': (['paire', 'mois'], 3),
           'paire x sens perdants': (['paire', 'sens'], 8), 'jours perdants': (['jour'], 8)}


def perdantes(h, cles, mini):
    g = h.groupby(cles)['r'].agg(['mean', 'count'])
    return set(g[(g['count'] >= mini) & (g['mean'] < 0)].index)


def cle(t, cles):
    return list(t[cles[0]]) if len(cles) == 1 else list(zip(*[t[c] for c in cles]))


def main():
    t = pd.read_csv('data/filtres_playbook/trades.csv.gz', parse_dates=['te'])
    t['mois'], t['jour'], t['trim'] = t['te'].dt.month, t['te'].dt.weekday, t['te'].dt.to_period('Q')
    res = []
    for s, g in t.groupby('strategie'):
        debut = pd.Timestamp('2015-01-01' if 'journalier' in s else '2025-01-01')
        test = g[g['te'] >= debut]
        for nom, (cles, mini) in FILTRES.items():
            # après coup, sur la période de test
            P = perdantes(g, cles, mini)
            ecarte_in = np.array([k in P for k in cle(test, cles)])
            # walk-forward
            ecarte = np.zeros(len(test), bool)
            for q, x in test.groupby('trim'):
                h = g[g['te'] < q.start_time - pd.Timedelta(days=10)]
                P = perdantes(h, cles, mini)
                ecarte[test.index.get_indexer(x.index)] = [k in P for k in cle(x, cles)]
            r = test['r'].to_numpy()
            for mesure, e in [('après coup', ecarte_in), ('walk-forward', ecarte)]:
                gard = r[~e]
                res.append(dict(strategie=s, test_depuis=str(debut.date()), filtre=nom, mesure=mesure, trades=len(r),
                                r_tous=round(r.mean(), 3), ecartes=int(e.sum()), r_ecartes=round(r[e].mean(), 3) if e.any() else None,
                                r_gardes=round(gard.mean(), 3) if len(gard) else None,
                                gain_par_trade=round(gard.mean() - r.mean(), 3) if len(gard) else None,
                                total_R_tous=round(r.sum(), 1), total_R_gardes=round(gard.sum(), 1),
                                erreur_type=round(gard.std() / np.sqrt(len(gard)), 3) if len(gard) > 1 else None))
    r = pd.DataFrame(res)
    os.makedirs('data/exclure_perdants', exist_ok=True)
    r.to_csv('data/exclure_perdants/resultats.csv', index=False)
    pd.set_option('display.width', 250)
    print(r[['strategie', 'filtre', 'mesure', 'trades', 'r_tous', 'ecartes', 'r_ecartes', 'r_gardes', 'gain_par_trade',
             'total_R_tous', 'total_R_gardes']].to_string(index=False))


if __name__ == '__main__':
    main()
