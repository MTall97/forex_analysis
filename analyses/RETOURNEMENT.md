# La méthode de « retournement » d'Amirou, testée sur les cours

*14/10/2026 — script : [`scripts/tester_retournement.py`](../scripts/tester_retournement.py) ; trades : `data/retournement/{journalier,h4}.csv.gz` ; résultats : `data/retournement/resultats.csv`.*

## Ce qu'il enseigne dans le canal
- **Attendre une bougie de retournement** : « attendez la formation d'un candle de retournement de situation telle qu'un engulfing candle ou un inside bar candle inverse avant de prendre position » (#1187) ; « ne prenez jamais position sans la confirmation d'une bougie de retournement de situation » (#1366). Il le répète des dizaines de fois en 2019-2020 (#693, #1034, #1301, #1386).
- **Entrer sur une zone** : zone de retournement, de liquidité, de support ou de résistance (#939, #1144, #1173).
- **Après un « mouvement climatique »** : « en général on s'attend à un renversement de tendance après des mouvements comme ça » (#15227, 17/08/2026).

C'était son style principal en 2021-2022 : des retournements avec des stops serrés (voir `analyses/TRADES_PAR_EPOQUE.md`).

## Règles testées, fixées avant le test
Les règles sont données pour un achat ; la vente est symétrique.

| Élément | Règle |
|---|---|
| Bougie de retournement | **englobante** (haussière, la précédente baissière, corps au moins aussi grand) ou **pin bar** (mèche basse d'au moins 2/3 de la bougie, clôture dans le tiers haut) |
| Zone | le plus bas de la bougie touche, à 0,25 ATR près, le plus bas des 60 bougies précédentes (hors les 5 dernières) : un support déjà testé |
| Mouvement climatique | le prix a baissé d'au moins 3 ATR en 5 bougies |
| Entrée, stop, objectif | entrée à la clôture de la bougie ; stop 2 pips sous son plus bas ; objectif 2 R ou 3 R ; sortie après 5 jours (journalier) ou 30 bougies de 4 h |
| Conventions | stop prioritaire dans une même bougie ; spread déduit |
| Témoins | la bougie de retournement **n'importe où** ; la zone **sans** bougie de retournement |

Deux rejeux :
- **journalier** : Dukascopy, 10 paires, 2012-2026 ;
- **4 h** : bougies reconstruites depuis l'horaire Yahoo, 22 paires, 2024-2026.

## Résultats (objectif 2 R ; R moyen par trade ± erreur type)

| Groupe | Journalier 2012-2019 | Journalier 2020-2026 | 4 h 2024-2026 |
|---|---|---|---|
| **Zone + bougie de retournement** | −0,09 ± 0,07 (281 trades, 38 %) | −0,12 ± 0,07 (276, 35 %) | −0,14 ± 0,03 (1 633, 32 %) |
| Zone + englobante | −0,07 ± 0,08 | −0,17 ± 0,08 | −0,10 ± 0,04 |
| Zone + pin bar | −0,12 ± 0,14 | +0,02 ± 0,16 | −0,25 ± 0,06 |
| **Mouvement climatique + bougie** | −0,08 ± 0,05 (521) | +0,07 ± 0,06 (427, 47 %) | −0,10 ± 0,03 (2 478) |
| Climatique + zone + bougie | −0,52 ± 0,15 (39) | −0,10 ± 0,23 (24) | −0,22 ± 0,11 (150) |
| *Témoin : bougie de retournement n'importe où* | −0,03 ± 0,02 | +0,01 ± 0,02 | −0,13 ± 0,01 |
| *Témoin : zone sans bougie* | −0,19 ± 0,03 | −0,20 ± 0,03 | −0,22 ± 0,02 |

Avec un objectif de 3 R, les conclusions sont les mêmes (détail dans `resultats.csv`).

## Ce qu'il faut en retenir
- **La méthode ne bat pas le hasard.** Une bougie de retournement sur un support fait aussi mal, voire un peu plus mal, que la même bougie prise n'importe où. La zone n'apporte rien.
- **Acheter sur un support sans attendre de bougie perd nettement** (−0,2 R par trade). Sur ce point, son conseil est juste : attendre la bougie évite cette perte. Mais il ramène seulement le résultat au niveau du hasard, pas au-dessus.
- **Le « mouvement climatique » n'est positif que sur une période** : +0,07 R en journalier 2020-2026, mais négatif en 2012-2019 et en 4 h. Ce n'est pas un effet stable.
- **Moins de 40 % de gagnants à 2 R**, alors qu'il faudrait environ 34 % rien que pour couvrir les frais. Le résultat net est proche de zéro ou négatif.
- Ces résultats rejoignent ceux de ses trades de 2021-2022 : une méthode de retournement qui n'était rentable que par une poignée de gains à 1:10 et plus, impossibles à reproduire par une règle.

## Limites
- La « zone » est définie mécaniquement (un plus bas déjà testé). Amirou trace ses zones à la main, avec des Fibonacci, des canaux et des « zones de liquidité », et la règle peut ne pas les capter.
- L'inside bar inverse n'est pas testé seul.
- Il entrait souvent en 15 min ou en 1 h après la bougie de retournement, ce qui n'est pas reproduit ici.
