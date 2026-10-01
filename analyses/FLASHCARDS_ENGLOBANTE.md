# Les flashcards « Naruto » : la stratégie de l'englobante vérifiée

> **Script** : [`scripts/tester_flashcards_englobante.py`](../scripts/tester_flashcards_englobante.py) → [`data/flashcards_englobante.csv`](../data/flashcards_englobante.csv).
> **Cartes** : copiées dans `assets/trades/2025-05/` à `2026-06/` (photos du canal citées ci-dessous).
> **Données de cours** : bougies horaires Yahoo Finance de janvier 2024 à septembre 2026, regroupées en bougies journalières de 22 h à 22 h UTC (clôture de New York), soit environ 700 jours par paire.

## 1. Ce que sont ces cartes

De mai 2025 à juin 2026, Amirou publie des **flashcards** illustrées de personnages de *Naruto* : Minato, Sakura, Pain, Sasuke, Naruto, Itachi, Jiraiya… Chaque carte résume les statistiques d'une stratégie sur une paire :

> « J'ai commencé à documenter les framework et stratégies que nous développons sur des flashcard » (#13305)
> « Chaque flashcard a les stats de sa strategie. La paire en question backtestée sur une periode de 10 ans minimum. La probabilité du setup, le jour optimal pour trader, le mois, la saison » (#13306)
> « Si les probabilité depassent 75%, je regarde le contexte fondamental. Si le context fondamental est aligné alors le trade devient un trade prenable et peut avoir une probabilité de plus de 90% » (#13415)

**La stratégie** : la carte AUDUSD (#14986) la nomme, ce sont les « configurations engloutissantes » (englobantes, *engulfing*) en journalier.
- **Englobante baissière** : une bougie baissière dont le corps recouvre celui de la bougie haussière de la veille.
- **Rupture** : la carte donne la probabilité que le **plus bas de l'englobante soit cassé dans les 3 jours** (pour une haussière, le plus haut). C'est ce qu'il annonce par exemple sur USDCAD : « 80% de chance de voir ce low pris demain » (#13342).
- Les cartes donnent aussi le jour de la rupture (« Jour 1 : 80-90 % ») et une variante « + FVG » (avec un *fair value gap*).

| Message | Date | Personnage | Paire | Baissier | Haussier |
|---|---|---|---|---|---|
| #13327 | 28/05/2025 | Minato | USDJPY | 70,97 % | 77,85 % |
| #13340 | 28/05/2025 | Sakura | EURNZD | 79,40 % | 73,53 % |
| #13343 | 29/05/2025 | Pain | USDCAD | 79,72 % | 83,40 % |
| #13355 | 02/06/2025 | Sasuke | XAUUSD | 76,02 % | 71,88 % |
| #13387 | 11/06/2025 | Naruto | GBPJPY | 74,7 % | 77,4 % |
| #13395 | 13/06/2025 | — | NZDUSD | 80,37 % | 82,46 % |
| #13409 | 24/06/2025 | Jiraiya (?) | AUDJPY | 81,0 % | 74,9 % |
| #13456, #13804 | 08/07 et 12/09/2025 | — | EURUSD | 78,79 % | 75,19 % |
| #13618 | 12/08/2025 | Itachi | GBPUSD | 76,80 % | 76,62 % |
| #14986 | 30/06/2026 | Sakura | AUDUSD | « 82 % des ruptures le jour 1 » | |

Deux autres images du même style (#13238, #13239, 01/05/2025) donnent les statistiques globales de « notre stratégie » : 76 % de réussite, 82,5 % le mercredi, mardi « à éviter », New York meilleure session (79,8 %).

Rappel : sur 16 cartes de chandeliers japonais du 08/04/2019 (#387 à #402), « Bullish/Bearish Engulfing » figure déjà parmi les figures enseignées. Ces anciennes cartes ne sont pas des flashcards Naruto.

## 2. Ses pourcentages sont exacts…

Configuration reconstruite sur 10 paires, de janvier 2024 à septembre 2026 :

| | Configurations | Rupture en 3 jours | dont dès le jour 1 |
|---|---|---|---|
| **Englobantes** (corps qui englobe celui de la veille) | 1 763 | **81,2 %** | 84 % |
| Englobantes strictes (mèches de la veille englobées aussi) | 449 | 80,2 % | 83 % |
| Moyenne annoncée sur les cartes | — | 77,3 % | 80-90 % |

Paire par paire, on retrouve ses ordres de grandeur, de 76 à 89 %. Les effets de jour qu'il décrit existent aussi :
- englobante baissière : le mercredi est le meilleur jour (83,1 % de rupture, contre 72 à 81 % les autres jours) ;
- englobante haussière : le lundi est le meilleur (88,1 %), comme sur la carte GBPJPY (#13387).

**Ses cartes ne sont pas inventées.**

## 3. …mais ils ne veulent pas dire ce qu'on croit

### Une bougie quelconque fait presque aussi bien
| | Configurations | Rupture en 3 jours |
|---|---|---|
| Englobantes | 1 763 | 81,2 % |
| **Toutes les bougies** (même couleur, sans condition) | 6 930 | **78,8 %** |

Après n'importe quelle bougie baissière, son plus bas est cassé dans les 3 jours près de 4 fois sur 5. C'est une propriété du marché : en 3 jours, le prix dépasse presque toujours l'extrême d'une bougie récente. L'englobante n'ajoute que 2 à 3 points.

### Un taux de rupture élevé n'est pas un trade gagnant
On transforme la rupture en trade, comme sur ses cartes :
- entrée à la clôture de l'englobante ;
- objectif : la cassure de l'extrême (+ 1 pip) ;
- stop : l'autre extrême de la bougie ;
- simulation heure par heure ; si objectif et stop tombent dans la même heure, on compte le stop ; spread déduit.

| | Trades | Gagnants | Gain moyen |
|---|---|---|---|
| Englobantes | 1 763 | **75,2 %** | **−0,02 R** |
| Englobantes strictes | 449 | 76,6 % | −0,01 R |
| Toutes les bougies | 6 930 | 68,7 % | −0,03 R |
| Englobante baissière un mercredi | 189 | — | +0,04 R |
| Englobante haussière un lundi | 185 | — | +0,06 R |

**Le trade gagne 3 fois sur 4 mais ne rapporte rien.** L'objectif est tout proche (médiane de 10 à 35 pips hors or : la clôture d'une englobante est près de son extrême) et le stop est loin (40 à 130 pips). Un gain moyen de 0,25-0,35 R trois fois sur quatre compense à peine une perte de 1 R une fois sur quatre. C'est la confusion classique entre **taux de réussite** et **espérance**.

Ce que les cartes ne disent pas :
- la probabilité de rupture n'est jamais comparée à celle d'une bougie quelconque ;
- elles ne disent pas où placer le stop, ni ce que rapporte la rupture face à ce qu'on risque.

## 3 bis. La variante « + FVG »

Trois de ses cartes donnent aussi un taux « + FVG » (*fair value gap*, un trou entre les mèches de trois bougies consécutives) :
- GBPJPY : 76,7 % baissier, 74,5 % haussier (#13387) ;
- AUDJPY : 81,7 % et 76,7 % (#13409) ;
- EURUSD : 81,6 % et 78,6 % (#13456, #13804).

C'est 1 à 3 points de plus que la version standard. Les cartes ne disent pas où se trouve le FVG ; trois définitions ont été testées :

| Définition du FVG | Quand est-il connu ? | Configurations | Rupture en 3 jours | Trades gagnants | Gain moyen |
|---|---|---|---|---|---|
| Aucun (englobante standard) | clôture de l'englobante | 1 763 | 81,2 % | 75,2 % | −0,02 R |
| **« Suivant »** : l'englobante est la bougie du milieu, le lendemain laisse un trou avec la veille | **clôture du lendemain** | 469 | **93,2 %** | 93,0 % | +0,14 R |
| ↳ même chose sans englobante (toute bougie suivie d'un FVG) | clôture du lendemain | 1 475 | 92,5 % | 91,9 % | +0,18 R |
| ↳ **trade pris quand le FVG est connu** (extrême pas encore cassé) | clôture du lendemain | 75 | **57,3 %** | — | **−0,02 R** |
| « Précédent » : l'englobante est la 3e bougie du FVG | clôture de l'englobante | 8 | 87,5 % | 75,0 % | −0,20 R |
| « Horaire » : un FVG en H1 pendant la journée de l'englobante | clôture de l'englobante | 1 544 | 81,1 % | 75,9 % | −0,01 R |

**Lecture** :
- **Le FVG « suivant » donne des chiffres spectaculaires, mais il triche.** Pour qu'un FVG se forme, la bougie du lendemain doit s'éloigner franchement : dans plus de 80 % des cas, elle casse déjà l'extrême de l'englobante (seules 75 configurations sur 469 restent intactes). On mesure donc la rupture après l'avoir vue se produire. N'importe quelle bougie suivie d'un FVG fait d'ailleurs aussi bien (92,5 %).
- **Au moment où le FVG est connu** (clôture du lendemain), il ne reste que 75 configurations sur 469 où l'extrême n'est pas encore cassé. La rupture n'y arrive plus que 57 fois sur 100, et le trade perd légèrement (−0,02 R).
- **Les deux définitions utilisables au moment de l'englobante** (FVG « précédent » ou FVG horaire) n'apportent rien. Le FVG horaire donne +0 point, ce qui est proche des +1 à 3 points de ses cartes : c'est probablement ce que mesure sa variante.

**Conclusion** : le « + FVG » n'améliore pas la stratégie. Soit il n'ajoute rien (FVG connu à temps), soit il ne peut pas être tradé (FVG connu trop tard).

## 4. Les trades qu'il a publiés avec ces cartes

Il ne trade pas la rupture telle quelle : il cherche une entrée (zone, session) et vise plus loin. Ce que montrent le canal et la simulation ([`data/trades_simules.csv`](../data/trades_simules.csv)) :

| Carte | Trade | Issue |
|---|---|---|
| USDJPY #13327 | « nous attendrons la session de New York » (#13328) | ❔ pas de niveaux publiés |
| EURNZD #13340 | « Le marché a coulé directement sans nous donner de point d'entrée » (#13338) | ⏸ non déclenché |
| USDCAD #13343 | vente 1.38352 (#13344) | ⏸ objectif atteint sans passer par l'entrée |
| XAUUSD #13355 | « Gold a touché mon sl avant de s'envoler » (#13352) | ❌ stop |
| GBPJPY #13387 | vente 196.200 (#13384), « Tp touché » (#13389) | ✅ objectif, mais capture publiée alors que l'entrée était déjà touchée (⚠️) |
| NZDUSD #13395 | achat 0.60307 (#13393) ; « l'analyse fondamentale va toujours primer » (#13396) | ❌ stop |
| AUDJPY #13409 | il déconseille l'achat, le fondamental étant contraire (#13412) ; « Le marché a tranché » (#13414) | ❔ niveaux incohérents avec le prix |
| EURUSD #13456 | vente à 1.17350 (#13455) | ❔ non rejoué |
| GBPUSD #13618 | vente 1.34473 (#13619) | ❌ stop |
| EURUSD #13804 | achat 1.17306 (#13808) | ❌ stop |
| AUDUSD #14986 | achat 0.69057 (#15005) | ✅ objectif (+2,1 R) |

**Bilan** : 2 objectifs (dont 1 publié après coup), 4 stops, 2 non déclenchés, 3 non vérifiables. Rien à voir avec les « 75 à 90 % » affichés.

Ses statistiques globales (76 % de réussite, 82,5 % le mercredi, #13239) ne correspondent pas non plus à ses trades annoncés à l'avance en 2023-2026 : 43 % d'objectifs atteints, 48 % le mercredi ([`TRADES_PAR_EPOQUE.md`](TRADES_PAR_EPOQUE.md)). Ces 76 % sont un taux de rupture de configuration, pas un taux de trades gagnants.

## 5. Conclusion

- Les flashcards décrivent un fait statistique **vrai** : le plus bas d'une englobante baissière est cassé dans les 3 jours environ 4 fois sur 5.
- Ce fait est **presque aussi vrai pour n'importe quelle bougie**, et **il ne se transforme pas en gain** : avec un stop à l'autre extrême, l'espérance est nulle, spread compris.
- Le passage de 75 % à « plus de 90 % » avec le fondamental (#13415) n'est pas étayé. Le test B de [`MODELE_FONDAMENTAL_ET_MLQ.md`](MODELE_FONDAMENTAL_ET_MLQ.md) montre que l'alignement fondamental n'améliore pas ses trades.
- Les effets du mercredi (baissier) et du lundi (haussier) se retrouvent, mais ils ajoutent moins de 0,1 R par trade.
- La variante « + FVG » n'aide pas : le FVG du lendemain voit la rupture avant de la « prédire », et les FVG connus à temps n'ajoutent rien (§ 3 bis).

### Limites
- 2 ans et 9 mois de données horaires, contre « 10 ans minimum » pour ses cartes. Les bougies journalières Yahoo plus anciennes ne sont pas fiables pour le Forex : ouverture fausse, plus hauts et plus bas trop étroits. Sur ces données, le taux de rupture tombe à 67 % pour les englobantes comme pour les bougies quelconques. La conclusion « l'englobante n'apporte rien » est donc la même.
- Le découpage des jours (22 h UTC) peut différer de celui de son courtier de quelques heures.
