#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Saisonnalité intrajournalière du Forex (effet décrit par Breedon et Ranaldo, 2013) : une devise tend à
se DÉPRÉCIER pendant les heures de bureau de son propre pays et à s'apprécier pendant celles des autres.

Données : bougies horaires Yahoo (déc. 2023 -> sept. 2026), devises contre le dollar.
Fenêtres (heures UTC) :
- Asie   : 23h-07h (JPY, AUD, NZD) ;
- Europe : 07h-12h (EUR, GBP, CHF), avant l'ouverture de New York ;
- États-Unis : 13h-20h.

Mesures :
1. rendement moyen de chaque devise contre le dollar par heure UTC (profil) ;
2. stratégie « Breedon-Ranaldo » : chaque jour, VENDRE la devise contre le dollar pendant ses heures
   locales et l'ACHETER pendant les heures américaines ; panier de 6 devises (EUR, GBP, CHF, JPY, AUD, NZD) ;
   résultat brut, puis net d'un spread par aller-retour (2 allers-retours par jour et par devise).
   Validation : 2024 contre 2025-2026.

Sorties : data/saisonnalite_intraday_profil.csv, data/saisonnalite_intraday_strategie.csv, résumé écran.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
import prix_yahoo  # noqa: E402
from modele_meta import SPREAD  # noqa: E402

DEVISES = {'EUR': ('EURUSD', 'europe'), 'GBP': ('GBPUSD', 'europe'), 'CHF': ('USDCHF', 'europe'),
           'JPY': ('USDJPY', 'asie'), 'AUD': ('AUDUSD', 'asie'), 'NZD': ('NZDUSD', 'asie')}
FENETRES = {'asie': (23, 7), 'europe': (7, 12), 'usa': (13, 20)}


def dans(h, f):
    a, b = FENETRES[f]
    return (h >= a) | (h < b) if a > b else (h >= a) & (h < b)


def rendements(dev):
    paire, _ = DEVISES[dev]
    d = prix_yahoo._charger(paire, '1h').copy()
    d['date'] = pd.to_datetime(d.date)
    d = d.set_index('date').sort_index()
    r = np.log(d.close / d.close.shift(1))
    r = r[(d.index.to_series().diff() <= pd.Timedelta(hours=1))]       # pas de trou (week-end)
    if paire.startswith('USD'):
        r = -r                                                           # rendement de la devise contre le dollar
    pip = 0.01 if paire.endswith('JPY') else 0.0001
    cout = SPREAD.get(paire, 1.5) * pip / d.close.mean()                 # spread en % du prix
    return r.dropna(), cout


def main():
    profil, journalier = {}, []
    for dev, (paire, region) in DEVISES.items():
        r, cout = rendements(dev)
        h = r.index.hour
        profil[dev] = (r.groupby(h).mean() * 1e4).round(3)                # en points de base par heure
        jour = r.index.normalize()
        local = (-r[dans(h, region)]).groupby(jour[dans(h, region)]).sum()
        usa = r[dans(h, 'usa')].groupby(jour[dans(h, 'usa')]).sum()
        x = pd.DataFrame({'local': local, 'usa': usa}).fillna(0)
        x['brut'] = x.local + x.usa
        x['net'] = x.brut - 2 * cout
        x['devise'] = dev
        journalier.append(x)
    prof = pd.DataFrame(profil)
    prof.index.name = 'heure_utc'
    prof.to_csv('data/saisonnalite_intraday_profil.csv')
    j = pd.concat(journalier)
    j.index.name = 'jour'
    j.to_csv('data/saisonnalite_intraday_strategie.csv')
    panier = j.groupby(level=0)[['local', 'usa', 'brut', 'net']].mean()
    print('Rendement moyen de la devise contre le dollar par heure UTC (points de base) :')
    print(prof.to_string())

    def st(s):
        return (f"{s.mean() * 1e4:+.2f} pb/jour, {s.mean() * 252 * 100:+.1f} %/an, t = "
                f"{s.mean() / s.std() * np.sqrt(len(s)):+.2f}, jours positifs {(s > 0).mean() * 100:.0f} %")
    print('\nStratégie Breedon-Ranaldo, panier de 6 devises :')
    for c in ['local', 'usa', 'brut', 'net']:
        print(f"  {c:<6}: {st(panier[c])}")
    for per, m in [('2024', panier.index.year == 2024), ('2025-2026', panier.index.year >= 2025)]:
        print(f"  {per}: brut {st(panier.brut[m])} | net {st(panier.net[m])}")
    print('\nPar devise (brut) :')
    for dev, g in j.groupby('devise'):
        print(f"  {dev}: brut {st(g.brut)} | net {st(g.net)}")


if __name__ == '__main__':
    main()
