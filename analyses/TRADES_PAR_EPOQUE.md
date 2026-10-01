# Les trades d'Amirou, époque par époque : 2021-2022 et 2023-2026

> **Script** : [`scripts/analyse_par_epoque.py`](../scripts/analyse_par_epoque.py) (tous les chiffres ci-dessous se recalculent avec lui).
> **Données** : 518 captures lues par OCR et rejouées sur les cours ([`data/trades_simules.csv`](../data/trades_simules.csv)), contexte au moment de la publication ([`data/meta_features.csv`](../data/meta_features.csv)), indicateurs fondamentaux ([`data/fondamental/indicateurs.csv`](../data/fondamental/indicateurs.csv)). Résultat ligne à ligne : [`data/epoques_trades.csv`](../data/epoques_trades.csv).
> **R net** : résultat en multiples du risque, spread déduit. « Hors ratios > 8 » retire les trades à objectif extrême (1:10 à 1:23), qui faussent les moyennes de 2021.

Pourquoi séparer : Amirou a changé de méthode (voir [`MODELE_FONDAMENTAL_ET_MLQ.md`](MODELE_FONDAMENTAL_ET_MLQ.md), § 6).
- **2021-2022** : Wyckoff, smart money, quarter points ; entrées « sniper » avec des stops de quelques pips et des ratios de 1:7 à 1:20.
- **2023-2026** : analyse fondamentale et sentiment d'abord (« fondamentale 40 %, sentiment 25 %, technique 25 %, price action 10 % », #15478), MLQ, stops de 40-50 pips, ratios de 1:2 à 1:3.

Mélanger les deux revient à mesurer une stratégie qui n'a jamais existé.

## 1. Vue d'ensemble

### Ce qui est publié
| Époque | Captures lues | Annoncées à l'avance | ↳ objectif | ↳ stop | ↳ jamais déclenchées | Publiées après coup | dont objectif déjà dépassé | Lecture incohérente |
|---|---|---|---|---|---|---|---|---|
| 2021-2022 | 173 | 120 | 33 | 58 | 29 (24 %) | 27 (16 %) | 17 | 26 |
| 2023-2026 | 345 | 230 | 66 | 89 | 73 (32 %) | **99 (29 %)** | 9 | 16 |

- **Les publications après coup doublent** (16 % → 29 %). Elles gagnent 70 % du temps dans les deux époques, contre 36-43 % pour les trades annoncés à l'avance : c'est l'effet vitrine.
- **Un trade annoncé sur trois ne se déclenche pas** en 2023-2026 (ordres limites jamais atteints, ou objectif atteint sans passer par l'entrée). Copier ses signaux suppose d'exécuter exactement son ordre, pas d'entrer au marché.

### Performance des trades annoncés et terminés
| | 2021-2022 | 2023-2026 |
|---|---|---|
| Trades | 91 | 155 |
| Gagnants | 36 % | 43 % |
| Stop médian | 13 pips | 43 pips |
| Ratio médian | 1:8,4 | 1:2,7 |
| R net moyen | +2,03 R | +0,43 R |
| **R net hors ratios > 8** | **+0,36 R** | **+0,50 R** |
| Plus longue série de stops | **14** | 8 |
| Pire baisse du compte, à 1 % de risque | 17 % | 9 % |
| … à 2 % de risque | 31 % | 17 % |
| Stops passés d'abord par +1 R de gain | 10 sur 58 | **36 sur 89** |
| R net avec la règle « BE à 1 R » | +2,14 R | **+0,66 R** |

| Année | Trades | Gagnants | R net | hors ratios > 8 |
|---|---|---|---|---|
| 2021 | 58 | 40 % | +2,79 R | +0,15 R |
| 2022 | 33 | 30 % | +0,69 R | +0,60 R |
| 2023 | 60 | 43 % | +0,80 R | +0,93 R |
| 2024 | 28 | 32 % | −0,09 R | −0,05 R |
| 2025 | 36 | 44 % | +0,40 R | +0,44 R |
| 2026 | 31 | 48 % | +0,22 R | +0,26 R |

**Lecture** :
- **2021-2022 : une loterie à gros lots.** Le +2,03 R moyen tient à une poignée de trades à 1:10-1:23 : sans eux, il reste +0,36 R. Deux trades sur trois perdent, la série de 14 stops d'affilée et la baisse de 31 % du compte (à 2 % de risque) le rendaient très dur à suivre.
- **2023-2026 : plus régulier, pas plus rentable.** Hors gros lots, l'espérance est comparable (+0,50 R contre +0,36 R ; l'écart n'est pas significatif, p = 0,06). Mais le parcours est deux fois moins violent (série max de 8 stops, baisse max de 9 % à 1 %).
- **Le BE compte surtout en 2023-2026** : 36 des 89 stops (40 %) avaient d'abord été à +1 R. Avec la règle « stop à l'entrée à +1 R » qu'il recommande (#1196, #15407), l'espérance passe de +0,43 à +0,66 R. En 2021-2022, les stops serrés étaient touchés trop vite pour que le BE serve (10 sur 58).
- 2024 est la seule année perdante, et c'est aussi celle où les publications après coup bondissent (36 %).

## 2. 2021-2022 : ce qui marchait et ce qui ne marchait pas (91 trades)

| Facteur | Constat | Fiabilité |
|---|---|---|
| **Mardi** | 1 gagnant sur 12 (8 %), −1,17 R hors gros lots | Significatif (p = 0,05) mais 12 trades |
| Mercredi | 48 % gagnants, +0,60 R hors gros lots | Non significatif (p = 0,15) |
| Vendredi | 42 %, +1,10 R hors gros lots | 19 trades |
| Jeudi | 24 %, −0,22 R hors gros lots | 21 trades |
| Achats / ventes | 45 % contre 27 % | — |
| Ratio < 2,5 | 48 % gagnants mais −0,06 R : les petits ratios ne payaient pas | 21 trades |
| Stop ≥ 60 pips | 1 sur 7 | Rare à l'époque |
| Distance au MLQ | Aucun effet (36-37 % partout) | — |
| Tendance 20 j | Contre la tendance un peu mieux (39 % contre 33 %) | Non significatif |
| Saisonnalité | Dans le sens : +0,75 R hors gros lots ; contre : −0,17 R | Non significatif, et nul en 2023-2026 |
| Paires | NZDUSD et EURJPY bons (56 %), USDJPY mauvais (1 sur 7), EURUSD −1,13 R hors gros lots | 7 à 13 trades par paire |
| Fondamentaux | Aller **contre** le différentiel de taux (43 % contre 31 %) ou le positionnement COT (46 % contre 34 %) faisait mieux | Style contrarien de l'époque |

**En résumé** : une méthode technique de retournement, rentable uniquement par ses rares très gros gains. Les jours (mercredi, vendredi) comptaient plus que les niveaux.

## 3. 2023-2026 : ce qui marche et ce qui ne marche pas (155 trades)

| Facteur | Constat | Fiabilité |
|---|---|---|
| **Entrée à moins de 25 pips d'un MLQ** | **49 % gagnants, +0,91 R** hors gros lots, contre 39-41 % et +0,30 à +0,38 R plus loin | R significatif (p = 0,04), taux de réussite non (p = 0,37) |
| **Stop de 15 à 30 pips** | **26 %, −0,09 R** : quand il revient à un stop serré, il perd | Significatif (p < 0,01), 27 trades |
| Stop de 30 à 60 pips (sa norme) | 41 %, +0,57 R | 85 trades |
| Stop ≥ 60 pips | 58 %, +0,44 R | 38 trades |
| **GBPUSD** | **1 gagnant sur 14**, −0,70 R | Significatif (p < 0,01) |
| AUDJPY | 64 %, +0,90 R | 14 trades, p = 0,10 |
| EURAUD | 25 %, −0,26 R | 12 trades |
| Mercredi | 48 %, +0,57 R (meilleur taux de réussite) | Non significatif (p = 0,47) |
| Jeudi | 39 %, mais +0,82 R | — |
| Lundi | 8 trades seulement : il ne trade presque plus le lundi | — |
| Publié la nuit ou à Londres (avant 12 h UTC) | 45-48 %, +0,66 à +0,73 R ; New York et soir : 35-39 %, +0,25 à +0,29 R | Non significatif (p = 0,33) |
| Ratio < 2,5 | 58 % gagnants, +0,41 R | 71 trades |
| Ratio > 8 | 0 sur 7 : les gros ratios ne marchent plus | — |
| Achats / ventes | Identiques (43 % / 42 %) | — |
| Tendance 20 j, saisonnalité | Aucun effet | — |
| COT variation 4 sem. dans le sens du trade | 47 %, +0,67 R contre 39 %, +0,22 R | Non significatif (p = 0,16) |
| Surprises économiques, différentiel de taux | Aucun effet, un peu mieux à contre-courant | — |
| Son propre biais écrit (14 j) | Trades **contre** ce qu'il a écrit : +0,80 R ; dans le sens : +0,40 R | 34 trades |

**En résumé** : depuis 2023, son meilleur profil est un **trade près d'un MLQ, avec un stop « normal » de 30 à 60 pips, publié avant l'ouverture de New York**, et en évitant GBPUSD. Le mercredi a le meilleur taux de réussite, mais l'écart avec les autres jours est faible.

**Attention aux faux positifs** : une trentaine de découpages ont été testés par époque. À p = 0,05, on s'attend à 1 ou 2 « découvertes » par hasard. Seuls le MLQ, les stops de 15-30 pips et GBPUSD en 2023-2026 (et le mardi en 2021-2022) passent ce seuil. Ce sont des pistes à vérifier sur ses prochains trades, pas des règles établies.

## 4. Ce qui a changé d'une époque à l'autre

| | 2021-2022 | 2023-2026 |
|---|---|---|
| Source du gain | Quelques trades à 1:10-1:23 | Beaucoup de petits gains à 1:2-1:3 |
| Meilleur jour | Mercredi et vendredi (mardi catastrophique) | Mercredi (taux), jeudi (R) ; plus aucun jour catastrophique |
| MLQ | Aucun effet | Seul facteur avec un effet net |
| Heure | Soir et New York (47 % de ses trades publiés à New York) | Nuit et Londres meilleurs |
| Petits ratios (< 2,5) | Ne paient pas (−0,06 R) | Paient (+0,41 R, 58 % de réussite) |
| Fondamentaux | Contrarien (contre taux et COT) | Neutres ; seule la dynamique du COT aide un peu |
| BE à 1 R | Utile à la marge | +0,23 R par trade |
| Séries de pertes | Jusqu'à 14 | Jusqu'à 8 |
| Publications après coup | 16 % | 29 % |

Le registre texte du canal (messages « TP », « SL », « BE ») confirme la tendance : 2023-2026 compte 25 BE pour 9 TP et 11 SL, signe que la gestion par le BE est devenue centrale.

| Époque | Trades du registre | TP | SL | BE | Ratés | Gain flottant | Inconnue | Réussite (TP / TP + SL) |
|---|---|---|---|---|---|---|---|---|
| 2019-2020 | 192 | 12 | 22 | 22 | 24 | 18 | 94 | 35 % |
| 2021-2022 | 22 | 3 | 3 | 5 | 6 | 1 | 4 | 50 % |
| 2023-2026 | 67 | 9 | 11 | 25 | 14 | 2 | 6 | 45 % |

## 5. Un modèle d'IA par époque fait-il mieux ?

Même modèle (régression logistique sur le contexte + les fondamentaux), entraîné soit sur la seule époque en cours, soit sur tout l'historique, puis testé sur l'année suivante :

| Année testée | Entraîné sur | Trades testés | AUC | R net, moitié retenue | R net, moitié écartée |
|---|---|---|---|---|---|
| 2022 | 2021 seule | 33 | 0,45 | +0,08 R | +1,33 R |
| 2024 | 2023 seule | 28 | 0,48 | −0,23 R | +0,06 R |
| 2024 | 2021-2023 mélangées | 28 | 0,52 | +0,28 R | −0,45 R |
| 2025 | 2023-2024 | 36 | 0,48 | +0,19 R | +0,60 R |
| 2025 | 2021-2024 mélangées | 36 | 0,27 | −0,44 R | +1,23 R |
| 2026 | 2023-2025 | 31 | **0,65** | +0,27 R | +0,17 R |
| 2026 | 2021-2025 mélangées | 31 | 0,60 | +0,42 R | +0,01 R |

- Séparer les époques ne suffit pas : avec 28 à 60 trades par an, le modèle n'a pas assez d'exemples. Les AUC sautent de 0,27 à 0,65 d'une année à l'autre, ce qui est du bruit.
- Le seul résultat encourageant est 2026 (AUC 0,65 en n'apprenant que sur 2023-2025), mais sur 31 trades.
- Il faudra attendre une ou deux années de trades supplémentaires dans le style actuel pour qu'un modèle propre à 2023-2026 soit testable sérieusement.

## 6. Conclusions pratiques

1. **Ne jamais juger Amirou sur l'ensemble 2021-2026** : les deux époques n'ont ni le même risque, ni la même source de gain.
2. **Style 2021-2022** : espérance positive hors gros lots (+0,36 R), mais seulement supportable avec un risque très faible (série de 14 stops).
3. **Style 2023-2026** : espérance de +0,50 R hors gros lots, +0,66 R avec le BE à 1 R. C'est le style à suivre si l'on copie ses signaux aujourd'hui, en exécutant exactement ses ordres limites.
4. **Filtres à surveiller sur ses prochains trades** (pas encore des règles) :
   - privilégier les entrées près d'un MLQ ;
   - se méfier des trades à stop serré (15-30 pips), qui sortent de son style actuel ;
   - se méfier de GBPUSD ;
   - préférer les publications d'avant l'ouverture de New York.
5. **Ne pas tenir compte des captures publiées après coup** : 29 % de ce qui est montré depuis 2023, avec 70 % de réussite, ce qui gonfle l'image du canal.

## Annexe : tableaux complets par époque

Hors ratios > 8 = espérance en retirant les trades à objectif extrême.

### Découpages 2021-2022 (91 trades)

**Jour de déclenchement**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| lundi | 12 | 50 % | +3,65 R | +0,92 R |
| mardi | 12 | 8 % | -0,21 R | -1,17 R |
| mercredi | 27 | 48 % | +2,76 R | +0,60 R |
| jeudi | 21 | 24 % | +0,83 R | -0,22 R |
| vendredi | 19 | 42 % | +2,69 R | +1,10 R |

**Heure de publication (UTC)**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| nuit / Asie (0-7 h) | 14 | 14 % | -0,48 R | +0,39 R |
| Londres (7-12 h) | 5 | 60 % | +2,00 R | +2,03 R |
| New York (12-17 h) | 43 | 35 % | +1,80 R | +0,35 R |
| soir (17-24 h) | 29 | 45 % | +3,57 R | -0,01 R |

**Paires (5 plus tradées)**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| EURUSD | 13 | 31 % | +3,70 R | -1,13 R |
| AUDUSD | 12 | 42 % | +0,04 R | +0,73 R |
| NZDUSD | 9 | 56 % | +2,52 R | +1,96 R |
| EURJPY | 9 | 56 % | +5,11 R | +0,98 R |
| USDJPY | 7 | 14 % | +0,18 R | -1,03 R |
| autres | 41 | 32 % | +1,61 R | +0,14 R |

**Sens**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| achat | 47 | 45 % | +2,40 R | +0,42 R |
| vente | 44 | 27 % | +1,62 R | +0,29 R |

**Ratio annoncé**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| moins de 2,5 | 21 | 48 % | -0,06 R | -0,06 R |
| 2,5 à 5 | 12 | 42 % | +0,56 R | +0,56 R |
| 5 à 8 | 10 | 30 % | +1,00 R | +1,00 R |
| plus de 8 | 48 | 31 % | +3,52 R | — |

**Taille du stop**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| moins de 15 pips | 53 | 34 % | +3,32 R | +0,73 R |
| 15 à 30 | 20 | 35 % | +0,49 R | +0,48 R |
| 30 à 60 | 11 | 64 % | +0,44 R | +0,44 R |
| 60 et plus | 7 | 14 % | -0,89 R | -0,80 R |

**Distance au MLQ (niveau de 250 pips)**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| moins de 25 pips | 28 | 36 % | +1,44 R | +0,43 R |
| 25 à 75 | 30 | 37 % | +2,34 R | +0,55 R |
| plus de 75 | 33 | 36 % | +2,24 R | -0,01 R |

**Tendance 20 jours**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| dans la tendance | 42 | 33 % | +1,45 R | +0,30 R |
| contre | 49 | 39 % | +2,52 R | +0,45 R |

**Saisonnalité (10 ans avant)**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| dans le sens | 52 | 40 % | +1,75 R | +0,75 R |
| contre | 39 | 31 % | +2,40 R | -0,17 R |

**Fondamentaux au moment de la publication**

| Indicateur | Dans le sens | Contre |
|---|---|---|
| Surprises économiques 30 j | 39 : 33 %, +1,90 R | 49 : 41 %, +2,32 R |
| Différentiel de taux | 36 : 31 %, +1,58 R | 51 : 43 %, +2,60 R |
| Variation des taux 90 j | 10 : 50 %, +2,44 R | 22 : 36 %, +2,01 R |
| COT (niveau) | 35 : 34 %, +1,70 R | 35 : 46 %, +2,96 R |
| COT (variation 4 sem.) | 35 : 43 %, +2,20 R | 35 : 37 %, +2,46 R |
| Son biais écrit (14 j) | 18 : 33 %, +2,39 R | 15 : 20 %, +1,06 R |

### Découpages 2023-2026 (155 trades)

**Jour de déclenchement**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| lundi | 8 | 38 % | +0,07 R | +0,22 R |
| mardi | 44 | 41 % | +0,27 R | +0,30 R |
| mercredi | 42 | 48 % | +0,53 R | +0,57 R |
| jeudi | 28 | 39 % | +0,62 R | +0,82 R |
| vendredi | 33 | 42 % | +0,45 R | +0,49 R |

**Heure de publication (UTC)**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| nuit / Asie (0-7 h) | 46 | 48 % | +0,55 R | +0,66 R |
| Londres (7-12 h) | 40 | 45 % | +0,60 R | +0,73 R |
| New York (12-17 h) | 46 | 39 % | +0,26 R | +0,29 R |
| soir (17-24 h) | 23 | 35 % | +0,25 R | +0,25 R |

**Paires (5 plus tradées)**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| EURUSD | 25 | 40 % | +0,32 R | +0,44 R |
| GBPUSD | 14 | 7 % | -0,72 R | -0,70 R |
| AUDJPY | 14 | 64 % | +0,76 R | +0,90 R |
| EURAUD | 12 | 25 % | -0,26 R | -0,26 R |
| GBPJPY | 11 | 27 % | -0,07 R | +0,03 R |
| autres | 79 | 51 % | +0,79 R | +0,84 R |

**Sens**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| achat | 84 | 43 % | +0,40 R | +0,47 R |
| vente | 71 | 42 % | +0,47 R | +0,54 R |

**Ratio annoncé**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| moins de 2,5 | 71 | 58 % | +0,41 R | +0,41 R |
| 2,5 à 5 | 66 | 30 % | +0,33 R | +0,33 R |
| 5 à 8 | 11 | 45 % | +2,10 R | +2,10 R |
| plus de 8 | 7 | 0 % | -1,07 R | — |

**Taille du stop**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| moins de 15 pips | 5 | 40 % | +1,69 R | +5,86 R |
| 15 à 30 | 27 | 26 % | -0,20 R | -0,09 R |
| 30 à 60 | 85 | 41 % | +0,55 R | +0,57 R |
| 60 et plus | 38 | 58 % | +0,44 R | +0,44 R |

**Distance au MLQ (niveau de 250 pips)**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| moins de 25 pips | 45 | 49 % | +0,78 R | +0,91 R |
| 25 à 75 | 54 | 39 % | +0,25 R | +0,30 R |
| plus de 75 | 56 | 41 % | +0,32 R | +0,38 R |

**Tendance 20 jours**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| dans la tendance | 83 | 41 % | +0,45 R | +0,52 R |
| contre | 72 | 44 % | +0,41 R | +0,48 R |

**Saisonnalité (10 ans avant)**

| | Trades | Gagnants | R net | R net hors ratios > 8 |
|---|---|---|---|---|
| dans le sens | 75 | 41 % | +0,38 R | +0,47 R |
| contre | 80 | 44 % | +0,47 R | +0,53 R |

**Fondamentaux au moment de la publication**

| Indicateur | Dans le sens | Contre |
|---|---|---|
| Surprises économiques 30 j | 86 : 43 %, +0,33 R | 69 : 42 %, +0,55 R |
| Différentiel de taux | 93 : 43 %, +0,38 R | 61 : 43 %, +0,53 R |
| Variation des taux 90 j | 71 : 41 %, +0,57 R | 35 : 43 %, +0,28 R |
| COT (niveau) | 93 : 42 %, +0,38 R | 62 : 44 %, +0,50 R |
| COT (variation 4 sem.) | 72 : 47 %, +0,67 R | 83 : 39 %, +0,22 R |
| Son biais écrit (14 j) | 69 : 42 %, +0,40 R | 34 : 44 %, +0,80 R |

