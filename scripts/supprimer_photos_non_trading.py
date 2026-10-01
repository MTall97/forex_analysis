#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Supprime de ChatExport_2026-10-01/photos/ les photos classées comme non liées au trading
dans data/photos_classification.csv (colonne « supprimee » = oui), ainsi que leurs miniatures.

Classement (fait à la main, planche par planche, sur les 3 568 photos du canal) :
    trading       graphiques, ordres, historiques MT4/MT5, journaux de trading, schémas  -> gardée
    conversation  captures de discussions (témoignages, échanges avec élèves)           -> gardée
    certificat    certificats de prop firms des élèves (FTMO, MFF, AQRE, …)              -> supprimée
    autre         photos personnelles, voitures, événements, publicités, mèmes, Facebook -> supprimée

Par défaut le script n'efface rien et affiche ce qu'il ferait. Ajouter --confirmer pour supprimer.
Les fichiers restent récupérables dans l'historique Git tant que celui-ci n'est pas purgé.

Usage :
    python scripts/supprimer_photos_non_trading.py              # simulation
    python scripts/supprimer_photos_non_trading.py --confirmer  # suppression
"""

import argparse
import csv
import os


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--classement', default='data/photos_classification.csv')
    p.add_argument('--export', default='ChatExport_2026-10-01')
    p.add_argument('--confirmer', action='store_true')
    args = p.parse_args()

    cibles = []
    with open(args.classement, encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r['supprimee'] == 'oui':
                photo = os.path.join(args.export, r['photo'])
                cibles += [photo, photo.replace('.jpg', '_thumb.jpg')]
    cibles = [c for c in cibles if os.path.exists(c)]
    taille = sum(os.path.getsize(c) for c in cibles)
    print(f"{len(cibles)} fichiers ({taille / 1e6:.1f} Mo) {'supprimés' if args.confirmer else 'à supprimer (simulation)'}")
    if args.confirmer:
        for c in cibles:
            os.remove(c)


if __name__ == '__main__':
    main()
