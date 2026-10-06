# La masterclass d'Amirou vérifiée sur les cours réels (2012-2026)

> **Données** : bougies journalières Dukascopy du 2 janvier 2012 au 1er octobre 2026 ([`data/prix/journalier_dukascopy.csv`](../data/prix/journalier_dukascopy.csv)). 2026 est complété par l'horaire Yahoo regroupé par jour, car Dukascopy ne publie le fichier annuel qu'en fin d'année. Pour la Bombe, le bébé abandonné en horaire et la variante « Londres » : bougies horaires Yahoo, décembre 2023 – septembre 2026.
> **Paires** : les 11 instruments étudiés : **EURUSD, GBPUSD, USDJPY, AUDJPY, AUDUSD, NZDUSD, USDCAD, GBPJPY, EURJPY, EURNZD et l'or (XAUUSD)**. L'or est exclu des tests MLQ (pas de niveaux de 250 pips comparables). Pour ajouter une paire, il suffit de relancer la commande de la section 8.
> **Scripts** :
> - [`scripts/tester_masterclass.py`](../scripts/tester_masterclass.py) (T1 à T8) ;
> - [`scripts/strategie_combinee.py`](../scripts/strategie_combinee.py) (combinaisons) ;
> - [`scripts/tester_bebe_abandonne.py`](../scripts/tester_bebe_abandonne.py) ;
> - [`scripts/tester_strategie_bombe.py`](../scripts/tester_strategie_bombe.py) ;
> - [`scripts/analyse_par_paire.py`](../scripts/analyse_par_paire.py).
>
> **Résultats bruts** :
> - [`data/masterclass_resultats.json`](../data/masterclass_resultats.json) ;
> - [`data/masterclass_trades.csv`](../data/masterclass_trades.csv) ;
> - [`data/strategie_combinee.csv`](../data/strategie_combinee.csv) ;
> - [`data/strategie_combinee_trades.csv`](../data/strategie_combinee_trades.csv).
>
> **Détail par paire et par année** : [`STRATEGIES_PAR_PAIRE.md`](STRATEGIES_PAR_PAIRE.md).

## Dates : les sessions de masterclass et les sources de chaque règle testée

**Les résumés de masterclass fournis par l'utilisateur ne sont pas datés.** Les dates ci-dessous viennent du canal.

**Sessions de masterclass annoncées dans le canal** :

| Session | Message |
|---|---|
| Webinaire gratuit, 4 octobre 2020 | #2763, #2769 |
| 1re masterclass « pour les plus avancés », à partir du 15 octobre 2020 | #2720, #2736 |
| Masterclass 3.0 en ligne, 1er juin 2021 | #3983 |
| Programme de fin février 2023 | #7249 |
| Masterclass de fin juin 2023 (43 participants), rediffusion d'une session du 2 septembre 2023 | #7925, #8034, #9200, #9679 |
| Masterclass de février 2024 (groupe créé le 16 janvier, fin mi-mai 2024) | #10456, #11281 |
| Masterclass du 15 juillet 2024 ; masterclass gratuite en deux parties, août et 7 septembre 2024 | #11312, #11615, #11650 |
| Masterclass du 12 janvier 2025 | #12610, #12652 |
| Masterclass de juillet 2025 (groupe créé le 6 juillet) | #13241, #13454 |
| Masterclass gratuite du 29 mars 2026 (replay supprimé le 5 avril) | #14619, #14623, #14650 |
| Masterclass du 12 avril 2026 | #14651, #14696 |
| Prochaine annoncée : novembre 2026 | #15218, #15339 |

**Date à laquelle chaque règle testée apparaît dans le canal** :

| Règle testée | Première apparition dans le canal | Autres messages |
|---|---|---|
| T1 Plus haut de la semaine mardi-mercredi « 70 % » | #7820, 5 avril 2023 | — |
| Saisonnalité (introduction) | #7762, 30 mars 2023 | 31 messages jusqu'en 2026 |
| MLQ (zones institutionnelles) | #6913, 16 novembre 2022 | 23 messages jusqu'au 19 juin 2026 |
| IBO / CBO | #11431, 20 juin 2024 | #11459 (vidéo promise), jusqu'au 8 avril 2026 |
| Englobante (flashcards « Naruto ») | #13305, 23 mai 2025 | flashcards jusqu'en juin 2026 (#14986) |
| T3 Lundi et mardi haussiers, mercredi prend le high (« 21 fois en 5 ans, 71 % ») | #14577-#14579, 18 mars 2026 | #14631 (1er avril 2026) |
| T2 Lundi-mardi-mercredi (« trois barres ») | résumé de masterclass ; dans le canal : #14631 (1er avril 2026), #14835 (11 mai 2026) | — |
| T4 AUDJPY en avril, plus bas en 1re semaine | #14662, 7 avril 2026 | EURJPY en juin : #14907 (31 mai 2026) |
| Corrélation AUDUSD/NZDUSD | résumé de masterclass ; la corrélation est évoquée dès #305 (2 avril 2019) | — |
| Bébé abandonné, Bombe, consolidation-expansion | **uniquement dans les résumés de masterclass** (aucun message du canal) | — |

- La plupart des règles chiffrées sont **récentes** (2023-2026). Elles ont donc été formulées après coup, sur des années que l'on peut vérifier.
- **Période testée** : toutes les règles journalières sont testées sur 2012-2026, donc avant et après leur publication. Les résultats après publication, de 2023 à 2026 selon la règle, figurent dans les tableaux par année de [`STRATEGIES_PAR_PAIRE.md`](STRATEGIES_PAR_PAIRE.md) et de son annexe.

## En bref

![Annoncé et mesuré](../assets/figures/masterclass_promesses.png)

| Affirmation de la masterclass | Annoncé | Mesuré 2012-2026 | Verdict |
|---|---|---|---|
| Le plus haut de la semaine se forme le mardi ou le mercredi | 70 % | **30 %** (le hasard donnerait 40 %) | ❌ c'est l'inverse : lundi et vendredi dominent |
| « Trois barres » lundi-mardi-mercredi sur GBPUSD | 85 % | objectif atteint **27 %**, −0,06 R | ❌ |
| « Trois barres » sur AUDJPY | 70-75 % | objectif atteint **23 %**, −0,13 R | ❌ |
| Lundi et mardi haussiers, mercredi prend le high (#14577) | 21 cas en 5 ans, 71 % | **718 cas** en 5 ans (11 instruments), **21 %** d'objectifs, −0,23 R | ❌ |
| AUDJPY en avril : plus bas du mois en 1re semaine (#14662) | 75 % | **50 %** (2015-2024) | ❌ |
| MLQ : zone ±25 pips, stop 50, objectif 250 (1:5) | rentable dès 17 % de réussite | **15,6 %**, −0,08 R ; niveaux décalés : −0,06 à −0,10 R | ❌ aucun avantage |
| Après une consolidation, l'expansion suit « systématiquement » | ~100 % | **41 %** (et 44 % de retours au milieu du range) | ❌ |
| AUDUSD et NZDUSD corrélés « de l'ordre de 80 % » | 80 % | **0,83** (de 0,65 à 0,92 selon l'année) | ✅ |
| Bébé abandonné : la 4e bougie explose dans le sens des deux bougies de même couleur | « très fiable » | **46 à 50 %**, comme le témoin | ❌ |
| Bombe (H1) sur les paires en yen | « favorable » | 10 trades, 1 gagnant | ❔ trop peu de cas, pas confirmé |
| Combinaison **trois barres + MLQ** (testée ici, pas dans la masterclass) | — | +0,39 R (2012-2019, t = 1,8), **+0,17 R (2020-2026, t = 1,1)** ; des niveaux décalés font presque aussi bien | ❌ prometteuse sur 4 paires, **ne résiste pas** aux 11 paires |

**Conclusion** : aucun des pourcentages de la masterclass ne se retrouve sur 15 ans de cours. Certains sont même inversés (jour du plus haut, consolidation). Ces chiffres ressemblent à des souvenirs de cas marquants ou à des comptages sur une courte période choisie. Ce ne sont pas des statistiques. La seule affirmation confirmée est la corrélation AUDUSD/NZDUSD, un fait connu. La combinaison qui semblait prometteuse sur 4 paires (trois barres + MLQ, section 6) ne résiste pas à l'ajout des 7 autres instruments.

## Méthode commune
- **Une règle = un algorithme** : chaque règle de la masterclass est traduite en conditions chiffrées sur les bougies, sans regarder le résultat avant. Quand la masterclass est floue (« bougie pleine »), le choix est indiqué.
- **Prudence** :
  - si l'objectif et le stop sont touchés le même jour, on compte le stop ;
  - le jour de l'entrée, seul le stop compte, car l'ordre des prix dans la bougie est inconnu ;
  - le spread est déduit.
- **Témoin** : chaque stratégie est comparée à la même règle appliquée au hasard (toute bougie, ou niveaux décalés). Un résultat ne compte que s'il fait mieux que son témoin.
- **Validation** :
  - les combinaisons sont choisies sur 2012-2019, puis vérifiées une seule fois sur 2020-2026 ;
  - par paire, on vérifie que les « meilleures paires » d'une période restent les meilleures sur l'autre.

> **Correction d'un bug pendant ce travail (T5, MLQ)** : la première version entrait au bord éloigné de la zone (MLQ + 25 pips pour une vente) alors que la condition ne vérifiait que le bord proche. Elle comptait donc des trades remplis à un prix jamais atteint. Elle choisissait aussi le niveau juste sous le plus haut du jour, ce qui écartait les niveaux traversés, donc perdants. Résultat faux : +0,55 R. Après correction : −0,04 R. Les niveaux décalés de 50 ou 125 pips donnent le même ordre de grandeur, ce qui confirme que le contrôle fonctionne.

## 1. Le jour du plus haut et du plus bas de la semaine (T1)

![Jour des extrêmes](../assets/figures/masterclass_jours_extremes.png)

Sur 8 415 semaines (11 instruments) :

| | Lundi | Mardi | Mercredi | Jeudi | Vendredi | Mardi + mercredi |
|---|---|---|---|---|---|---|
| Plus haut de la semaine | 25,1 % | 15,3 % | 14,6 % | 16,9 % | 28,1 % | **29,8 %** |
| Plus bas de la semaine | 30,4 % | 14,1 % | 13,0 % | 15,7 % | 26,8 % | **27,1 %** |

- Les extrêmes de la semaine se forment surtout **le lundi et le vendredi**, aux bords de la semaine. C'est un effet mécanique : le premier et le dernier jour ont plus de chances d'être les extrêmes d'une marche au hasard.
- Le conseil « ne pas trader le lundi et le vendredi parce que les extrêmes se font mardi-mercredi » (#7820) ne s'appuie donc pas sur les données.

## 2. Lundi-mardi-mercredi : les « trois barres » (T2)

![Schéma](../assets/figures/guide_lundi_mardi_mercredi.png)

**Règle testée**, en vente (l'achat est symétrique) :
- **lundi** haussier « plein » : corps ≥ 60 % du range, clôture dans le quart haut ;
- **mardi** rouge, qui clôture sous la clôture du lundi ;
- **entrée** à la clôture du mardi ;
- **stop** 2 pips au-dessus du plus haut du mardi ;
- **objectif** : plus bas du lundi, au moins 60 pips et RR ≥ 1,2 (filtre de la masterclass) ;
- sortie au plus tard le vendredi.

| Version | Trades | Objectif atteint | Gagnants | R moyen |
|---|---|---|---|---|
| Toutes les configurations (sans filtre) | 1 000 | 45,4 % | 48,9 % | −0,08 |
| **Avec le filtre 60 pips et RR ≥ 1,2** | **311** | **24,4 %** | 33,8 % | **−0,05** |
| Filtre + le mardi dépasse d'abord le plus haut du lundi | 226 | 27,9 % | 37,2 % | −0,02 |
| Filtre + plus haut du mardi fait à Londres (2024-2026) | 25 | 40 % | 52 % | +0,53 |
| Filtre + plus haut du mardi hors de Londres (2024-2026) | 45 | 24 % | 31 % | −0,06 |

| Paire | Trades | Objectif | Gagnants | R moyen |
|---|---|---|---|---|
| GBPUSD | 26 | 26,9 % | 34,6 % | −0,06 |
| EURUSD | 18 | 11,1 % | 33,3 % | −0,34 |
| AUDJPY | 31 | 22,6 % | 32,3 % | −0,13 |
| USDJPY | 36 | 30,6 % | 38,9 % | +0,03 |
| AUDUSD | 19 | 15,8 % | 31,6 % | −0,25 |
| NZDUSD | 12 | 41,7 % | 41,7 % | +0,56 |
| USDCAD | 25 | 20,0 % | 24,0 % | −0,17 |
| EURJPY | 35 | 20,0 % | 28,6 % | −0,27 |
| GBPJPY | 35 | 25,7 % | 31,4 % | −0,24 |
| EURNZD | 29 | 34,5 % | 41,4 % | +0,51 |
| Or (XAUUSD) | 45 | 22,2 % | 35,6 % | +0,03 |

![Trois barres par paire et par année](../assets/figures/paire_lundi_mardi_mercredi_trois_barres.png)

- **Le setup est rare** : 0,16 par mois et par paire, soit environ 2 par an et par paire, et 21 par an sur les 11 instruments.
- **85 % sur GBPUSD n'est pas retrouvé** : 27 % d'objectifs sur 15 ans.
- **Depuis 2024 en revanche, GBPUSD fait +0,87 R** sur 8 trades (5 gagnants) :
  - gagnants : 03/04/2024, 05/06/2024, 30/04/2025, 07/01/2026, 11/03/2026 ;
  - perdants : 11/09/2024, 04/06/2025, 20/05/2026.

  Si la masterclass a été construite sur ces dernières années, cela peut expliquer l'impression de fiabilité. Mais 8 trades ne prouvent rien, et 2012-2023 est négatif.
- **Variante « Londres »** : quand le plus haut du mardi se fait pendant la session de Londres, +0,53 R (25 trades), contre −0,06 R sinon (45 trades). C'est la seule variante intéressante, mais elle ne porte que sur 2024-2026 (horaire Yahoo) : à suivre.
- NZDUSD (+0,56 R, 12 trades) et EURNZD (+0,51 R, 29 trades) sont positives. Les croisés du yen GBPJPY et EURJPY sont négatifs.

## 3. « Lundi et mardi haussiers, mercredi prend le high » (T3, #14577-#14579)

**Annoncé** : 21 fois en 5 ans, 71 % de réussite avec stop 20 pips et objectif 60 pips.

**Mesuré** :
- sur les 5 dernières années (depuis mars 2021), le schéma se produit **718 fois** sur 11 instruments (56 fois sur EURUSD seul), et non 21 ;
- vente au plus haut du mardi quand mercredi le dépasse : **21 % d'objectifs**, 22 % de gagnants, **−0,23 R** par trade ;
- avec un stop de 20 pips pour un objectif de 60, le hasard donnerait 25 % : le résultat est même un peu pire, car un mercredi qui dépasse le plus haut du mardi continue souvent de monter ;
- sur 2012-2026 : 1 717 trades, 21,2 %, −0,20 R. Aucune paire n'est rentable de façon stable : AUDUSD fait +0,24 R sur 5 ans mais +0,08 sur 15 ans ; GBPUSD +0,09 R sur 5 ans, mais négative avant ;
- l'or est un cas à part : un stop fixe de 20 pips (2 $) y est minuscule, d'où −1,0 R par trade. La règle n'est de toute façon pas pensée pour l'or.

## 4. AUDJPY en avril, et le « plus bas du mois en 1re semaine » (T4, #14662)

| Paire | Avril 2015-2024 : plus bas en semaine 1 | Repli moyen sous l'ouverture du mois | Avrils haussiers | Tous les mois : plus bas en semaine 1 | **Mois haussiers** : plus bas en semaine 1 |
|---|---|---|---|---|---|
| **AUDJPY** | **50 %** (annoncé : 75 %) | 176 pips (annoncé : 91) | 70 % | 45 % | **72 %** |
| EURUSD | 20 % | 201 pips | 50 % | 35 % | 60 % |
| GBPUSD | 40 % | 274 pips | 70 % | 32 % | 58 % |
| USDJPY | 50 % | 193 pips | 60 % | 43 % | 68 % |

- **D'où vient probablement le « 75 % »** : quand un mois **finit en hausse**, son plus bas est souvent au début (72 % sur AUDJPY). C'est automatique : si le prix monte, le point bas est plutôt au début.
- Mais on ne sait pas à l'avance si le mois finira en hausse. Utilisé dans l'autre sens (« le plus bas sera en semaine 1, donc j'achète »), la règle ne vaut plus que 45-50 %.

## 5. MLQ, bébé abandonné, consolidation, Bombe

### MLQ ±25 / 50 / 250 pips (T5)

![MLQ](../assets/figures/guide_mlq.png)

**Règle testée** :
- premier niveau de 250 pips rencontré à plus de 50 pips de la clôture de la veille ;
- entrée limite au bord de la zone de ±25 pips, stop 50 pips (l'autre bord), objectif 250 pips, sur 30 jours au maximum.

| Niveaux | Trades | Objectif | R moyen |
|---|---|---|---|
| **MLQ (multiples de 250 pips)** | 6 055 | **15,6 %** | **−0,08** |
| Niveaux décalés de 50 pips (témoin) | 6 007 | 15,9 % | −0,06 |
| Niveaux décalés de 125 pips, à mi-chemin (témoin) | 5 960 | 15,2 % | −0,10 |

- Il faut 16,7 % de réussite pour être à l'équilibre avec un ratio de 1:5 : le MLQ seul est **juste en dessous**, comme n'importe quel niveau.
- Les années vont de −0,28 R (2018) à +0,17 R (2021), sans régularité.
- Les MLQ font comme les niveaux décalés (−0,08 R contre −0,06 et −0,10 R) : ils ne « tiennent » pas mieux qu'un niveau quelconque.

### Bébé abandonné (définition corrigée)

![Bébé abandonné](../assets/figures/guide_bebe_abandonne.png)

**Définition** : bougies 1 et 3 de même couleur, bougie 2 de couleur opposée et englobée par les deux. Entrée à la clôture de la bougie 3 ; on regarde la bougie 4.

| Échelle | Figures | 4e bougie dans le sens annoncé | Témoin (même couleurs, sans englobement) | R moyen, objectif 1 R |
|---|---|---|---|---|
| Horaire, 13 paires, 2024-2026 (mèches englobées) | 2 578 | 46,5 % | 48,9 % | −0,17 (témoin −0,17) |
| Horaire (corps englobés) | 5 383 | 47,2 % | 48,9 % | −0,17 |
| Journalier, 11 instruments, 2012-2026 (mèches) | 527 | 49,9 % | 49,7 % | −0,04 (témoin −0,06) |
| Journalier (corps) | 1 343 | 50,7 % | 49,7 % | +0,03 (t = 1,5) |

La 4e bougie part dans le sens annoncé **une fois sur deux**, exactement comme après n'importe quelles trois bougies. En horaire, le spread rend tout trade perdant.

### Consolidation puis expansion (T8)
Consolidation = 5 jours dans un range de moins de 1,5 ATR ; expansion = le prix avance d'1 ATR dans le sens de la cassure avant de revenir au milieu du range.

| Cassure | Cas | Expansion | Retour au milieu du range |
|---|---|---|---|
| Après une consolidation | 1 686 | **41 %** | **44 %** |
| Cassure ordinaire | 8 786 | 46 % | 27 % |

C'est **l'inverse** de l'affirmation : une cassure de range étroit revient plus souvent dans le range qu'elle ne s'étend (fausse cassure).

### Bombe (H1, 2024-2026, 13 paires)
- 46 trades, 35 % de gagnants, +0,11 R par trade (témoin +0,01 R).
- **Paires en yen** : 10 trades, **un seul gagnant** (EURJPY, 23/07/2024, +8,3 R). Les 9 autres sont des pertes ou de petits gains. Le +0,30 R moyen tient entièrement à ce trade.
- Avec 1,4 setup par mois, il faudrait plusieurs années pour savoir si la Bombe a un avantage. Rien ne permet de dire qu'elle est meilleure sur le yen.

### Corrélation AUDUSD / NZDUSD (T7)
- Corrélation des rendements journaliers sur 2012-2026 : **0,83**. C'est exact : la masterclass annonce « de l'ordre de 80 % ».
- Elle varie selon l'année : 0,65 en 2017, 0,92 en 2022, 0,83 en 2026.
- Conséquence pratique, juste aussi : prendre le même trade sur AUDUSD et NZDUSD revient presque à doubler le risque.

## 6. Combiner les briques : englobante, mercredi, MLQ, trois barres

![Combinaisons](../assets/figures/masterclass_combinaisons.png)

**Briques** :
- **E** : englobante journalière ;
- **jour** : englobante formée le mardi ou le mercredi ;
- **M** : l'extrême de la bougie signal à moins de 25 pips d'un MLQ ;
- **T** : trois barres.

**Trade** : entrée à la clôture de la bougie signal, stop à l'autre extrême, objectif 1 R ou 2 R, ou sortie à la clôture du 3e jour. 12 combinaisons × 3 gestions = 36 essais, **choisis sur 2012-2019**. 11 instruments (sans l'or pour le MLQ).

| Combinaison (sortie au 3e jour) | 2012-2019 : trades, R | 2020-2026 : trades, R (t) |
|---|---|---|
| Toute bougie (témoin) | 22 892 ; −0,03 | 19 290 ; 0,00 (−0,2) |
| E (englobante seule) | 5 852 ; −0,02 | 4 804 ; +0,02 (1,0) |
| E + englobante du mercredi | 1 235 ; +0,04 | 974 ; +0,02 (0,6) |
| E + MLQ | 1 096 ; −0,05 | 876 ; +0,10 (2,2) |
| E + MLQ + mardi | 220 ; +0,02 | 175 ; +0,10 (1,1) |
| MLQ seul | 4 097 ; −0,02 | 3 521 ; +0,02 (0,9) |
| T (trois barres) | 615 ; +0,07 | 569 ; +0,07 (1,0) |
| **T + MLQ** | **119 ; +0,39 (t = 1,8)** | **101 ; +0,17 (1,1)** |
| T + englobante | 140 ; +0,06 | 121 ; −0,11 |

**Comment le résultat a évolué avec le nombre de paires.** Sur les 4 premières paires, « trois barres + MLQ » semblait la seule piste sérieuse. Avec 11 instruments, elle ne tient plus :

| Paires testées | 2012-2019 | 2020-2026 | Tous les MLQ | Niveaux décalés de 50 à 200 pips (témoins) |
|---|---|---|---|---|
| 4 (EURUSD, GBPUSD, USDJPY, AUDJPY) | +0,72 R (t = 2,8) | +0,31 R | +0,54 R | −0,31 à +0,17 R |
| 6 (+ AUDUSD, NZDUSD) | +0,66 R (t = 3,3) | +0,18 R | +0,45 R | −0,20 à +0,12 R |
| **11** (+ USDCAD, GBPJPY, EURJPY, EURNZD) | **+0,39 R (t = 1,8)** | **+0,17 R (t = 1,1)** | **+0,29 R** | **−0,10 à +0,17 R** |

- **Les nouvelles paires ne confirment pas la règle** : USDCAD −0,25 R, EURJPY −0,42 R, GBPJPY −0,04 R ; seule EURNZD est très positive (+1,22 R sur 17 trades).
- **Le contrôle ne la distingue plus du hasard** : des niveaux décalés de 125 ou 175 pips, qui ne sont pas des MLQ, donnent +0,12 et +0,17 R, presque autant que les vrais MLQ (+0,29 R).
- **C'est le schéma classique d'un résultat dû au hasard** : excellent sur l'échantillon où on l'a trouvé, il fond quand on ajoute des données. Avec 36 combinaisons essayées, il fallait s'y attendre.
- Liste complète des occurrences : `data/par_paire/occurrences_trois_barres_mlq_sortie_au_3e_jour.csv`.

**Les autres combinaisons** font à peine mieux que le témoin. E + MLQ est positive en 2020-2026 (+0,10 R, t = 2,2) mais négative en 2012-2019 : c'est typiquement le genre de résultat qui ne se reproduit pas.

## 7. Ce qu'il faut retenir
1. **Les pourcentages de la masterclass (70 %, 75 %, 85 %) ne correspondent pas aux cours réels.** Sur 15 ans et 11 instruments, les règles donnent 20 à 50 % selon les cas, souvent moins que le hasard une fois le spread déduit.
2. **Plusieurs affirmations sont à l'envers** :
   - les extrêmes de la semaine se font surtout le lundi et le vendredi ;
   - une cassure de consolidation est plus souvent fausse que vraie.
3. **Les « bons » chiffres viennent souvent d'un raisonnement après coup** : « le plus bas est en semaine 1 » est vrai pour les mois qui ont monté, mais on ne le sait qu'à la fin du mois.
4. **Ce qui est juste** : AUDUSD et NZDUSD sont bien corrélées à environ 80 %.
5. **Aucune règle ni aucune combinaison n'a d'avantage robuste.** « Trois barres + MLQ », prometteuse sur 4 paires, ne résiste pas aux 11 instruments. Seule la variante « plus haut du mardi à Londres » (+0,53 R sur 25 trades, 2024-2026) reste à suivre, faute d'historique horaire plus ancien.

## 8. Relancer ou compléter
```bash
python scripts/prix_dukascopy_journalier.py --debut 2012 --paires EURUSD GBPUSD USDJPY AUDJPY AUDUSD NZDUSD USDCAD GBPJPY EURJPY EURNZD XAUUSD   # ajouter les paires téléchargées
python scripts/tester_masterclass.py && python scripts/strategie_combinee.py && python scripts/tester_bebe_abandonne.py
python scripts/analyse_par_paire.py && python scripts/figures_rapports.py
```
