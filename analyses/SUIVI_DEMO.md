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

*Variante d'entrée testée à part, sans toucher à cette règle : l'entrée sur un FVG 1h ou 4h fait moins bien que l'entrée à la clôture ([`ENGLOBANTE_FVG.md`](ENGLOBANTE_FVG.md)).*

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

## Suivi du narratif (ajouté le 14/10/2026)

*Script : [`scripts/suivi_demo_narratif.py`](../scripts/suivi_demo_narratif.py). Journal : [`data/suivi_demo/journal_narratif.csv`](../data/suivi_demo/journal_narratif.csv). Pourquoi : [`NARRATIF_ET_STRATEGIES.md`](NARRATIF_ET_STRATEGIES.md).*

La règle ci-dessus ne change pas. On note seulement, pour chaque signal, si l'avis écrit d'Amirou dans le canal allait dans son sens.

- **Narratif** : pour la paire A/B le jour J, la somme de son biais écrit sur A pendant les 14 jours avant J, moins la même somme sur B (`data/fondamental/biais_amirou.csv`, tiré de ses messages et de ses rapports SignalX par `scripts/biais_textuel.py`).
- **Classement** : « dans le sens » (narratif acheteur pour un achat), « contre », « sans avis » (score nul), ou « à compléter » si le canal n'est pas à jour à la veille du signal.
- **Critère fixé à l'avance** : quand les deux groupes (« dans le sens » ; « contre ou sans avis ») comptent chacun au moins 30 trades clôturés, le narratif est jugé utile si le groupe « dans le sens » fait **au moins 0,2 R de plus par trade**. Sinon, il n'apporte rien à cette stratégie.
- **Limite** : le lexique ne repère que les phrases explicites (« l'euro est faible », « vendre EURUSD »). En octobre, seuls 7 jours ont un avis repéré : beaucoup de signaux risquent d'être « sans avis ».

Mise à jour complète :

```
python scripts/prix_yahoo.py --mettre-a-jour AUDJPY AUDUSD EURJPY EURNZD EURUSD GBPJPY GBPUSD NZDUSD USDCAD USDJPY
python scripts/suivi_demo_englobante_mlq.py
# ajouter le nouvel export du canal à data/telegram_messages.jsonl (voir CLAUDE.md)
python scripts/biais_textuel.py
python scripts/suivi_demo_narratif.py
```

## Journal au 14/10/2026

| Signal | Paire | Entrée | Stop | Objectif | Niveau MLQ | Statut | R net | Narratif d'Amirou (14 j) |
|---|---|---|---|---|---|---|---|---|
| 02/10/2026 | GBPJPY | 209,071 | 207,638 | 211,937 | 207,5 | sortie le 3e jour (07/10) | −0,14 | dans le sens (GBP +1, JPY −1) |
| 05/10/2026 | USDJPY | 157,954 | 157,412 | 159,038 | 157,5 | sortie le 3e jour (08/10) | +0,17 | dans le sens (USD +3, JPY −2) |
| 09/10/2026 | AUDJPY | 110,568 | 109,932 | 111,840 | 110,0 | ouvert | | dans le sens (JPY −1) |
| 13/10/2026 | AUDJPY | 110,565 | 110,003 | 111,689 | 110,0 | ouvert | | dans le sens (JPY −1) |

**Bilan** : 4 signaux, 2 clôturés, R moyen +0,01 R. Beaucoup trop tôt pour conclure : il en faut au moins 30.
