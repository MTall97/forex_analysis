# Les trades simulés pour tester la masterclass, avec leurs dates (focus 2020-2026)

*Rédigé le 06/10/2026. Scripts : [`scripts/trades_masterclass_par_date.py`](../scripts/trades_masterclass_par_date.py) et [`scripts/tester_englobante_mlq_recent.py`](../scripts/tester_englobante_mlq_recent.py). Données : [`data/masterclass_2020_2026/`](../data/masterclass_2020_2026/).*

## Ce qu'on trouve ici

Pour vérifier chaque règle de la masterclass, **on n'a pas repris les trades d'Amirou**. On a cherché, sur les cours réels, **tous les jours où la règle donnait un signal**, puis on a simulé le trade que la règle prescrit :

- entrée, stop et objectif fixés par la règle ;
- issue lue sur les bougies Dukascopy (journalières, ou horaires pour la Bombe et le bébé abandonné horaire) ;
- spread déduit ;
- si le stop et l'objectif sont touchés le même jour, on compte le stop.

Chaque ligne des fichiers ci-dessous est donc **un trade simulé, daté au jour du signal**. Le résultat est exprimé en R (1 R = le risque, la distance entre l'entrée et le stop).

- **Période complète** : 2012 à septembre 2026, sur 11 instruments (AUDJPY, AUDUSD, EURJPY, EURNZD, EURUSD, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDJPY, XAUUSD).
- **Focus 2020-2026** : demandé parce que l'économie mondiale a changé de régime à partir de 2020 (Covid, inflation, hausses de taux de 2022, guerre en Ukraine, élection américaine de 2024).
- La période 2012-2019 sert de **comparaison** : une règle valable devrait marcher dans les deux périodes, ou au moins dans la période récente avec une raison claire.

| Fichier (un trade par ligne, 2020-2026) | Règle |
|---|---|
| [`t2_trois_barres.csv`](../data/masterclass_2020_2026/t2_trois_barres.csv) | T2 lundi-mardi-mercredi « trois barres » |
| [`t3_lundi_mardi_haussiers.csv`](../data/masterclass_2020_2026/t3_lundi_mardi_haussiers.csv) | T3 lundi et mardi haussiers, mercredi prend le high (#14577) |
| [`t5_mlq.csv`](../data/masterclass_2020_2026/t5_mlq.csv) | T5 MLQ ±25 pips, stop 50, objectif 250 |
| [`bebe_abandonne_journalier.csv`](../data/masterclass_2020_2026/bebe_abandonne_journalier.csv), [`bebe_abandonne_horaire.csv`](../data/masterclass_2020_2026/bebe_abandonne_horaire.csv) | Bébé abandonné (définition corrigée) |
| [`bombe_h1.csv`](../data/masterclass_2020_2026/bombe_h1.csv) | Bombe (H1) |
| [`englobante_mercredi.csv`](../data/masterclass_2020_2026/englobante_mercredi.csv), [`englobante_mlq.csv`](../data/masterclass_2020_2026/englobante_mlq.csv), [`trois_barres_mlq.csv`](../data/masterclass_2020_2026/trois_barres_mlq.csv) | Combinaisons de briques (section 6 de `MASTERCLASS_VERIFIEE.md`) |
| [`flashcards_englobante.csv`](../data/masterclass_2020_2026/flashcards_englobante.csv) | Englobante « Naruto » des flashcards |

Les fichiers s'ouvrent dans Excel ou LibreOffice. Les colonnes sont : date, paire, sens, niveaux (entrée, stop, objectif quand la règle en fixe), issue et `r`.

## 1. Résultat par règle : 2012-2019 contre 2020-2026

| Règle | Période | 1er trade | Dernier trade | Trades | Gagnants | R moyen | R cumulé | t |
|---|---|---|---|---|---|---|---|---|
| T2 Lundi-mardi-mercredi « trois barres » | 2012-2019 | 2012-01-11 | 2019-10-30 | 158 | 31,0 % | -0,14 | -21,8 | -1,13 |
| T2 Lundi-mardi-mercredi « trois barres » | 2020-2026 | 2020-02-05 | 2026-08-26 | 153 | 36,6 % | +0,05 | +7,8 | +0,40 |
| T3 Lundi et mardi haussiers, mercredi prend le high | 2012-2019 | 2012-01-04 | 2019-12-11 | 847 | 22,8 % | -0,20 | -174,0 | -3,65 |
| T3 Lundi et mardi haussiers, mercredi prend le high | 2020-2026 | 2020-01-08 | 2026-09-30 | 870 | 23,2 % | -0,19 | -162,6 | -3,33 |
| T5 MLQ ±25 / stop 50 / objectif 250 pips | 2012-2019 | 2012-01-11 | 2019-12-31 | 3343 | 15,7 % | -0,11 | -380,7 | -3,07 |
| T5 MLQ ±25 / stop 50 / objectif 250 pips | 2020-2026 | 2020-01-02 | 2026-09-30 | 2712 | 17,1 % | -0,03 | -71,1 | -0,61 |
| Bébé abandonné (journalier) | 2012-2019 | 2012-01-18 | 2019-12-31 | 293 | 47,8 % | -0,06 | -17,1 | -1,09 |
| Bébé abandonné (journalier) | 2020-2026 | 2020-01-02 | 2026-09-10 | 234 | 48,7 % | -0,01 | -3,6 | -0,26 |
| Bébé abandonné (horaire) | 2020-2026 | 2023-12-15 | 2026-09-30 | 2578 | 47,8 % | -0,17 | -426,8 | -8,46 |
| Bombe (H1) | 2020-2026 | 2024-01-02 | 2026-09-14 | 46 | 34,8 % | +0,11 | +5,1 | +0,46 |
| Englobante du mercredi (objectif 2 R) | 2012-2019 | 2012-01-04 | 2019-12-25 | 1235 | 45,6 % | +0,03 | +31,6 | +0,87 |
| Englobante du mercredi (objectif 2 R) | 2020-2026 | 2020-01-01 | 2026-09-23 | 974 | 44,6 % | -0,00 | -1,7 | -0,05 |
| Englobante + MLQ (objectif 2 R) | 2012-2019 | 2012-01-04 | 2019-12-31 | 1096 | 41,2 % | -0,06 | -61,2 | -1,75 |
| Englobante + MLQ (objectif 2 R) | 2020-2026 | 2020-01-02 | 2026-09-25 | 876 | 46,6 % | +0,08 | +70,0 | +2,13 |
| Trois barres + MLQ (sortie au 3e jour) | 2012-2019 | 2012-03-27 | 2019-12-31 | 119 | 45,4 % | +0,39 | +46,6 | +1,78 |
| Trois barres + MLQ (sortie au 3e jour) | 2020-2026 | 2020-01-14 | 2026-08-04 | 101 | 44,6 % | +0,17 | +17,0 | +1,06 |
| Englobante « Naruto » (rupture des flashcards) | 2020-2026 | 2024-01-05 | 2026-09-28 | 1763 | 75,2 % | -0,02 | -33,2 | -1,29 |


**Lecture** :
- **t** mesure si le R moyen se distingue de zéro. Entre −2 et +2, le résultat peut être dû au hasard.
- **Gagnants** : part des trades avec R > 0. Pour une règle à objectif lointain (MLQ 1:5), un faible taux peut suffire ; c'est le R moyen qui tranche.
- Le bébé abandonné horaire, la Bombe et les flashcards ne sont testés que depuis fin 2023 ou 2024 : ce sont les seules années où l'horaire Yahoo est disponible.

## 2. Année par année, 2020-2026

**R moyen par année**

| Règle | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| Bombe (H1) | — | — | — | — | +0,86 | -0,14 | -0,22 |
| Bébé abandonné (horaire) | — | — | — | -0,25 | -0,15 | -0,12 | -0,23 |
| Bébé abandonné (journalier) | +0,06 | -0,14 | +0,09 | -0,00 | +0,15 | -0,10 | -0,18 |
| Englobante + MLQ (objectif 2 R) | +0,17 | -0,10 | +0,18 | -0,17 | +0,06 | +0,26 | +0,20 |
| Englobante du mercredi (objectif 2 R) | -0,12 | -0,01 | -0,03 | -0,11 | +0,03 | +0,15 | +0,08 |
| Englobante « Naruto » (rupture des flashcards) | — | — | — | — | -0,04 | -0,03 | +0,02 |
| T2 Lundi-mardi-mercredi « trois barres » | +0,07 | -0,08 | -0,29 | +0,24 | -0,22 | +0,32 | +0,40 |
| T3 Lundi et mardi haussiers, mercredi prend le high | +0,06 | -0,08 | -0,33 | -0,33 | -0,32 | -0,25 | -0,00 |
| T5 MLQ ±25 / stop 50 / objectif 250 pips | +0,03 | +0,17 | -0,22 | +0,05 | -0,12 | -0,04 | +0,05 |
| Trois barres + MLQ (sortie au 3e jour) | -0,06 | +0,01 | +0,20 | +0,39 | +0,16 | -0,15 | +0,98 |

**trades par année**

| Règle | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| Bombe (H1) | 0 | 0 | 0 | 0 | 13 | 14 | 19 |
| Bébé abandonné (horaire) | 0 | 0 | 0 | 35 | 946 | 887 | 710 |
| Bébé abandonné (journalier) | 27 | 44 | 32 | 29 | 40 | 38 | 24 |
| Englobante + MLQ (objectif 2 R) | 126 | 146 | 116 | 125 | 126 | 143 | 94 |
| Englobante du mercredi (objectif 2 R) | 119 | 157 | 153 | 136 | 162 | 145 | 102 |
| Englobante « Naruto » (rupture des flashcards) | 0 | 0 | 0 | 0 | 612 | 671 | 480 |
| T2 Lundi-mardi-mercredi « trois barres » | 21 | 19 | 25 | 18 | 24 | 34 | 12 |
| T3 Lundi et mardi haussiers, mercredi prend le high | 137 | 119 | 112 | 145 | 131 | 136 | 90 |
| T5 MLQ ±25 / stop 50 / objectif 250 pips | 412 | 326 | 516 | 423 | 360 | 410 | 265 |
| Trois barres + MLQ (sortie au 3e jour) | 16 | 18 | 18 | 7 | 21 | 11 | 10 |

**gagnants % par année**

| Règle | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| Bombe (H1) | — | — | — | — | 54 | 21 | 32 |
| Bébé abandonné (horaire) | — | — | — | 43 | 49 | 49 | 44 |
| Bébé abandonné (journalier) | 48 | 43 | 53 | 55 | 58 | 42 | 42 |
| Englobante + MLQ (objectif 2 R) | 46 | 40 | 55 | 39 | 43 | 51 | 54 |
| Englobante du mercredi (objectif 2 R) | 42 | 41 | 47 | 40 | 44 | 50 | 48 |
| Englobante « Naruto » (rupture des flashcards) | — | — | — | — | 74 | 74 | 78 |
| T2 Lundi-mardi-mercredi « trois barres » | 52 | 32 | 20 | 39 | 38 | 32 | 58 |
| T3 Lundi et mardi haussiers, mercredi prend le high | 30 | 25 | 19 | 19 | 20 | 23 | 28 |
| T5 MLQ ±25 / stop 50 / objectif 250 pips | 18 | 21 | 14 | 18 | 15 | 17 | 19 |
| Trois barres + MLQ (sortie au 3e jour) | 50 | 28 | 50 | 43 | 38 | 46 | 70 |


## 3. Ce que montre la période 2020-2026

1. **Aucune règle de la masterclass ne devient rentable de façon fiable après 2020.**
   - T3 (lundi et mardi haussiers) reste nettement perdant : −0,19 R par trade, t = −3,3, perdant chaque année de 2021 à 2025.
   - T5 MLQ (1:5) est moins mauvais qu'avant 2020 (−0,03 R contre −0,11 R), mais reste négatif. 2021 est la seule bonne année (+0,17 R) ; 2022 est la pire (−0,22 R).
   - T2 « trois barres » passe de −0,14 R à +0,05 R, mais sur 153 trades (t = 0,4) : c'est du bruit, avec de fortes variations d'une année à l'autre (−0,29 R en 2022, +0,40 R en 2026).
   - Bébé abandonné : environ 48 % de gagnants, comme le témoin. En horaire, −0,17 R par trade sur 2 578 trades.
   - Bombe : +0,86 R en 2024, puis négatif en 2025 et 2026, sur 13 à 19 trades par an.
2. **2022 est la pire année** pour presque toutes les règles (T2, T3, T5). C'est l'année des hausses de taux brutales de la Fed et de l'effondrement du yen : les marchés suivaient de longues tendances, et les règles de retournement ou de rejet de niveau ont échoué.
3. **Une seule piste ressort, mais elle ne vient pas de la masterclass telle quelle** (section 4).

## 4. La seule piste : achat sur englobante haussière qui rejette un MLQ (2020-2026)

C'est la combinaison « englobante + MLQ » de `MASTERCLASS_VERIFIEE.md` (section 6), limitée aux **achats**.

**Le signal** :
- la bougie journalière est haussière et englobe la bougie baissière de la veille ;
- son plus bas touche un niveau MLQ (multiple de 250 pips) à 25 pips près ;
- entrée à la clôture, stop sous le plus bas (+2 pips), objectif 2 R ou sortie à la clôture du 3e jour.

| Niveaux utilisés (achats, objectif 2 R) | 2012-2019 | 2020-2026 |
|---|---|---|
| **MLQ réels** | −0,02 R (540 trades) | **+0,20 R (420 trades, t = 3,5, 51 % de gagnants)** |
| Décalés de 50 pips | −0,04 R | −0,10 R |
| Décalés de 100 pips | +0,01 R | +0,07 R |
| Décalés de 125 pips | +0,03 R | −0,03 R |
| Décalés de 175 pips | −0,01 R | +0,04 R |
| Décalés de 200 pips | −0,02 R | −0,01 R |
| Toute englobante haussière (témoin) | −0,01 R | +0,05 R |

- **Sur 2020-2026, c'est solide** :
  - positif chaque année : 2020 +0,17 R ; 2021 +0,01 R ; 2022 +0,41 R ; 2023 +0,06 R ; 2024 +0,11 R ; 2025 +0,39 R ; 2026 +0,24 R ;
  - positif sur les 10 paires, de +0,11 R (USDJPY) à +0,41 R (AUDJPY) ;
  - nettement au-dessus des niveaux décalés et du témoin, donc le niveau MLQ semble compter.
- **Mais trois réserves empêchent de conclure** :
  - **rien avant 2020** : −0,02 R sur 2012-2019 ;
  - **trouvé après coup** : la séparation achats / ventes a été faite en regardant les résultats. Avec environ 70 variantes testées dans ce projet, il faut un t bien supérieur à 2 pour y croire. Ici t = 3,5, ce qui passe ce seuil de justesse ;
  - **les ventes ne marchent pas** (−0,03 R), alors que la règle d'Amirou est symétrique.
- **Explication possible** : depuis 2020, les replis sur des niveaux ronds ont souvent été rachetés (marchés portés par les liquidités, puis par la faiblesse du yen). Ce serait un effet du régime récent, pas une règle permanente.
- **Ce qu'il faut faire** : suivre ce signal **à partir d'octobre 2026, sans rien changer**, sur compte démo. Si, après 6 à 12 mois (environ 30 à 60 trades), il reste au-dessus de +0,1 R, la piste devient sérieuse. Le contrôle se relance avec `python scripts/tester_englobante_mlq_recent.py`.

## 5. Les règles qui ne sont pas des trades : T1 et T4, année par année

**T1 — Plus haut de la semaine formé mardi ou mercredi** (annoncé : 70 %), sur 11 instruments :

| Année | Semaines | Plus haut mardi ou mercredi | Plus haut lundi ou vendredi |
|---|---|---|---|
| 2020 | 572 | 28 % | 53 % |
| 2021 | 572 | 32 % | 49 % |
| 2022 | 572 | 29 % | 53 % |
| 2023 | 572 | 34 % | 51 % |
| 2024 | 582 | 27 % | 59 % |
| 2025 | 572 | 30 % | 51 % |
| 2026 (jusqu'en septembre) | 429 | 32 % | 54 % |

C'est 27 à 34 % chaque année, jamais 70 %. Les années 2012-2019 donnent les mêmes chiffres : le régime n'y change rien.

**T4 — AUDJPY en avril : plus bas du mois dans la 1re semaine** (annoncé : 75 %, #14662) :

| Année | Date du plus bas d'avril | 1re semaine ? | Variation d'avril |
|---|---|---|---|
| 2020 | 02/04/2020 | ✅ | +5,6 % |
| 2021 | 13/04/2021 | ❌ | +0,2 % |
| 2022 | 26/04/2022 | ❌ | +0,5 % |
| 2023 | 06/04/2023 | ✅ | +1,1 % |
| 2024 | 19/04/2024 | ❌ | +3,7 % |
| 2025 | 09/04/2025 | ❌ | −2,0 % |
| 2026 | 02/04/2026 | ✅ | +3,0 % |

- 3 avrils sur 7 (43 %) entre 2020 et 2026 ; 50 % sur 2015-2024.
- Avril est en hausse 6 fois sur 7 depuis 2020 : la saisonnalité haussière d'avril tient mieux que la règle du plus bas.
- **EURJPY en juin** (#14907) : plus bas en 1re semaine en 2023 et 2025 seulement, soit 2 juins sur 7 depuis 2020. Le détail est dans [`t4_audjpy_avril_eurjpy_juin.csv`](../data/masterclass_2020_2026/t4_audjpy_avril_eurjpy_juin.csv).

## 6. Liste complète des trades 2020-2026 pour les petites règles

Pour les règles qui comptent des centaines ou des milliers de trades (T3, T5, englobantes, bébé abandonné), la liste est dans les fichiers CSV du tableau du début.

#### T2 « trois barres » (153 trades)

| date | paire | sens | entree | sl | tp | issue | r |
|---|---|---|---|---|---|---|---|
| 2020-02-05 | GBPUSD | achat | 1.303 | 1.2939 | 1.3184 | stop | -1,01 |
| 2020-04-08 | XAUUSD | vente | 1647.3 | 1668.8 | 1609 | stop | -1,01 |
| 2020-04-15 | EURJPY | achat | 117.65 | 117.28 | 118.71 | stop | -1,04 |
| 2020-05-13 | EURJPY | vente | 116.23 | 116.87 | 115.28 | sortie vendredi | +0,65 |
| 2020-05-13 | USDJPY | vente | 107.17 | 107.7 | 106.49 | sortie vendredi | +0,23 |
| 2020-06-17 | AUDUSD | vente | 0.68928 | 0.69782 | 0.67761 | sortie vendredi | +0,68 |
| 2020-06-17 | GBPJPY | vente | 135.12 | 136.37 | 133.5 | objectif | +1,29 |
| 2020-06-17 | AUDJPY | vente | 74.032 | 75.107 | 72.645 | sortie vendredi | +0,92 |
| 2020-06-24 | USDCAD | achat | 1.3541 | 1.3483 | 1.363 | objectif | +1,52 |
| 2020-06-24 | EURJPY | vente | 120.39 | 121.12 | 119.31 | sortie vendredi | +0,18 |
| 2020-06-24 | EURNZD | achat | 1.74 | 1.7356 | 1.7521 | objectif | +2,68 |
| 2020-06-24 | GBPJPY | vente | 133.29 | 134 | 131.66 | sortie vendredi | +1,43 |
| 2020-06-24 | AUDJPY | vente | 73.89 | 74.441 | 72.714 | sortie vendredi | +0,50 |
| 2020-07-29 | EURUSD | vente | 1.1719 | 1.1776 | 1.1641 | stop | -1,01 |
| 2020-07-29 | XAUUSD | vente | 1956 | 1981.2 | 1899.6 | stop | -1,01 |
| 2020-07-29 | AUDUSD | vente | 0.71578 | 0.71785 | 0.70864 | stop | -1,05 |
| 2020-09-02 | USDJPY | vente | 105.9 | 106.17 | 105.29 | stop | -1,04 |
| 2020-09-23 | USDCAD | vente | 1.3297 | 1.3348 | 1.3171 | stop | -1,03 |
| 2020-10-28 | USDCAD | vente | 1.3192 | 1.3211 | 1.3124 | stop | -1,08 |
| 2020-11-11 | XAUUSD | achat | 1876.5 | 1867.1 | 1965.4 | stop | -1,03 |
| 2020-11-25 | USDJPY | vente | 104.51 | 104.78 | 103.68 | sortie vendredi | +1,73 |
| 2021-02-24 | XAUUSD | vente | 1805.7 | 1816.1 | 1780.5 | objectif | +2,40 |
| 2021-03-03 | EURNZD | achat | 1.6571 | 1.6526 | 1.6685 | objectif | +2,49 |
| 2021-04-21 | EURUSD | vente | 1.2032 | 1.2082 | 1.1942 | stop | -1,02 |
| 2021-04-21 | GBPUSD | vente | 1.3938 | 1.4011 | 1.3809 | sortie vendredi | +0,85 |
| 2021-04-21 | USDJPY | achat | 108.13 | 107.95 | 108.83 | stop | -1,05 |
| 2021-04-28 | USDCAD | achat | 1.2407 | 1.2386 | 1.249 | stop | -1,07 |
| 2021-05-05 | GBPUSD | vente | 1.3887 | 1.3907 | 1.3801 | stop | -1,06 |
| 2021-05-12 | GBPJPY | vente | 153.67 | 153.98 | 151.93 | stop | -1,08 |
| 2021-06-16 | GBPJPY | vente | 155 | 155.5 | 154.32 | objectif | +1,30 |
| 2021-07-21 | AUDUSD | achat | 0.73381 | 0.72973 | 0.74082 | stop | -1,02 |
| 2021-07-21 | EURNZD | vente | 1.7017 | 1.7099 | 1.6851 | objectif | +1,99 |
| 2021-08-25 | XAUUSD | vente | 1801.7 | 1809.7 | 1776.4 | stop | -1,04 |
| 2021-10-13 | EURJPY | vente | 130.91 | 131.29 | 129.74 | stop | -1,04 |
| 2021-10-13 | AUDJPY | vente | 83.26 | 83.82 | 81.853 | stop | -1,03 |
| 2021-11-10 | GBPUSD | vente | 1.3559 | 1.3609 | 1.345 | objectif | +2,18 |
| 2021-11-24 | NZDUSD | achat | 0.69513 | 0.69134 | 0.70133 | stop | -1,04 |
| 2021-12-08 | GBPJPY | vente | 150.37 | 151.15 | 149.18 | sortie vendredi | -0,13 |
| 2021-12-29 | EURJPY | vente | 129.88 | 130.24 | 129.21 | stop | -1,04 |
| 2021-12-29 | GBPJPY | vente | 154.19 | 154.6 | 152.93 | stop | -1,06 |
| 2022-01-05 | USDCAD | vente | 1.2705 | 1.2768 | 1.2624 | stop | -1,02 |
| 2022-03-02 | AUDJPY | vente | 83.383 | 83.879 | 82.458 | stop | -1,04 |
| 2022-04-13 | USDCAD | vente | 1.2635 | 1.2663 | 1.2561 | stop (même jour que l'objectif) | -1,05 |
| 2022-04-13 | USDJPY | vente | 125.43 | 125.78 | 124.01 | stop | -1,03 |
| 2022-04-13 | GBPJPY | vente | 163.07 | 163.64 | 161.52 | stop | -1,04 |
| 2022-04-27 | XAUUSD | achat | 1906.5 | 1895.4 | 1934.3 | stop | -1,03 |
| 2022-05-04 | XAUUSD | achat | 1868.3 | 1850.1 | 1899.8 | objectif | +1,72 |
| 2022-05-25 | EURJPY | vente | 136.02 | 136.81 | 134.66 | sortie vendredi | -0,51 |
| 2022-06-15 | EURUSD | achat | 1.0437 | 1.0395 | 1.052 | stop | -1,02 |
| 2022-07-13 | AUDUSD | achat | 0.67453 | 0.67084 | 0.6854 | stop | -1,03 |
| 2022-08-10 | AUDUSD | vente | 0.69537 | 0.69962 | 0.68913 | stop | -1,02 |
| 2022-08-10 | AUDJPY | vente | 94.021 | 94.408 | 93.096 | stop | -1,05 |
| 2022-08-10 | USDCAD | achat | 1.2885 | 1.2841 | 1.295 | stop | -1,03 |
| 2022-08-17 | AUDUSD | achat | 0.70189 | 0.69885 | 0.71246 | stop | -1,03 |
| 2022-08-17 | EURUSD | achat | 1.0169 | 1.012 | 1.0268 | stop | -1,02 |
| 2022-10-19 | USDCAD | achat | 1.3726 | 1.3655 | 1.3878 | stop | -1,02 |
| 2022-10-19 | NZDUSD | vente | 0.5655 | 0.57209 | 0.55504 | stop | -1,02 |
| 2022-10-19 | AUDJPY | vente | 93.665 | 94.429 | 92.085 | stop | -1,02 |
| 2022-11-02 | GBPUSD | achat | 1.1488 | 1.1435 | 1.1613 | stop | -1,02 |
| 2022-11-09 | EURJPY | vente | 146.46 | 147.01 | 145.39 | stop | -1,03 |
| 2022-11-09 | GBPJPY | vente | 167.82 | 169.08 | 165.81 | objectif | +1,58 |
| 2022-11-30 | AUDJPY | achat | 92.729 | 92.162 | 93.701 | objectif | +1,68 |
| 2022-11-30 | XAUUSD | achat | 1748.7 | 1739.9 | 1763.6 | objectif | +1,65 |
| 2022-12-07 | XAUUSD | achat | 1770.8 | 1766.9 | 1809.8 | sortie vendredi | +6,26 |
| 2022-12-07 | EURJPY | vente | 143.28 | 144.02 | 141.49 | stop | -1,02 |
| 2023-01-11 | GBPUSD | vente | 1.2153 | 1.22 | 1.2079 | stop | -1,03 |
| 2023-01-25 | USDJPY | vente | 130.21 | 131.14 | 129.04 | objectif | +1,25 |
| 2023-01-25 | EURJPY | vente | 141.79 | 142.22 | 140.46 | stop | -1,04 |
| 2023-01-25 | AUDJPY | vente | 91.767 | 91.945 | 90.102 | stop | -1,10 |
| 2023-03-08 | EURJPY | vente | 144.92 | 145.46 | 144.11 | objectif | +1,46 |
| 2023-03-15 | XAUUSD | vente | 1903 | 1914.2 | 1871.3 | stop | -1,03 |
| 2023-04-05 | AUDUSD | vente | 0.67594 | 0.67948 | 0.66506 | objectif | +3,05 |
| 2023-05-17 | AUDJPY | vente | 90.826 | 91.278 | 90.094 | stop | -1,04 |
| 2023-05-17 | EURNZD | achat | 1.7421 | 1.7387 | 1.7533 | stop | -1,09 |
| 2023-05-17 | GBPJPY | vente | 170.31 | 170.85 | 168.76 | stop | -1,05 |
| 2023-08-23 | AUDJPY | vente | 93.647 | 94.077 | 92.83 | stop | -1,04 |
| 2023-09-20 | XAUUSD | vente | 1931.3 | 1937.5 | 1922.4 | stop | -1,05 |
| 2023-10-11 | EURNZD | achat | 1.7552 | 1.7504 | 1.7705 | objectif | +3,12 |
| 2023-10-11 | USDJPY | achat | 148.63 | 148.14 | 149.24 | objectif | +1,24 |
| 2023-10-11 | XAUUSD | vente | 1859.5 | 1865.5 | 1844.1 | stop | -1,05 |
| 2023-10-11 | USDCAD | achat | 1.3584 | 1.3567 | 1.3679 | objectif | +5,49 |
| 2023-10-18 | GBPJPY | vente | 182.38 | 182.82 | 181.14 | sortie vendredi | +0,32 |
| 2023-12-13 | EURJPY | vente | 156.89 | 157.31 | 155.83 | stop (même jour que l'objectif) | -1,04 |
| 2024-01-31 | EURNZD | achat | 1.7681 | 1.7596 | 1.7814 | sortie vendredi | +1,10 |
| 2024-02-28 | EURNZD | vente | 1.7571 | 1.7636 | 1.7447 | stop | -1,05 |
| 2024-03-06 | GBPJPY | vente | 190.62 | 191.05 | 189.7 | objectif | +2,07 |
| 2024-04-03 | GBPJPY | achat | 190.57 | 190.01 | 191.35 | objectif | +1,33 |
| 2024-04-03 | GBPUSD | achat | 1.2576 | 1.2537 | 1.2642 | objectif | +1,68 |
| 2024-04-10 | EURJPY | vente | 164.81 | 165.19 | 164.19 | objectif | +1,59 |
| 2024-04-24 | EURNZD | achat | 1.8032 | 1.7978 | 1.81 | stop | -1,06 |
| 2024-05-08 | GBPJPY | vente | 193.48 | 194.15 | 191.59 | stop | -1,04 |
| 2024-05-08 | AUDJPY | vente | 101.97 | 102.49 | 100.93 | stop | -1,03 |
| 2024-05-22 | USDJPY | vente | 156.27 | 156.56 | 155.49 | stop | -1,03 |
| 2024-05-22 | GBPJPY | vente | 198.61 | 198.92 | 197.29 | stop | -1,08 |
| 2024-05-22 | EURJPY | vente | 169.62 | 169.96 | 168.94 | stop | -1,04 |
| 2024-06-05 | GBPUSD | vente | 1.2772 | 1.2819 | 1.2694 | sortie vendredi | +1,08 |
| 2024-06-26 | EURJPY | vente | 171.02 | 171.41 | 170.27 | stop | -1,04 |
| 2024-07-03 | USDJPY | vente | 161.49 | 161.76 | 160.68 | stop | -1,04 |
| 2024-07-10 | EURNZD | vente | 1.7649 | 1.7701 | 1.7578 | stop | -1,06 |
| 2024-08-14 | XAUUSD | vente | 2464 | 2477 | 2423.7 | stop | -1,02 |
| 2024-09-11 | GBPUSD | achat | 1.3079 | 1.3047 | 1.3143 | stop | -1,04 |
| 2024-10-11 | EURNZD | vente | 1.79 | 1.7972 | 1.7769 | sortie vendredi | +0,04 |
| 2024-11-27 | XAUUSD | achat | 2632.1 | 2608.3 | 2721.2 | sortie vendredi | +0,74 |
| 2024-11-27 | AUDUSD | achat | 0.64738 | 0.64314 | 0.65494 | sortie vendredi | +0,75 |
| 2024-12-11 | AUDJPY | vente | 96.802 | 97.485 | 95.617 | stop | -1,03 |
| 2024-12-18 | GBPJPY | vente | 195.18 | 195.91 | 193.58 | stop | -1,03 |
| 2024-12-25 | USDJPY | vente | 157.06 | 157.41 | 156.24 | stop | -1,03 |
| 2025-01-08 | EURJPY | vente | 163.62 | 164.56 | 161.85 | objectif | +1,87 |
| 2025-01-22 | AUDUSD | vente | 0.62614 | 0.62905 | 0.61893 | stop | -1,03 |
| 2025-01-22 | EURUSD | vente | 1.0406 | 1.0437 | 1.0266 | stop | -1,03 |
| 2025-01-22 | USDCAD | achat | 1.434 | 1.4287 | 1.4485 | sortie vendredi | -0,01 |
| 2025-01-22 | NZDUSD | vente | 0.56598 | 0.56907 | 0.55788 | stop | -1,05 |
| 2025-01-29 | AUDJPY | achat | 97.246 | 96.819 | 98.248 | stop | -1,04 |
| 2025-01-29 | EURJPY | achat | 162.21 | 161.6 | 163.45 | stop | -1,02 |
| 2025-02-05 | EURJPY | vente | 159.85 | 160.72 | 157.97 | objectif | +2,16 |
| 2025-02-05 | GBPJPY | vente | 192.28 | 193.19 | 190.02 | objectif | +2,46 |
| 2025-02-05 | AUDJPY | vente | 96.318 | 96.772 | 94.617 | objectif | +3,71 |
| 2025-03-19 | AUDJPY | vente | 95.065 | 95.767 | 93.901 | objectif | +1,63 |
| 2025-03-19 | NZDUSD | vente | 0.58176 | 0.58328 | 0.57406 | objectif | +4,97 |
| 2025-03-19 | USDCAD | achat | 1.4299 | 1.4258 | 1.438 | objectif | +1,91 |
| 2025-03-19 | EURNZD | achat | 1.8799 | 1.8718 | 1.893 | stop | -1,04 |
| 2025-03-26 | GBPJPY | vente | 194.09 | 195.01 | 192.41 | stop | -1,03 |
| 2025-03-26 | AUDJPY | vente | 94.564 | 94.932 | 93.585 | stop | -1,05 |
| 2025-04-30 | USDJPY | achat | 142.26 | 141.95 | 143.89 | objectif | +5,22 |
| 2025-04-30 | GBPUSD | vente | 1.3412 | 1.3444 | 1.328 | objectif | +4,05 |
| 2025-05-14 | USDJPY | vente | 147.52 | 148.29 | 145.7 | objectif | +2,35 |
| 2025-06-04 | GBPUSD | vente | 1.353 | 1.3559 | 1.3451 | stop | -1,04 |
| 2025-06-04 | XAUUSD | vente | 3359.7 | 3388.6 | 3295.2 | stop | -1,01 |
| 2025-06-18 | AUDJPY | vente | 94.218 | 94.86 | 93.182 | sortie vendredi | -0,03 |
| 2025-06-18 | EURJPY | vente | 166.93 | 167.63 | 165.88 | stop | -1,02 |
| 2025-07-16 | EURNZD | vente | 1.9492 | 1.9543 | 1.9395 | stop | -1,06 |
| 2025-07-30 | USDJPY | vente | 148.42 | 148.83 | 147.52 | stop | -1,02 |
| 2025-08-13 | XAUUSD | achat | 3350.4 | 3330.7 | 3404.8 | stop | -1,02 |
| 2025-08-20 | USDJPY | vente | 147.74 | 148.13 | 147.08 | objectif | +1,65 |
| 2025-08-27 | USDJPY | vente | 147.47 | 147.93 | 146.76 | stop | -1,02 |
| 2025-08-27 | EURUSD | achat | 1.1637 | 1.16 | 1.1726 | stop | -1,02 |
| 2025-09-10 | XAUUSD | vente | 3633.4 | 3673.8 | 3577.7 | sortie vendredi | -0,24 |
| 2025-11-12 | AUDJPY | vente | 100.6 | 100.9 | 99.685 | stop | -1,06 |
| 2025-11-12 | GBPJPY | vente | 202.64 | 203.3 | 201.79 | stop | -1,04 |
| 2025-11-26 | XAUUSD | vente | 4133.5 | 4159.2 | 4039.9 | stop | -1,01 |
| 2025-11-26 | GBPJPY | vente | 205.52 | 206.01 | 204.62 | stop | -1,05 |
| 2026-01-07 | GBPJPY | vente | 211.51 | 212.17 | 210.5 | objectif | +1,47 |
| 2026-01-07 | GBPUSD | vente | 1.3501 | 1.357 | 1.3415 | objectif | +1,21 |
| 2026-02-11 | EURUSD | vente | 1.1892 | 1.1932 | 1.182 | sortie vendredi | +0,51 |
| 2026-03-11 | EURUSD | vente | 1.1614 | 1.1672 | 1.1511 | objectif | +1,77 |
| 2026-03-11 | GBPUSD | vente | 1.3419 | 1.3483 | 1.3285 | objectif | +2,08 |
| 2026-03-11 | NZDUSD | vente | 0.59252 | 0.59672 | 0.58524 | objectif | +1,70 |
| 2026-05-20 | GBPJPY | vente | 213.03 | 213.53 | 211.37 | stop | -1,05 |
| 2026-05-20 | GBPUSD | vente | 1.3397 | 1.3436 | 1.3304 | stop | -1,03 |
| 2026-07-08 | GBPJPY | vente | 216.68 | 217.23 | 215.57 | stop | -1,05 |
| 2026-07-29 | EURNZD | vente | 1.9693 | 1.9722 | 1.9629 | stop | -1,10 |
| 2026-07-29 | GBPJPY | achat | 217.71 | 217.49 | 218.52 | stop (même jour que l'objectif) | -1,12 |
| 2026-08-26 | XAUUSD | vente | 4712.1 | 4755.2 | 4651.8 | objectif | +1,39 |

#### Trois barres + MLQ (sortie au 3e jour) (101 trades)

| date | paire | sens | r |
|---|---|---|---|
| 2020-01-14 | USDJPY | vente | -1,03 |
| 2020-01-28 | AUDUSD | achat | -1,03 |
| 2020-04-14 | EURJPY | achat | -1,04 |
| 2020-05-12 | USDJPY | vente | +0,23 |
| 2020-06-16 | AUDJPY | vente | +0,92 |
| 2020-06-16 | AUDUSD | vente | +0,68 |
| 2020-06-23 | USDCAD | achat | +2,48 |
| 2020-07-07 | AUDUSD | vente | -1,02 |
| 2020-07-14 | USDJPY | vente | +1,05 |
| 2020-07-28 | EURUSD | vente | -1,01 |
| 2020-09-01 | USDCAD | achat | +0,07 |
| 2020-09-01 | EURNZD | vente | +0,07 |
| 2020-10-06 | GBPJPY | vente | -1,02 |
| 2020-10-06 | GBPUSD | vente | -1,01 |
| 2020-10-06 | USDCAD | achat | -1,02 |
| 2020-11-24 | USDJPY | vente | +1,73 |
| 2021-03-23 | AUDUSD | vente | -0,22 |
| 2021-03-23 | EURJPY | vente | -0,56 |
| 2021-04-20 | GBPUSD | vente | +0,85 |
| 2021-04-20 | NZDUSD | vente | -0,46 |
| 2021-04-27 | NZDUSD | vente | -1,04 |
| 2021-05-04 | AUDUSD | vente | -1,02 |
| 2021-05-18 | USDCAD | achat | -0,20 |
| 2021-06-01 | EURUSD | vente | +1,35 |
| 2021-06-01 | GBPUSD | vente | -0,01 |
| 2021-06-15 | AUDJPY | vente | +6,47 |
| 2021-07-20 | AUDJPY | achat | +0,83 |
| 2021-09-28 | GBPJPY | vente | +0,37 |
| 2021-11-02 | EURJPY | vente | -1,04 |
| 2021-11-23 | USDCAD | vente | -1,02 |
| 2021-11-23 | EURUSD | achat | -1,04 |
| 2021-11-23 | EURNZD | vente | -1,03 |
| 2021-12-28 | USDJPY | vente | -1,05 |
| 2021-12-28 | EURJPY | vente | -1,04 |
| 2022-01-04 | USDCAD | vente | -1,02 |
| 2022-01-18 | USDJPY | vente | +1,71 |
| 2022-03-15 | NZDUSD | achat | +4,29 |
| 2022-05-31 | EURUSD | vente | +0,38 |
| 2022-07-05 | EURJPY | vente | +0,13 |
| 2022-07-12 | USDJPY | vente | -1,01 |
| 2022-08-09 | AUDUSD | vente | -1,02 |
| 2022-08-16 | EURJPY | achat | +0,54 |
| 2022-08-16 | GBPJPY | achat | -0,22 |
| 2022-08-16 | AUDUSD | achat | -1,03 |
| 2022-08-16 | GBPUSD | achat | -1,01 |
| 2022-08-23 | USDJPY | vente | -1,01 |
| 2022-08-30 | GBPJPY | vente | +0,43 |
| 2022-09-13 | GBPJPY | vente | +2,01 |
| 2022-09-13 | EURNZD | achat | +0,54 |
| 2022-11-22 | EURUSD | achat | +1,15 |
| 2022-12-06 | GBPJPY | vente | -1,02 |
| 2022-12-20 | USDJPY | vente | -0,18 |
| 2023-04-25 | GBPUSD | vente | -1,01 |
| 2023-05-02 | AUDJPY | vente | +0,02 |
| 2023-05-16 | NZDUSD | vente | -1,06 |
| 2023-05-23 | EURJPY | vente | -1,02 |
| 2023-10-10 | EURNZD | achat | +6,27 |
| 2023-10-24 | EURJPY | vente | +0,59 |
| 2023-12-12 | EURJPY | vente | -1,04 |
| 2024-01-23 | USDCAD | vente | -1,04 |
| 2024-02-27 | AUDUSD | achat | -1,05 |
| 2024-04-02 | GBPJPY | achat | +1,73 |
| 2024-04-09 | EURJPY | vente | +4,47 |
| 2024-04-23 | EURNZD | achat | -1,06 |
| 2024-05-07 | AUDJPY | vente | -1,03 |
| 2024-05-21 | EURJPY | vente | -1,04 |
| 2024-06-18 | EURUSD | vente | +1,85 |
| 2024-06-25 | EURUSD | vente | -0,10 |
| 2024-07-02 | EURNZD | vente | +0,45 |
| 2024-07-02 | USDCAD | vente | +0,44 |
| 2024-09-03 | AUDJPY | vente | +1,17 |
| 2024-09-17 | GBPUSD | vente | -1,02 |
| 2024-10-01 | AUDJPY | vente | -1,01 |
| 2024-10-22 | NZDUSD | achat | -1,06 |
| 2024-11-05 | EURNZD | vente | +3,46 |
| 2024-11-26 | GBPUSD | achat | +2,20 |
| 2024-12-10 | AUDJPY | vente | -1,03 |
| 2024-12-17 | EURJPY | vente | -1,01 |
| 2024-12-24 | USDJPY | vente | -1,03 |
| 2024-12-24 | GBPJPY | vente | -1,02 |
| 2025-01-21 | USDJPY | achat | +0,17 |
| 2025-03-18 | USDCAD | achat | +1,12 |
| 2025-03-25 | GBPJPY | vente | -1,03 |
| 2025-03-25 | AUDJPY | vente | -1,05 |
| 2025-04-22 | USDJPY | achat | +0,32 |
| 2025-06-03 | AUDUSD | vente | -1,03 |
| 2025-06-03 | USDJPY | achat | +0,70 |
| 2025-06-17 | EURJPY | vente | -1,02 |
| 2025-06-17 | AUDJPY | vente | -0,03 |
| 2025-10-14 | USDJPY | vente | +1,19 |
| 2025-10-21 | AUDUSD | vente | -1,03 |
| 2026-01-13 | GBPUSD | vente | +0,67 |
| 2026-03-10 | GBPUSD | vente | +3,04 |
| 2026-04-21 | EURJPY | vente | +1,58 |
| 2026-05-05 | GBPUSD | achat | +1,13 |
| 2026-05-19 | EURJPY | vente | -0,19 |
| 2026-07-14 | USDJPY | vente | -1,03 |
| 2026-07-28 | NZDUSD | achat | +4,50 |
| 2026-07-28 | GBPJPY | achat | -1,12 |
| 2026-08-04 | AUDUSD | achat | +0,40 |
| 2026-08-04 | EURUSD | achat | +0,83 |

#### Bombe (H1) (46 trades)

| date | paire | sens | entree | sl | sortie | r |
|---|---|---|---|---|---|---|
| 2024-01-02 05:00 | EURGBP | vente | 0.86618 | 0.8703 | 0.86805 | -0,48 |
| 2024-03-20 08:00 | EURUSD | vente | 1.0855 | 1.0877 | 1.0877 | -1,04 |
| 2024-04-12 03:00 | AUDUSD | vente | 0.6529 | 0.65559 | 0.64224 | +3,92 |
| 2024-04-23 05:00 | GBPUSD | vente | 1.2344 | 1.2364 | 1.2364 | -1,06 |
| 2024-05-16 07:00 | EURGBP | vente | 0.85759 | 0.85939 | 0.8562 | +0,71 |
| 2024-06-12 05:00 | NZDUSD | achat | 0.61508 | 0.61352 | 0.61762 | +1,53 |
| 2024-07-22 15:00 | GBPUSD | vente | 1.2909 | 1.2945 | 1.2913 | -0,15 |
| 2024-07-23 00:00 | EURJPY | vente | 170.59 | 171.17 | 165.82 | +8,26 |
| 2024-09-04 23:00 | NZDUSD | vente | 0.61874 | 0.62186 | 0.62116 | -0,83 |
| 2024-10-11 15:00 | NZDUSD | achat | 0.61117 | 0.60844 | 0.60878 | -0,93 |
| 2024-10-18 02:00 | GBPUSD | achat | 1.3023 | 1.2981 | 1.3033 | +0,22 |
| 2024-10-22 09:00 | EURUSD | vente | 1.0819 | 1.0842 | 1.0809 | +0,38 |
| 2024-11-11 00:00 | EURAUD | vente | 1.6261 | 1.6307 | 1.6227 | +0,71 |
| 2025-01-28 09:00 | USDJPY | vente | 155.44 | 156 | 155.75 | -0,57 |
| 2025-03-27 06:00 | AUDJPY | achat | 94.972 | 94.394 | 94.823 | -0,29 |
| 2025-04-30 01:00 | GBPUSD | vente | 1.3391 | 1.3421 | 1.3288 | +3,34 |
| 2025-05-20 13:00 | EURJPY | achat | 162.9 | 162.39 | 162.66 | -0,50 |
| 2025-06-02 23:00 | EURUSD | achat | 1.1457 | 1.1406 | 1.1415 | -0,84 |
| 2025-06-23 05:00 | EURUSD | achat | 1.1515 | 1.1475 | 1.1475 | -1,02 |
| 2025-07-08 10:00 | EURUSD | vente | 1.1732 | 1.1769 | 1.1731 | -0,00 |
| 2025-08-08 05:00 | EURGBP | vente | 0.86701 | 0.8689 | 0.86517 | +0,91 |
| 2025-08-21 00:00 | AUDUSD | vente | 0.64296 | 0.64691 | 0.64312 | -0,07 |
| 2025-08-26 06:00 | EURUSD | vente | 1.1625 | 1.1665 | 1.1665 | -1,02 |
| 2025-09-02 01:00 | GBPJPY | achat | 199.71 | 199.15 | 199.15 | -1,04 |
| 2025-09-10 12:00 | AUDJPY | achat | 97.542 | 97.268 | 97.421 | -0,51 |
| 2025-09-12 18:00 | AUDUSD | achat | 0.66551 | 0.66315 | 0.66642 | +0,34 |
| 2025-09-26 07:00 | AUDUSD | vente | 0.6533 | 0.65658 | 0.65555 | -0,72 |
| 2026-01-27 02:00 | EURUSD | achat | 1.1898 | 1.1872 | 1.1872 | -1,03 |
| 2026-02-11 14:00 | AUDUSD | achat | 0.71271 | 0.70786 | 0.7123 | -0,10 |
| 2026-03-13 19:00 | EURJPY | vente | 182.39 | 182.94 | 182.75 | -0,68 |
| 2026-03-16 05:00 | GBPJPY | vente | 211.13 | 211.64 | 211.64 | -1,05 |
| 2026-03-17 05:00 | GBPUSD | vente | 1.3287 | 1.334 | 1.334 | -1,02 |
| 2026-03-17 05:00 | EURUSD | vente | 1.1484 | 1.1529 | 1.1529 | -1,02 |
| 2026-04-20 06:00 | GBPJPY | vente | 214.38 | 214.74 | 214.74 | -1,07 |
| 2026-05-12 00:00 | EURUSD | vente | 1.177 | 1.1793 | 1.1723 | +2,05 |
| 2026-05-29 04:00 | EURAUD | vente | 1.6247 | 1.6278 | 1.6227 | +0,59 |
| 2026-06-01 00:00 | EURAUD | vente | 1.6213 | 1.6245 | 1.6227 | -0,50 |
| 2026-06-04 07:00 | NZDUSD | vente | 0.58672 | 0.59122 | 0.58771 | -0,25 |
| 2026-06-10 13:00 | NZDUSD | achat | 0.58265 | 0.58015 | 0.58015 | -1,06 |
| 2026-06-29 23:00 | GBPAUD | achat | 1.9256 | 1.9205 | 1.9222 | -0,72 |
| 2026-07-08 06:00 | GBPUSD | achat | 1.3364 | 1.3341 | 1.3341 | -1,05 |
| 2026-08-12 02:00 | GBPAUD | achat | 1.9136 | 1.9097 | 1.9124 | -0,35 |
| 2026-09-01 04:00 | USDJPY | achat | 159.87 | 159.36 | 160.07 | +0,40 |
| 2026-09-13 23:00 | AUDUSD | vente | 0.71541 | 0.71906 | 0.71362 | +0,46 |
| 2026-09-13 23:00 | NZDUSD | vente | 0.58123 | 0.58383 | 0.57813 | +1,13 |
| 2026-09-14 00:00 | EURUSD | vente | 1.1591 | 1.162 | 1.1557 | +1,15 |

