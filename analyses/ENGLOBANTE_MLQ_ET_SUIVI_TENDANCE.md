# Englobante + MLQ et suivi de tendance : objectifs de 1 R, 2 R et 3 R

*Rédigé le 06/10/2026, à la demande de l'utilisateur. Scripts : [`scripts/tester_englobante_mlq_objectifs.py`](../scripts/tester_englobante_mlq_objectifs.py), [`scripts/tester_suivi_tendance.py`](../scripts/tester_suivi_tendance.py) ; résultats : [`data/englobante_mlq_objectifs/`](../data/englobante_mlq_objectifs/), [`data/suivi_tendance/`](../data/suivi_tendance/).*

## 1. Englobante sur un MLQ

**Règle** : bougie journalière qui englobe le corps de la veille de couleur opposée ; son extrême (plus bas pour un achat, plus haut pour une vente) est à 25 pips ou moins d'un multiple de 250 pips (MLQ). Entrée à la clôture, stop 2 pips au-delà de l'extrême, objectif 1, 2 ou 3 R, sortie au plus tard à la clôture du 3e jour, spread déduit.

**Témoins** : les mêmes englobantes près de **niveaux décalés** de 125 pips (des niveaux sans signification, aussi nombreux), et **toutes les englobantes**.

**R moyen par trade** (nombre de trades) :

| Rejeu | Période | Groupe | 1 R | 2 R | 3 R |
|---|---|---|---|---|---|
| journalier, 10 paires | 2012-2019 | **MLQ, achats et ventes** | −0,09 (1 097) | −0,06 | −0,05 |
| | | niveaux décalés (témoin) | −0,03 (991) | +0,02 | +0,02 |
| | 2020-2026 | **MLQ, achats** | +0,08 (420) | **+0,20** (±0,06) | +0,20 |
| | | MLQ, ventes | −0,02 (456) | −0,03 | −0,01 |
| | | niveaux décalés (témoin) | −0,09 (900) | −0,06 | −0,06 |
| horaire, 22 paires | 2024-2026 | **MLQ, achats** | +0,11 (384) | +0,15 (±0,06) | +0,14 |
| | | MLQ, ventes | +0,07 (373) | +0,05 | +0,02 |
| | | niveaux décalés (témoin) | −0,06 (812) | −0,06 | −0,05 |
| | | toutes les englobantes (témoin) | −0,04 (3 962) | −0,03 | −0,03 |

- **Depuis 2020, l'englobante sur un MLQ fait mieux que ses témoins**, surtout à l'achat : +0,15 à +0,20 R avec un objectif de 2 R, contre −0,06 R pour les niveaux décalés. Les cours horaires de 2024-2026, plus précis, sur 22 paires, le confirment.
- **Mais pas avant 2020** : sur 2012-2019, la même règle perd (−0,09 à −0,05 R) et fait moins bien que les niveaux décalés. L'avantage n'existe donc que sur une partie de l'histoire : c'est pourquoi la règle est suivie en démo avant d'y croire ([`SUIVI_DEMO.md`](SUIVI_DEMO.md)).
- **1 R contre 2 R** : 1 R fait gagner plus souvent (55-58 % de trades gagnants en horaire), mais rapporte moins par trade (+0,11 contre +0,15 R à l'achat). Les ventes sont faibles quel que soit l'objectif.

## 2. Votre suivi de tendance

**Règle**, tirée de vos trades de juin 2026 (vente ; l'achat est symétrique) :
- **tendance** : la clôture de la veille est au moins 1 ATR(14) journalier sous celle d'il y a 5 jours (variante : 2 ATR) ;
- **déclencheur**, entre 07h et 17h UTC :
  - « **cassure** » : vente 1 pip sous le plus bas de la veille ;
  - « **faux dépassement** » : le prix passe au-dessus du plus haut de la veille, puis une bougie 1h clôture de nouveau en dessous : vente à cette clôture (votre GBPUSD du 22/06) ;
- **stop** à 0,25 ATR de l'entrée, soit 20 pips en médiane, comme vos stops (variante : 0,5 ATR, 39 pips) ;
- **objectif 1 R** (2 R et 3 R pour comparer) ;
- **sortie à 20h UTC** si rien n'est touché, avant le rollover (variante : 20h le lendemain) ;
- spread déduit ; un trade par paire et par jour.

**Cours** : horaire Yahoo, 22 paires, décembre 2023 - octobre 2026. Le suivi commence à l'heure qui suit l'entrée (dans l'heure de la cassure, le plus bas s'est le plus souvent formé avant l'entrée). Quand une même heure touche le stop et l'objectif, l'ordre est inconnu : les deux cas ont été calculés, et l'écart ne dépasse jamais 0,06 R.

**Résultats avec un objectif de 1 R, sortie à 20h** (R moyen par trade, ± erreur type) :

| Déclencheur | Stop | Trades | Gagnants | R avant spread | **R net** | Témoin : toutes les cassures | Témoin : contre-tendance |
|---|---|---|---|---|---|---|---|
| Cassure | 0,25 ATR (20 pips) | 3 478 | 48 % | −0,04 | **−0,13** (±0,02) | −0,14 | −0,19 |
| Cassure | 0,5 ATR (39 pips) | 3 478 | 48 % | −0,00 | **−0,05** (±0,01) | −0,06 | −0,12 |
| Faux dépassement | 0,25 ATR | 1 611 | 50 % | +0,02 | **−0,08** (±0,02) | −0,12 | −0,11 |
| Faux dépassement | 0,5 ATR | 1 611 | 49 % | +0,02 | **−0,03** (±0,02) | −0,05 | −0,05 |

- **Aucune version n'est rentable**, avec un objectif de 1 R comme de 2 ou 3 R, en sortant le soir comme le lendemain, et chaque année (2024, 2025, 2026) est négative.
- **Avant spread, c'est un pile ou face** (−0,04 à +0,02 R, 48 à 50 % de gagnants à 1 R). **Le spread coûte 0,10 R par trade avec un stop de 20 pips**, et 0,05 R avec 39 pips : avec des stops courts et des objectifs de 1 R, il suffit à rendre la stratégie perdante.
- **Le filtre de tendance n'apporte presque rien** : les cassures dans le sens des 5 derniers jours font à peine mieux que toutes les cassures (−0,13 contre −0,14 R). Ce qui est sûr, c'est qu'**aller contre la tendance est pire** (−0,19 R).
- **Le « faux dépassement » fait un peu mieux que la cassure**, mais reste négatif. La seule case positive (faux dépassement, tendance ≥ 2 ATR, stop 0,5 ATR : +0,03 R sur 395 trades, ±0,05) est dans le bruit.
- **Par paire**, seules EURJPY (+0,07), EURUSD (+0,04) et GBPAUD (+0,01) sont légèrement positives sur la version cassure ; ce sont des paires à faible spread, et 22 essais en donnent toujours quelques-uns au-dessus de zéro.

## Ce qu'il faut retenir

1. **L'englobante sur un MLQ (achats) reste la seule piste positive**, depuis 2020 seulement. Avec un objectif de 2 R, elle fait mieux qu'avec 1 R.
2. **Votre suivi de tendance de juin, mis en règles, ne gagne pas** : c'est un pile ou face avant frais, et le spread le rend perdant, surtout avec des stops de 20 pips et des objectifs de 1 R. Vos bons départs de juin tiennent à la période (forte baisse de la livre et du dollar néo-zélandais), pas à un avantage de la méthode.
3. Si vous gardez cette approche : stops plus larges (au moins 0,5 ATR), paires à faible spread (EURUSD, USDJPY, EURJPY), et jamais à contre-tendance.
