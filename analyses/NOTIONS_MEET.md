# Les notions du Google Meet d'Amirou : explication, et ce qu'elles changent sur les cours

*17/10/2026 — notes du Meet transmises par l'utilisateur. Script : [`scripts/tester_notions_meet.py`](../scripts/tester_notions_meet.py) ; résultats : `data/notions_meet/stop_1r.csv` (stop élargi, objectif 1 R) et `data/notions_meet/macro.csv` (taux et VIX). Taux et VIX : FRED (`data/prix/fred_macro/`).*

## 1. Les notions, expliquées

| Notion | Ce que c'est | Déjà testé ? |
|---|---|---|
| **US10Y, US02Y** | Rendements des emprunts d'État américains à 10 et 2 ans. Le 2 ans suit les anticipations sur les taux de la Fed : s'il monte, le dollar est en général soutenu. L'écart 10 ans − 2 ans (la « pente ») renseigne sur la croissance attendue : une pente qui se creuse va souvent avec un dollar plus faible. | Oui, ci-dessous |
| **VIX** | Indice de la peur sur la Bourse américaine (volatilité attendue du S&P 500). Un VIX qui monte signale de l'aversion au risque : on achète le yen, le franc suisse et le dollar, on vend l'AUD, le NZD et le CAD. | Oui, ci-dessous |
| **Sentiment du marché** | Ce que les intervenants croient et comment ils sont positionnés : VIX, positions des fonds (COT), « risk on / risk off ». | COT : `analyses/MODELE_FONDAMENTAL_ET_MLQ.md`, `analyses/FOURCHETTE_CONFLUENCE.md` |
| **Liens des paires** | Les corrélations : EURUSD et GBPUSD montent souvent ensemble ; AUDJPY suit l'appétit pour le risque ; USDJPY suit le taux américain. Prendre trois trades corrélés revient à prendre trois fois le même risque. | Indirectement, ci-dessous (taux et VIX par paire) |
| **Mouvement climatique** | Un mouvement très rapide et très ample, souvent sur une nouvelle, qui épuise acheteurs ou vendeurs. On s'attend ensuite à un retournement (#15227). | Oui : `analyses/RETOURNEMENT.md` (pas d'avantage stable) |
| **Wyckoff** | Une lecture des phases du marché : accumulation (les gros achètent en range), hausse, distribution (ils vendent en range), baisse. Elle repose sur des événements nommés : « spring », faux cassage sous le range ; « upthrust », faux cassage au-dessus ; « test ». | En partie : le faux cassage est testé dans `analyses/ENGLOBANTE_MLQ_ET_SUIVI_TENDANCE.md` (« faux dépassement ») |
| **Structure du marché** | Une suite de plus hauts et de plus bas : hausse quand ils montent, baisse quand ils descendent. On parle de cassure de structure quand cette suite s'inverse. | Oui : suivi de tendance, `analyses/ENGLOBANTE_MLQ_ET_SUIVI_TENDANCE.md` |
| **Price action** | Lire les bougies elles-mêmes (englobante, pin bar, inside bar), sans indicateur. | Oui : englobante, retournement, flashcards |
| **Stop order** | Un ordre d'achat au-dessus du prix, ou de vente en dessous, exécuté seulement si le marché part dans le sens voulu. C'est une confirmation. | Oui : `analyses/ENGLOBANTE_FVG.md`, `analyses/ENTREES_LUNDI_MARDI_MERCREDI.md` (ne fait pas mieux que l'entrée à la clôture) |
| **Narratif** | L'histoire que le marché se raconte : « l'euro est faible à cause de l'énergie ». | Oui : `analyses/NARRATIF_ET_STRATEGIES.md`, et suivi en démo |
| **Momentum** | La tendance récente a tendance à continuer. | Oui : `analyses/AUTRES_ALGORITHMES.md`, suivi de tendance |
| **Préservation du capital** | Perdre moins et moins souvent, quitte à gagner moins par trade. | Oui, ci-dessous |

## 2. « Chercher 1 R avec plus de marge sur le stop »

Les signaux et l'entrée à la clôture ne changent pas. Le stop est éloigné (1 fois, 1,5 fois ou 2 fois la distance d'origine), et l'objectif est placé à 1 R du nouveau stop. La sortie au temps reste la même : clôture de J+3 pour l'englobante, clôture du vendredi pour lundi-mardi-mercredi. Le stop est prioritaire dans une même bougie, et le spread est déduit.

| Stratégie (sous-ensemble) | Variante | Gagnants | R moyen (± erreur type) | Pire série de pertes | Baisse max (R) |
|---|---|---|---|---|---|
| **Englobante + MLQ, achats, horaire 2024-2026** (387) | règle actuelle (2 R) | 51 % | **+0,15 ± 0,06** | 9 | 11,5 |
| | 1 R, stop x1 | 58 % | +0,11 ± 0,04 | 6 | **7,3** |
| | 1 R, stop x1,5 | 56 % | +0,05 ± 0,04 | 8 | 8,6 |
| | 1 R, stop x2 | 55 % | +0,04 ± 0,03 | 9 | 10,7 |
| **Englobante + MLQ, achats, journalier 2012-2026** (961) | règle actuelle (2 R) | 46 % | **+0,07 ± 0,04** | 11 | 34,9 |
| | 1 R, stop x1 | 51 % | +0,00 ± 0,03 | 7 | 42,5 |
| | 1 R, stop x1,5 | 53 % | +0,02 ± 0,03 | 8 | 34,9 |
| | 1 R, stop x2 | 52 % | +0,02 ± 0,02 | 8 | 36,3 |
| **Lundi-mardi-mercredi, avec filtre** (88) | règle actuelle (objectif au plus bas/haut du lundi) | 43 % | **+0,39 ± 0,19** | 10 | 13,6 |
| | 1 R, stop x1 | 53 % | +0,03 ± 0,11 | 6 | 8,6 |
| | 1 R, stop x1,5 | 47 % | −0,07 ± 0,10 | 10 | 15,7 |
| | 1 R, stop x2 | 46 % | −0,08 ± 0,10 | 10 | 15,7 |

- **Un stop plus large ne fait presque pas gagner plus souvent** : de 51-58 % à 1 R, contre 46-51 % à 2 R. Avec 1 R d'objectif, il faudrait plus de 50 % de réussite, frais compris, juste pour ne pas perdre.
- **On gagne moins par trade.** Sur lundi-mardi-mercredi, la stratégie tombe de +0,39 R à environ 0 : son avantage vient des trades qui vont loin (jusqu'au plus bas du lundi), et un objectif à 1 R les coupe.
- **La seule variante qui préserve mieux le capital** est l'englobante horaire avec 1 R et le stop **d'origine** : séries de pertes plus courtes (6 contre 9) et baisse maximale plus faible (7,3 R contre 11,5). Mais le gain moyen baisse un peu (+0,11 contre +0,15). Sur 2012-2026, cet avantage disparaît (+0,00).
- **Élargir le stop n'aide jamais** : à risque égal en argent, la position est plus petite, et les rares pertes coûtent autant.
- **Pour préserver le capital**, le levier efficace reste la **taille de position** : risquer 0,5 % au lieu de 2 % divise la baisse par quatre sans changer la stratégie. Les règles de sortie, elles, n'y changent presque rien.

## 3. Taux américains et VIX comme filtres

Chaque trade est classé selon ce que disaient les données **la veille** :
- **taux à 2 ans** : variation sur 5 jours ;
- **pente 10 ans − 2 ans** : variation sur 5 jours ;
- **VIX** : variation sur 5 jours, et régime de stress quand il dépasse 25.

« Dans le sens » veut dire, par exemple, acheter le dollar quand le 2 ans monte, ou acheter le yen quand le VIX monte.

**Le taux à 2 ans, sur l'englobante (règle actuelle, toutes paires avec dollar)** :

| Période | Dans le sens | Contre |
|---|---|---|
| 2012-2015 | −0,01 R (343) | +0,03 R (356) |
| 2016-2019 | +0,03 R (465) | +0,02 R (524) |
| 2020-2023 | −0,06 R (473) | +0,02 R (534) |
| **2024-2026** | **+0,13 R** (390) | **−0,15 R** (444) |

En horaire 2024-2026, on retrouve le même effet : +0,10 R dans le sens, −0,15 R contre. Sur lundi-mardi-mercredi : +0,38 R dans le sens, +0,10 R contre, mais sur seulement 50 et 78 trades.

- **Depuis 2024, suivre le taux à 2 ans aurait nettement aidé**, avec un écart d'environ 0,25 R par trade. Avant 2024, **aucun effet**, ou même l'inverse. C'est un effet de période, lié à un marché des changes dominé par les anticipations sur la Fed, pas une règle stable : il peut s'arrêter à tout moment.
- **La pente 10 ans − 2 ans et le VIX n'apportent rien** de stable : écarts faibles, de signe changeant, échantillons petits pour le VIX.
- **Le régime de stress (VIX > 25)** ne change rien sur l'englobante. Sur lundi-mardi-mercredi, il y a trop peu de cas (18).

## 4. « Trade intéressant sur l'AUD et la GBP la semaine prochaine »
Je ne peux pas prévoir la semaine à venir. Voici en revanche ce que montrent ses trades annoncés passés depuis 2023, rejoués sur les cours :

| Devise | Trades | Gagnants | R moyen |
|---|---|---|---|
| AUD | 66 | 48 % | +0,61 ± 0,24 |
| GBP | 55 | 33 % | +0,17 ± 0,25 |

Ses trades sur l'AUD ont été plutôt meilleurs que la moyenne, ceux sur la GBP moins bons. Les échantillons restent petits. Si ses idées sur l'AUD et la GBP sont publiées dans le canal, elles seront vérifiées avec `scripts/verifier_octobre_2026.py`, comme les autres trades.

## 5. En résumé
- **Stop plus large et 1 R** : pas d'amélioration. On gagne un peu plus souvent, mais on gagne moins, et lundi-mardi-mercredi perd l'essentiel de son avantage. Pour préserver le capital, mieux vaut réduire la taille de position.
- **US02Y** : la seule notion qui aide, mais **seulement depuis 2024**. À suivre à côté du suivi en démo, comme le narratif, sans en faire une règle.
- **US10Y-US02Y, VIX, sentiment** : rien de stable.
- **Wyckoff, mouvement climatique, structure, price action, stop order, momentum, narratif** : déjà traduits en règles et testés, sans avantage stable.
