# Améliorer les stratégies avec le playbook (tracker + journal des stratégies)

*17/10/2026. Question de l'utilisateur : en se basant uniquement sur les deux pages (tracker saisonnalité & fonda, journal des stratégies), peut-on améliorer les statistiques des trades ? Puis : et avec un stop de 20 à 50 pips ?*

*Scripts : [`scripts/tester_filtres_playbook.py`](../scripts/tester_filtres_playbook.py) → `data/filtres_playbook/` ; [`scripts/tester_stops_fixes.py`](../scripts/tester_stops_fixes.py) → `data/stops_fixes/`.*

## 1. Six règles « ne pas entrer quand… », tirées des colonnes du tracker

Les règles ont été fixées avant le test, et chacune est mesurée sur les cinq stratégies du journal.

| Règle | Ce qu'elle écarte |
|---|---|
| R1 saisonnalité contraire | trades contre la moyenne du même mois sur 10 ans |
| R2 annonce majeure dans les 24 h | taux, NFP, inflation, chômage ou PIB sur l'une des deux devises |
| R3 banque centrale dans les 48 h | une décision de taux sur l'une des deux devises |
| R4 COT extrême dans le sens du trade | devise achetée déjà au-dessus du 90e centile des gérants d'actifs sur 3 ans, ou devise vendue sous le 10e |
| R5 contre le narratif d'Amirou | trades contre son biais écrit sur 14 jours |
| R6 contre le taux US 2 ans | achat du dollar quand le 2 ans a baissé de 3 pb ou plus sur 5 jours, et l'inverse |

**Gain en R par trade quand on applique la règle** (R moyen des trades gardés moins R moyen de tous) :

| Règle | Englobante horaire 2024-26 | Englobante journalière 2012-26 | Lundi-mardi-mercredi | Cassure-retour MLQ | Suivi de tendance |
|---|---|---|---|---|---|
| R1 saisonnalité | 0,00 | 0,00 | +0,08 | −0,01 | 0,00 |
| R2 annonce 24 h | 0,00 | −0,01 | −0,18 | +0,01 | 0,00 |
| R3 banque centrale 48 h | +0,02 | +0,01 | **−0,32** | +0,02 | +0,01 |
| R4 COT extrême | **+0,05** | **−0,03** | +0,06 | +0,01 | +0,02 |
| R5 contre Amirou | +0,01 | +0,03 | +0,21 | −0,01 | 0,00 |
| R6 contre le 2 ans | +0,02 | −0,01 | +0,12 | **+0,12** | **−0,04** |

- **Aucune règle n'aide partout.** La plus régulière (R3, ne pas entrer dans les 48 h d'une décision de banque centrale) aide dans 7 cas sur 9, avec des gains de 0,01 à 0,02 R. Mais elle coûte 0,32 R sur lundi-mardi-mercredi, dont les meilleurs trades tombent justement autour des banques centrales.
- **R4 (COT extrême)** aide l'englobante récente (+0,05) et le suivi de tendance, mais nuit à l'englobante sur 2012-2026.
- **R6 (taux à 2 ans)** aide nettement la cassure-retour (+0,12, environ 3,7 erreurs types), mais nuit au suivi de tendance. On retrouve le constat de `analyses/NOTIONS_MEET.md` : c'est un effet de période (2024-2026).
- **La saisonnalité (R1) et les annonces (R2) ne servent à rien** comme filtres.
- **Les écarts sur lundi-mardi-mercredi** (88 trades) sont trop instables pour être utilisés.

**Le meilleur couple (R3 + R4)** appliqué aux cinq stratégies :

| Stratégie | Tous les trades | Trades gardés | Écart |
|---|---|---|---|
| Englobante + MLQ horaire 2024-2026 | +0,10 R (764) | **+0,16 R** (512) | +0,07, dans les deux moitiés de la période |
| Cassure-retour MLQ | +0,01 R | +0,03 R | +0,02 (seulement la 2e moitié) |
| Suivi de tendance 1 R | −0,13 R | −0,11 R | +0,02, toujours perdant |
| Englobante + MLQ journalière 2012-2026 | +0,00 R | −0,02 R | **−0,02** |
| Lundi-mardi-mercredi | +0,39 R | +0,16 R | **−0,23** |

## 2. Stop fixe de 20, 30, 40 ou 50 pips

Les signaux, l'entrée et la sortie au temps ne changent pas. L'objectif reste en R de la stratégie : 2 R, ou 1 R pour le suivi de tendance. Pour lundi-mardi-mercredi, l'objectif d'origine (plus haut ou plus bas du lundi) est gardé, avec une variante à 2 R.

| Stratégie | Stop d'origine | 20 pips | 30 pips | 40 pips | 50 pips |
|---|---|---|---|---|---|
| Englobante + MLQ horaire 2024-2026 | **+0,10** (baisse max 17 R) | −0,01 | +0,04 | +0,07 | +0,09 (baisse max 27 R) |
| Englobante + MLQ journalière 2012-2026 | **+0,00** | −0,28 | −0,13 | −0,06 | −0,02 |
| Lundi-mardi-mercredi (objectif d'origine) | **+0,39** | +0,24 | +0,38 | +0,33 | +0,18 |
| Cassure-retour MLQ | +0,01 | −0,09 | −0,01 | −0,02 | +0,02 |
| Suivi de tendance 1 R | −0,13 | −0,11 | −0,08 | −0,05 | −0,04 |

- **Un stop fixe ne fait jamais mieux que le stop d'origine** placé derrière la structure (extrême de la bougie, du mardi, ATR). Au mieux il fait jeu égal (50 pips sur l'englobante, 30 pips sur lundi-mardi-mercredi), et souvent avec une baisse maximale plus forte.
- **Plus le stop fixe est petit, plus c'est mauvais.** À 20 pips, le bruit de marché touche le stop avant que l'idée ait le temps de jouer, et le spread pèse plus lourd en R.
- Sur le suivi de tendance, un stop plus large réduit la perte (de −0,13 à −0,04 R), surtout parce que le spread compte moins. La stratégie reste perdante.

## 3. En résumé
- **Le playbook (tracker + journal) n'améliore pas les stratégies de façon fiable.** Une règle qui aide une stratégie en dégrade une autre, ou ne tient que sur une période. Les gains vont de 0,01 à 0,07 R, à la limite du bruit.
- **Le seul candidat sérieux** : ne pas prendre l'englobante + MLQ dans les 48 h d'une décision de banque centrale, ni quand le COT est déjà extrême dans le sens du trade (+0,10 → +0,16 R sur 2024-2026). Il ne tient pas sur 2012-2026. Il mérite seulement d'être **noté à côté du suivi en démo**, comme le narratif, sans changer la règle suivie.
- **Le stop fixe de 20 à 50 pips n'apporte rien.** Gardez le stop derrière la structure. Pour réduire le risque, la seule mesure efficace reste la taille de position.

## Stop au point d'entrée (BE) après +1 R (17/10/2026)

Script : `scripts/tester_be_1r.py` → `data/be_1r/`. Pour chaque stratégie, on garde le même signal, la même entrée, le même stop et le même objectif. On remonte simplement le stop au prix d'entrée quand le prix a fait +1 R. Le BE ne s'applique qu'à partir de la bougie suivante. On déduit le spread. Le suivi de tendance n'est pas concerné : son objectif est 1 R.

| Stratégie | Sans BE | BE à +1 R | BE à +1,5 R | Trades | Sortis au BE (avec BE à +1 R) |
|---|---|---|---|---|---|
| Englobante + MLQ, horaire 2024-26 | +0,10 ± 0,04 | +0,11 ± 0,04 | +0,10 | 764 | 98 |
| Englobante + MLQ, journalier 2012-26 | +0,00 | +0,01 | +0,01 | 1 973 | 168 |
| Lundi-mardi-mercredi | **+0,39 ± 0,19** | +0,27 ± 0,18 | +0,33 | 88 | 18 |
| Cassure-retour MLQ | +0,01 | −0,01 | +0,00 | 3 941 | 1 035 |

Ce que l'on regarde ensuite, ce sont les trades sortis au BE : qu'auraient-ils donné sans BE ?

- **Lundi-mardi-mercredi** : les 18 trades sortis au BE auraient donné 6 objectifs, 7 stops et 5 sorties le vendredi, soit **+8,9 R au total**. Avec le BE, ils donnent −1,1 R (spread compris). L'objectif d'origine est le plus haut ou le plus bas du lundi : il est souvent loin, et le prix revient fréquemment au point d'entrée avant de l'atteindre. Le BE réduit la plus forte baisse (9,2 → 7,4 R) et améliore la première moitié de la période (−0,12 → −0,01 R), mais il coûte 0,30 R par trade sur la seconde.
- **Englobante horaire** : le gain de +0,014 R par trade est bien inférieur à l'erreur type (0,04). Il ne vient que de la seconde moitié et disparaît sur le journalier 2012-2026.
- **Cassure-retour** : le BE coupe 320 trades qui seraient allés à l'objectif.

Conclusion : le BE à +1 R ne fait pas mieux que la règle d'origine. Il transforme surtout des gains en sorties à zéro. Il réduit la baisse maximale, ce qui peut rendre la stratégie plus facile à suivre, mais il ne l'améliore pas.

## Écarter les paires, mois ou jours perdants (17/10/2026)

Script : `scripts/tester_exclure_perdants.py` → `data/exclure_perdants/resultats.csv`. Pour chaque stratégie, on écarte les cases qui perdent : paires, mois (la saisonnalité propre à la stratégie), paire × mois, paire × sens ou jours de la semaine. On mesure le résultat de deux façons :

- **après coup** : les cases perdantes sont repérées sur tous les trades, puis retirées de ces mêmes trades ;
- **en conditions réelles (walk-forward)** : chaque trimestre, on ne repère les cases perdantes que sur les trades déjà connus, puis on applique le filtre au trimestre suivant.

Les tests portent sur 2025-2026 pour les stratégies de 2024-2026 et sur 2015-2026 pour l'englobante journalière.

| Stratégie et filtre | Gain par trade après coup | Gain par trade en conditions réelles |
|---|---|---|
| Englobante horaire, paire × mois | +0,26 R | −0,01 R |
| Englobante horaire, paires | +0,08 | −0,03 |
| Englobante horaire, jours (mardi et vendredi écartés) | +0,10 | **+0,10** (t = 2,3) |
| Englobante journalière 2012-26, paire × mois | +0,25 | +0,03 |
| Englobante journalière 2012-26, mois | +0,11 | **+0,09** (t = 2,2) |
| Cassure-retour, paire × mois | +0,34 | −0,06 |
| Suivi de tendance, paire × mois | +0,31 | +0,02 (reste perdant) |
| Lundi-mardi-mercredi | trop peu de trades (63 testés) | — |

Après coup, le filtre améliore toujours le résultat. En conditions réelles, l'amélioration disparaît presque partout. Les deux exceptions ne tiennent pas :

- **Les mois perdants de l'englobante journalière** aident en 2015-2020 et en 2021-2023. En 2024-2026, ce n'est plus le cas : les trades écartés font +0,18 R, contre +0,16 R pour les trades gardés.
- **Les jours perdants de l'englobante horaire** (entrée le mardi ou le vendredi) aident en 2025 et en 2026. Mais sur l'englobante journalière, l'entrée du mardi est l'une des meilleures depuis 2020 (+0,12 et +0,22 R).

Enfin, ce test compte 25 combinaisons (5 filtres × 5 stratégies). Sur 25 essais, il est normal que le hasard en fasse ressortir une ou deux avec t ≈ 2.
