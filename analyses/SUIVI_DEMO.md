# Suivi en démo : achat sur englobante qui rejette un MLQ

*Commencé le 06/10/2026. Script : [`scripts/suivi_demo_englobante_mlq.py`](../scripts/suivi_demo_englobante_mlq.py). Journal : [`data/suivi_demo/journal_englobante_mlq.csv`](../data/suivi_demo/journal_englobante_mlq.csv).*

## Pourquoi

C'est la seule piste positive des tests de la masterclass ([`MASTERCLASS_TRADES_DATES.md`](MASTERCLASS_TRADES_DATES.md), section 4) :
- +0,20 R par trade de 2020 à 2026, sur 420 trades ;
- mais rien de 2012 à 2019 (−0,02 R) ;
- et la séparation entre achats et ventes a été choisie après avoir vu les résultats.

Seuls des trades **postérieurs** à la découverte peuvent dire si l'avantage est réel. Le suivi commence donc le **02/10/2026**, au lendemain des dernières données utilisées.

## La règle (fixée à l'avance, inchangée)

- **Signal** : bougie journalière (00h-24h UTC) haussière dont le corps englobe celui de la bougie baissière de la veille.
- **Condition MLQ** : son plus bas est à 25 pips ou moins d'un multiple de 250 pips.
- **Entrée** à la clôture.
- **Stop** 2 pips sous le plus bas.
- **Objectif** à 2 R.
- **Sortie** au stop, à l'objectif ou à la clôture du 3e jour. Si le stop et l'objectif sont touchés le même jour, on compte le stop.
- **Spread** déduit.
- **10 paires** : AUDJPY, AUDUSD, EURJPY, EURNZD, EURUSD, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDJPY.

## Critère de décision (fixé à l'avance)

| Après 30 à 60 trades | Décision |
|---|---|
| R moyen ≥ +0,10 R | piste sérieuse, à poursuivre avec un risque réduit |
| entre 0 et +0,10 R | non concluant, continuer le suivi |
| R moyen < 0 | piste abandonnée |

Fréquence attendue : environ 60 signaux par an sur les 10 paires, soit 30 trades en 6 mois.

## Mettre à jour

```
python scripts/prix_yahoo.py --mettre-a-jour AUDJPY AUDUSD EURJPY EURNZD EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDJPY
python scripts/suivi_demo_englobante_mlq.py
```

Le journal est recalculé entièrement à chaque lancement, à partir des cours.

## Journal au 06/10/2026

| Signal | Paire | Entrée | Stop | Objectif | Niveau MLQ | Statut |
|---|---|---|---|---|---|---|
| 02/10/2026 | GBPJPY | 209,071 | 207,638 | 211,937 | 207,5 | ouvert |
| 05/10/2026 | USDJPY | 157,954 | 157,412 | 159,038 | 157,5 | ouvert |
