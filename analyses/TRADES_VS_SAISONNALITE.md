# Les trades d'Amirou face à la saisonnalité et au contexte macro (2019 – 2026)

> **Question posée** : les trades du canal ont-ils suivi la saisonnalité ? Pourquoi certains ont-ils échoué ? Et quels mois n'ont pas respecté leur saisonnalité, pour quelles raisons ?
> **Fichiers** : [`data/trades.csv`](../data/trades.csv) (registre), [`data/trades_saisonnalite.csv`](../data/trades_saisonnalite.csv) (confrontation), [`data/mois_hors_saisonnalite.csv`](../data/mois_hors_saisonnalite.csv) (mois atypiques), [`data/saisonnalite.csv`](../data/saisonnalite.csv) et [`data/rendements_mensuels.csv`](../data/rendements_mensuels.csv) (cours).

## 1. Méthode

| Étape | Script | Ce qu'il fait |
|---|---|---|
| Cours | [`scripts/saisonnalite_mensuelle.py`](../scripts/saisonnalite_mensuelle.py) | Cours quotidiens de la Fed (H.10, [datasets/exchange-rates](https://github.com/datasets/exchange-rates)) jusqu'au 25/09/2026 ; 28 paires reconstituées et l'or (moyenne mensuelle). Rendement mensuel = clôture du mois / clôture du mois précédent |
| Registre | [`scripts/construire_registre_trades.py`](../scripts/construire_registre_trades.py) | Relie chaque annonce d'entrée à ses issues (TP, SL, BE, raté) par paire et par réponse ; 32 corrections manuelles dans [`data/trades_corrections.csv`](../data/trades_corrections.csv) |
| Confrontation | [`scripts/confronter_trades_saisonnalite.py`](../scripts/confronter_trades_saisonnalite.py) | Biais saisonnier **ex ante** (10 années précédant le trade, donc ce qu'on pouvait savoir à l'époque), mouvement réel du mois, cause des stops touchés |

- **Biais saisonnier** : un mois est « haussier » si au moins 2 années sur 3 ont été positives et la moyenne est positive ; « baissier » dans le cas inverse ; sinon « neutre ».
- **Écart avec les PDF du projet** : les PDF utilisent les clôtures Yahoo Finance ; ici, ce sont les fixings de midi à New York. Les moyennes sont proches (EURUSD septembre 2020-2025 : −1,31 % ici contre −1,11 % dans le PDF), mais un mois proche de zéro peut changer de signe.
- **Limites du registre** :
  - 281 trades retrouvés, dont 60 seulement ont une issue décisive (TP ou SL) avec un sens connu ;
  - à partir de 2021, les trades sont surtout montrés en image ou réservés aux groupes payants, donc le registre automatique les sous-estime ;
  - les septembres vérifiés à la main dans [`TRADES_SEPTEMBRE.md`](TRADES_SEPTEMBRE.md) font foi en cas d'écart.

## 2. Vue d'ensemble des trades

| Année | Trades | TP / gain | SL | BE | Non déclenchés | Issue inconnue ou flottante |
|---|---|---|---|---|---|---|
| 2019 | 85 | 7 | 15 | 12 | 3 | 48 |
| 2020 | 107 | 5 | 7 | 10 | 21 | 64 |
| 2021 | 13 | 1 | 1 | 4 | 3 | 4 |
| 2022 | 9 | 2 | 2 | 1 | 3 | 1 |
| 2023 | 11 | 0 | 2 | 0 | 6 | 3 |
| 2024 | 11 | 0 | 5 | 1 | 5 | 0 |
| 2025 | 17 | 3 | 2 | 7 | 3 | 2 |
| 2026 | 28 | 6 | 2 | 17 | 0 | 3 |
| **Total** | **281** | **24** | **36** | **52** | **44** | **125** |

- **Taux de réussite sur les issues annoncées : 40 %** (24 TP ou gains contre 36 SL).
  - 2019-2020, quand les signaux étaient donnés en direct avec leur suivi : 35 %.
  - 2021-2026 : 46 %. Cette hausse s'explique surtout par un changement de présentation : le canal public montre désormais surtout les résultats.
- **Biais vendeur** : 145 ventes pour 84 achats.
- **Paires les plus tradées** : EURUSD (29), GBPUSD (24), GBPJPY (17), EURJPY (16), EURNZD (15), GBPAUD (14).
- **Le BE est l'issue la plus fréquente** depuis 2025 (24 sur 45 trades) : la règle « mettez-vous à BE » est appliquée très tôt.

## 3. Les trades ont-ils suivi la saisonnalité ?

| Critère | Trades (tous) | TP / gains | SL | Taux de réussite (TP ÷ TP+SL) |
|---|---|---|---|---|
| Sens **avec** un biais saisonnier net (ex ante) | 32 | 1 | 2 | 33 % |
| Sens **contre** un biais saisonnier net | 39 | 4 | 3 | 57 % |
| Mois **sans** biais saisonnier net | 157 | 13 | 24 | 35 % |
| Sens avec la moyenne 10 ans (critère souple) | 108 | 9 | 14 | 39 % |
| Sens contre la moyenne 10 ans | 120 | 9 | 15 | 38 % |
| Sens **avec** le mouvement réel du mois | 122 | 10 | 16 | 38 % |
| Sens **contre** le mouvement réel du mois | 104 | 8 | 12 | 40 % |

**Conclusions :**
1. **La saisonnalité n'explique pas les résultats des trades.**
   - La plupart des trades sont pris des mois sans biais saisonnier net. Avec le critère souple, le taux de réussite est le même dans le sens de la saison et contre elle (39 % contre 38 %).
   - Les échantillons « biais net » (3 et 7 issues décisives) sont trop petits pour conclure.
2. **Même la direction réelle du mois ne fait pas la différence** (38 % contre 40 %). Les trades sont des opérations de quelques heures à quelques jours, avec des stops courts : ils se jouent sur l'entrée et sur l'annonce économique du jour, pas sur la tendance du mois.
3. **Amirou ne parle de saisonnalité qu'à partir de mars 2023** (#7762 : « Aujourd'hui je vous introduis à la saisonnalité »). Ses messages sur le sujet, 31 au total, datent tous de 2023 à 2026. Sur 2019-2022, il ne s'en sert pas.

## 4. Les affirmations saisonnières d'Amirou, vérifiées

| Message | Mois | Affirmation | Ce que disent les 10 années précédentes | Mois réel | Verdict |
|---|---|---|---|---|---|
| #8591 #8592 | 07/2023 | « Dollar baissier en juillet sur 20 ans » | EURUSD juillet : 57 % haussier, +0,64 % (14 ans) | EURUSD +0,93 % | ✅ (statistique faible mais juste) |
| #9817 | 11/2023 | AUDJPY haussier en novembre | 60 %, +0,99 % | +1,98 % | ✅ |
| #9783 #10073 | 12/2023 | Ne pas vendre EURUSD en décembre ; DXY baissier | 80 % haussier, +1,15 % | +1,42 % | ✅ |
| #10892 #10946 | 04/2024 | EURUSD haussier en avril | 60 %, +0,29 % | **−0,99 %** | ❌ Amirou le reconnaît lui-même (CPI US trop fort) |
| #11946 | 09/2024 | EURUSD « très baissier » en septembre | 20 % haussier, −1,36 % | **+0,77 %** | ❌ (baisse de taux de 50 pb de la Fed le 18/09) |
| #13180 | 04/2025 | AUDJPY haussier en avril | 70 %, +0,78 % | **−2,36 %** | ❌ (droits de douane du « Liberation Day », 02/04) |
| #14662 | 04/2026 | AUDJPY haussier en avril | 60 %, +0,23 % | +3,21 % | ✅ (cessez-le-feu avec l'Iran le 07/04) |
| #14815 | 05/2026 | EURUSD « très très baissier » en mai | **50 %, −0,06 % : aucun biais** | −0,42 % | ⚠️ Bonne direction, mais la statistique invoquée n'existe pas ; le PDF du projet donne même mai **haussier** |
| #14907 | 06/2026 | EURJPY « très haussier » en juin | 83 % (6 ans), +2,19 % | **−0,17 %** | ❌ (et non « plein profit » comme l'écrivait Antigravity) |
| #15204 | 08/2026 | « Saisonnalité haussière du dollar » en août | 40 %, +0,02 % : **aucun biais** | Dollar en baisse (EURUSD +0,85 %) | ❌ Affirmation non fondée, démentie |
| #15269 | 09/2026 | Dollar haussier en septembre | 40 % haussier, −0,82 % | EURUSD −1,87 % | ✅ |

**Bilan** : 6 prévisions justes sur 11.
- Les biais invoqués sont souvent réels mais **faibles** : 57 à 70 % de mois favorables, quand Amirou parle de « 20 ans » ou de « très très baissier ».
- Deux affirmations (mai et août 2026) ne correspondent à **aucune** statistique.
- Les échecs ont tous une cause macro identifiable qui a dominé la saison (section 6).

## 5. Pourquoi les trades ont échoué

Les 36 stops touchés, classés d'après ce que dit le canal dans les 2 jours autour de chaque SL :

| Cause | SL | Exemples |
|---|---|---|
| **Stop serré ou chasse aux stops** (« de justesse », « quelques pips », spread, « est allé dans notre sens ensuite ») | 12 | NZDCHF 06/2019 (#1015) ; USDCHF 09/2019 (#1285) ; EURAUD juin 2024, sorti trois fois de justesse (#11390, #11405, #11427) ; or 06/2025 (#13352) ; USDJPY 01/10/2026 (#15505), puis TP dépassé |
| **Annonce économique** (NFP, CPI, banque centrale) | 10 | AUDUSD 05/2019 (« à cause de l'annonce sur le dollar », #933) ; trois trades le 24/09/2019 (« annonce économique et nos 3 trades ont touché SL », #1251) ; AUDUSD 03/2023 pendant la crise SVB (#7718) ; EURCAD 03/2026 sur un ton restrictif inattendu de la BCE (#14611) |
| **Non expliquée** dans le canal | 14 | Série de février 2020 (GBPCHF, NZDCAD, CHFJPY), en plein début de la crise COVID ; AUDJPY 09/2022 (#6427) ; GBPJPY 01/2024 (#10363 : « j'avais même oublié ce trade ») |

**Ce que montrent les données :**
- **Septembre 2019, le cas d'école.** Huit ventes sur des paires en yen et contre le dollar ont été prises alors que le yen et le dollar s'affaiblissaient tout le mois. GBPJPY a fait +2,9 %, CADJPY +2,1 %, USDJPY +1,7 %. Contexte : trêve commerciale entre les États-Unis et la Chine, espoir d'un accord sur le Brexit et retour de l'appétit pour le risque. Sept SL en trois semaines.
- **Février 2020.** Des ventes de NZDCAD et CHFJPY touchent leur SL alors que ces paires finissent le mois en baisse (−2,2 % et −0,6 %) : le sens était bon, l'entrée ou le stop non. C'était le début de la panique COVID, avec une volatilité qui a explosé.
- **Stops très serrés** : 4 pips (USDCAD 09/2020, perte de 3 948 $), 1 $ sur l'or (09/2021), 2 à 4 pips sur plusieurs trades de 2021. Ils expliquent les nombreux « SL touché puis le prix est parti dans notre sens » : au moins 9 cas où le canal le dit lui-même.
- **Plus d'un SL sur deux n'est pas un problème de direction.** Sur les SL dont on connaît le sens, 16 vont dans le sens du mouvement du mois (16 « avec », 12 « contre »). La perte vient de l'entrée ou de la taille du stop.

## 6. Mois qui n'ont pas suivi leur saisonnalité, et pourquoi

Le fichier [`data/mois_hors_saisonnalite.csv`](../data/mois_hors_saisonnalite.csv) liste les **137 mois** (2019-2026, 14 paires) où une paire a évolué à l'inverse de son biais sur 10 ans, avec un écart d'au moins un écart-type. Les épisodes les plus marqués (au moins 1,5 écart-type) se regroupent autour d'événements macro :

| Période | Paires hors saison (réel vs moyenne 10 ans) | Cause principale |
|---|---|---|
| Février 2019 | GBPAUD +3,65 % (vs −1,40), EURAUD +1,91 % | AUD affaibli par les signaux de baisse de taux de la RBA ; livre soutenue par le recul du risque de Brexit sans accord |
| Mai 2019 | EURGBP +2,77 % (vs −0,71) | Démission de Theresa May, crainte d'un Brexit dur, montée du Brexit Party |
| Juillet 2019 | Or +3,97 % (vs −0,87), NZDUSD −1,68 % | Virage de la Fed vers les baisses de taux (première baisse le 31/07), guerre commerciale |
| Décembre 2019 | GBPUSD +2,56 % (vs −0,45 ; 2,8 σ) | Élections britanniques du 12/12 : majorité conservatrice, fin de l'incertitude sur le Brexit |
| Mars 2020 | GBPAUD +3,11 %, USD et JPY en forte hausse | Krach COVID et ruée sur le dollar ; AUD et NZD effondrés |
| Mai, août et novembre 2020 | AUDUSD +4,67 % (11/2020), NZDUSD +6,16 %, EURUSD +2,58 %, AUDJPY +3,26 % (08/2020) | Création monétaire de la Fed et dollar faible ; en novembre, vaccins (Pfizer le 09/11) et élection américaine. Mois habituellement favorables au dollar, totalement inversés |
| Avril-mai 2021 | GBPUSD +2,53 % (3 σ), EURGBP +2,12 %, or +5,11 % | Réouverture rapide du Royaume-Uni (vaccination) ; recul des rendements américains |
| Juin 2021 | USDCHF +2,87 % (4,5 σ), AUDUSD −2,72 %, NZDUSD −3,78 % | Réunion de la Fed du 16/06, plus restrictive que prévu (« dot plot ») : dollar en forte hausse au lieu de sa faiblesse habituelle de juin |
| Mars-avril 2022 | Or +4,96 %, USDCAD +2,56 % | Invasion de l'Ukraine, puis hausse de taux de 50 pb de la Fed (mai 2022) |
| Novembre-décembre 2022 | EURJPY −2,12 %, GBPJPY −2,64 %, or +3,67 % puis +4,23 % | CPI américain plus faible le 10/11, interventions du Japon (octobre), élargissement surprise de la bande de taux de la BoJ le 20/12 : rebond du yen pendant ses mois habituellement faibles |
| Décembre 2023 | GBPJPY −3,92 % | Spéculation sur la sortie des taux négatifs au Japon (Ueda, 07/12) et virage de la Fed vers les baisses de taux (13/12) |
| Janvier 2024 | USDJPY +3,79 % (vs −1,14 ; 3,1 σ) | Séisme de Noto (01/01), qui repousse la hausse de la BoJ ; données américaines solides |
| Juillet-septembre 2024 | NZDUSD −2,44 % (07) puis +4,96 % (08) ; AUDUSD +3,52 % (08) et +2,50 % (09) ; EURUSD +2,19 % (08) ; or +4,09 % (09) | Virage de la RBNZ vers les baisses (07/2024) ; hausse de la BoJ le 31/07 et NFP faible le 02/08 : **krach du 5 août** et débouclage du carry trade ; baisse de 50 pb de la Fed le 18/09 ; relance chinoise le 24/09. Le septembre « baissier » d'EURUSD est démenti |
| Octobre 2024 | Or +4,63 % | Achats des banques centrales, élection américaine |
| Décembre 2024 | USDCHF +2,79 % (vs −1,52), GBPAUD +3,83 % | Baisse de 50 pb de la BNS (12/12) ; baisse « restrictive » de la Fed le 18/12 ; RBA prudente |
| Avril 2025 | AUDJPY −2,36 %, GBPJPY −1,55 %, EURGBP +1,60 % | Droits de douane du « Liberation Day » (02/04) : fuite vers le yen et l'euro ; le dollar **baisse** malgré la crise, ce qu'Amirou relève lui-même (#13852) |
| Juillet 2025 | USDJPY +4,46 % (vs −1,20 ; 2,6 σ), USDCHF +2,33 % | Revers de la coalition au pouvoir aux sénatoriales japonaises (20/07), rebond du dollar après les accords commerciaux |
| Août 2025 | GBPUSD +2,20 % | NFP américain très faible (01/08) avec de lourdes révisions ; hausse du risque sur l'indépendance de la Fed |
| Avril 2026 | AUDUSD +4,80 %, EURAUD −2,83 % | Cessez-le-feu entre les États-Unis et l'Iran (07/04, #14664), retour de l'appétit pour le risque, RBA en cycle de hausse (rapport SignalX *8avril.pdf*) |
| Juin 2026 | USDCHF +3,47 % (vs −0,93), AUDJPY −1,80 %, EURUSD −2,25 % | Fed restrictive (taux maintenus, une hausse anticipée), DXY au plus haut depuis un an, inflation européenne qui ralentit (*22juin.pdf*, #14981) ; yen au plus bas depuis 40 ans à 162,27 (*30juin.pdf*) |
| Août 2026 | EURAUD −1,12 % | Intervention de la BoJ le 12/08 (#15204) ; RBA restrictive |
| Septembre 2026 (au 25/09) | USDJPY −1,60 % (vs +1,11) | Hausse de la BoJ à 1,25 % le 18/09 ([Bloomberg](https://www.bloomberg.com/news/articles/2026-09-18/boj-hikes-rates-at-fastest-pace-since-1990-as-inflation-persists)) et risque d'intervention, alors que la Fed remontait aussi ses taux |

**Ce qui revient :** un mois quitte sa saisonnalité quand **une banque centrale change de cap par surprise** (Fed en juin 2021 et septembre 2024, BoJ en décembre 2022 et juillet 2024, BNS en décembre 2024), ou quand **un choc politique ou géopolitique** déplace les capitaux (Brexit, COVID, Ukraine, droits de douane de 2025, Iran en 2026). Les mois de « saison » ne résistent pas à ces événements. C'est d'ailleurs la règle qu'Amirou énonce lui-même en avril 2024 (#10946) et septembre 2025 (#13852).

## 7. Faits inhabituels relevés

**Marchés**
1. **EURUSD sous la parité** (septembre 2022, 0,99) et **USDJPY au plus haut depuis 40 ans à 162** (juin 2026, *30juin.pdf*).
2. **Le dollar baisse pendant les crises de 2025** au lieu de servir de refuge (droits de douane de Trump). Amirou l'observe (#13852) ; c'est l'inverse de 2020 et de 2022.
3. **Krach du 5 août 2024** : AUDJPY a perdu 14 % entre le 10/07 et le 05/08, puis le NZDUSD a fait +5 % en août, l'un de ses deux mois habituellement les plus faibles (−1,6 % en moyenne sur 2010-2025).
4. **2026, reprise des hausses de taux** : la Fed relève ses taux pour la première fois depuis 2023 (16/09, 12 voix contre 0) ; la BCE (2,50 %), la RBA (4,60 %, quatrième hausse de l'année) et la BoJ (1,25 %, plus haut depuis 31 ans) aussi. Pétrole au-delà de 100 $ (Brent à 105,83 $ dans *21sep.pdf*), rendement à 10 ans américain à 5 %, or au-delà de 4 400 $.
5. **AUDUSD +4,8 % en avril 2026** : l'un des quatre mois à plus de 4,5 % depuis 2020.

**Canal**
6. **Objectifs redessinés après coup** pour annoncer des gains plus gros (EURJPY 2021, GBPCAD 2023, EURUSD 2025, voir [`TRADES_SEPTEMBRE.md`](TRADES_SEPTEMBRE.md)).
7. **Perte non déclarée**, visible seulement dans un historique (EURGBP, 16/09/2026).
8. **Promotion d'OmegaPro en 2022**, dont les fondateurs ont été inculpés aux États-Unis en 2025 pour une fraude de type Ponzi de plus de 650 M$.
9. **Statistiques saisonnières citées sans réalité dans les données** (mai et août 2026, section 4).
10. **Tailles de position sans rapport avec les règles données en public** : 120 lots avec 4 pips de stop en 2020, compte de 100 $ risqué à environ 80 % en 2026.

## 8. Ce qu'il faut retenir
- **La saisonnalité est un filtre de contexte, pas un moteur de résultat.** Dans les trades du canal, elle ne change pas le taux de réussite, qui reste autour de 40 %.
- **La lecture macro d'Amirou est son vrai point fort.** Mais les mois qui « trahissent » leur saisonnalité sont justement ceux des grands chocs, que la saisonnalité ne peut pas anticiper.
- **Les ratés viennent d'abord de l'exécution** (stops de quelques pips, entrées avant confirmation, trades ouverts juste avant une annonce), plus que d'une erreur de direction.
- **Pour aller plus loin** : coder chaque trade de 2021 à 2026 à partir des captures (sens, entrée, SL, TP lus sur l'image), comme pour les septembres, afin de remplacer les 125 issues inconnues par des issues vérifiées.
