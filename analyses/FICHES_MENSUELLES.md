# Fiches mensuelles et tracker saisonnalité & fonda (janvier 2023 - octobre 2026)

*17/10/2026. Sur le modèle de la base Notion de l'utilisateur, « Tracker Forex saisonnalité & fonda EURUSD ».*

- **Page interactive (tracker)** : `scripts/construire_carnet_html.py DOSSIER` produit `data.json` et les captures. La page est `docs/tracker/tracker.html` : y insérer `data.json` à la place de `{{DONNEES}}`, et publier les captures à côté dans `captures/`. EURUSD, GBPUSD, AUDUSD et USDJPY ; une ligne par mois avec :
  - statut ;
  - saisonnalité sur 3, 5, 10 et 20 ans ;
  - explication fonda : taux, annonces, COT ;
  - messages d'Amirou avec leur lien et ce que la paire a fait 1 semaine et 1 mois après ;
  - ses trades avec leur capture et leur résultat rejoué.
- **Fiches texte** : `scripts/fiches_mensuelles.py` → `analyses/fiches_mensuelles/AAAA-MM.md`. Elles couvrent toutes les devises, et les avis y sont mesurés contre la moyenne des 8 devises.

## Méthode et limites
- **Le sens d'un message est lu automatiquement** par le lexique de `scripts/biais_textuel.py`. Il se trompe parfois : par exemple, « la BCE a annoncé la fin de son cycle de baisse » (#13812) est lu comme baissier pour l'euro. La page laisse corriger le sens message par message. Les mouvements en pips après le message, eux, sont factuels.
- **Résultats bruts des avis**, en force de la devise contre la moyenne des 8 :
  - 430 avis à 1 semaine : 53 % justes ;
  - 423 avis à 1 mois : 48 % justes.

  Mesurés sur les quatre paires, ils sont suivis par la paire dans 47 à 50 % des cas. C'est le niveau du hasard. Cela ne dit rien de ses trades, mesurés à part, mais cela montre que ses commentaires de marché pris un par un ne prédisent pas le sens.
- **Saisonnalité sur 10 ans, EURUSD** : bon sens 27 mois sur 46 (59 %).
- **Les données** :
  - mois : Fed H.10 (`data/rendements_mensuels.csv`) ;
  - cours journaliers : Dukascopy, puis Yahoo ;
  - taux : BIS ;
  - annonces : calendrier TradingView ;
  - COT : CFTC (gérants d'actifs) ;
  - trades : `data/verification_trades.csv`.
