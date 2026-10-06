# forex_analysis

Étude de la **saisonnalité du Forex et des matières premières**, confrontée aux analyses et aux trades publiés entre 2019 et 2026 par **Hamma dit Amirou Touré** sur son canal Telegram *« The halal winning team »* et dans ses rapports **SignalX**.

Le dépôt réunit trois choses :
1. un **générateur de rapports de saisonnalité** en Python (13 PDF déjà produits) ;
2. les **archives** du canal (15 062 messages, 3 577 photos) et des 21 rapports SignalX de 2026 ;
3. des **analyses** : celles produites par Antigravity (un agent IA utilisé au départ), et une vérification complète de ces analyses et des trades de septembre.

---

## Arborescence

| Chemin | Contenu |
|---|---|
| [`forex_seasonality_generator.py`](forex_seasonality_generator.py) | Générateur de rapports PDF de saisonnalité (yfinance + pandas + matplotlib) |
| [`rapports_pdf/`](rapports_pdf/) | 13 rapports de 5 pages (AUDJPY, AUDUSD, EURJPY, EURUSD, GBPJPY, GBPUSD, NZDUSD, USDCAD, USDCHF, USDJPY, GOLD, SILVER, OIL — 2020-2025) + `21sep.pdf` (rapport SignalX du 21/09/2026) |
| [`data/telegram_messages.jsonl`](data/telegram_messages.jsonl) | **Source de référence** : le canal entier (14/03/2019 → 01/10/2026), un message par ligne |
| [`data/trade_events.csv`](data/trade_events.csv) | Messages classés par événement de trade (entrée, TP, SL, BE, raté…) |
| [`scripts/`](scripts/) | Scripts de conversion, d'extraction et de téléchargement (voir plus bas) |
| [`analyses/STRATEGIE_ET_MODELE.md`](analyses/STRATEGIE_ET_MODELE.md) | **Stratégie d'Amirou, performance mesurée sur 518 trades rejoués, algorithme et modèle d'IA de copie** |
| [`analyses/MODELE_FONDAMENTAL_ET_MLQ.md`](analyses/MODELE_FONDAMENTAL_ET_MLQ.md) | **Version fondamentale (calendrier, COT, taux, biais écrit d'Amirou), habitudes MLQ et mercredi, évolution de son style 2021-2026** |
| [`analyses/TRADES_PAR_EPOQUE.md`](analyses/TRADES_PAR_EPOQUE.md) | **Ses trades analysés séparément pour 2021-2022 (stops serrés, grands ratios) et 2023-2026 (fondamental, MLQ, ratios 1:2-1:3)** |
| [`analyses/MASTERCLASS_VERIFIEE.md`](analyses/MASTERCLASS_VERIFIEE.md) | **La masterclass vérifiée sur 2012-2026 : 70 %, 75 %, 85 % annoncés contre 20 à 50 % mesurés ; aucune règle ni combinaison robuste sur 11 instruments** |
| [`analyses/MASTERCLASS_TRADES_DATES.md`](analyses/MASTERCLASS_TRADES_DATES.md) | **Les trades simulés pour chaque règle, datés, avec le focus 2020-2026 : aucune règle ne devient rentable ; une seule piste (achat sur englobante qui rejette un MLQ, +0,20 R depuis 2020) à suivre en démo** |
| [`analyses/STRATEGIES_PAR_PAIRE.md`](analyses/STRATEGIES_PAR_PAIRE.md) | **Chaque stratégie paire par paire et année par année, avec les dates de toutes les occurrences** |
| [`analyses/GUIDE_STRATEGIES.md`](analyses/GUIDE_STRATEGIES.md) | **Guide illustré : lundi-mardi-mercredi, englobante, bébé abandonné, structure du marché et Bombe, MLQ** |
| [`analyses/FLASHCARDS_ENGLOBANTE.md`](analyses/FLASHCARDS_ENGLOBANTE.md) | **Les flashcards « Naruto » (2025-2026) : la stratégie de l'englobante et ses « probabilités de rupture » vérifiées** |
| [`analyses/AUTRES_ALGORITHMES.md`](analyses/AUTRES_ALGORITHMES.md) | **Carry, momentum et saisonnalité intrajournalière testés sur 2000-2026 : ce qui marche vraiment sur le Forex** |
| [`analyses/TRADES_VS_SAISONNALITE.md`](analyses/TRADES_VS_SAISONNALITE.md) | **Tous les trades du canal confrontés à la saisonnalité**, pouvoir prédictif de la saisonnalité mensuelle (≈ 50 %), causes des ratés, mois hors saison et faits inhabituels |
| [`analyses/TRADES_SEPTEMBRE.md`](analyses/TRADES_SEPTEMBRE.md) | **Vérification des trades de chaque mois de septembre (2019-2026)** et statistiques sur tout le canal |
| [`docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md`](docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md) | Vérification point par point des trois rapports d'Antigravity |
| [`docs/STOCKAGE_IMAGES.md`](docs/STOCKAGE_IMAGES.md) | Tri des images, envoi vers S3 et allègement de GitHub |
| [`docs/RAPPORT_TRAVAUX.md`](docs/RAPPORT_TRAVAUX.md) | Rapport des travaux de la session du 01/10/2026 |
| [`data/photos_classification.csv`](data/photos_classification.csv) | Classement des 3 568 photos du canal (trading, conversation, certificat, autre) |
| [`assets/trades/`](assets/trades/) | Captures de trades citées dans les analyses, nommées `AAAA-MM-JJ_HHhMM_photoN.jpg` (UTC) |
| [`assets/tradingview/`](assets/tradingview/) | Les 1 243 captures des liens TradingView du canal, nommées par date et numéro de message (+ `index.csv`) |
| [`ChatExport_2026-10-01/`](ChatExport_2026-10-01/) | Export HTML brut du canal (messages + photos), jusqu'au 01/10/2026 |
| [`ChatExport_2026-09-17/`](ChatExport_2026-09-17/) | Export JSON brut (jusqu'au 17/09/2026, sans les photos) + les 21 PDF SignalX (`rapport Amirou/`) |
| [`RAPPORT_GLOBAL_PROJET.md`](RAPPORT_GLOBAL_PROJET.md), [`AUDIT_TRADES_AMIROU_WINS_LOSSES.md`](AUDIT_TRADES_AMIROU_WINS_LOSSES.md), [`RAPPORT_SYNTHESE_SIGNALX_2026.md`](RAPPORT_SYNTHESE_SIGNALX_2026.md) | Rapports rédigés par Antigravity, **corrigés dans le texte** (corrections marquées ✏️ et expliquées ; version d'origine dans l'historique Git) |

**Relancer les analyses** : toutes les données sont dans le dépôt ; inventaire, ordre des scripts et commandes dans [`docs/DONNEES_ET_SCRIPTS.md`](docs/DONNEES_ET_SCRIPTS.md).

Les figures des rapports (schémas des stratégies, graphiques de résultats) sont dans `assets/figures/` et se régénèrent avec `python scripts/figures_rapports.py`.

---

## Installation

```bash
python -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
```

Les scripts de `scripts/` n'utilisent que la bibliothèque standard. `requirements.txt` ne sert qu'au générateur de saisonnalité.

## Utilisation

### 1. Générer des rapports de saisonnalité
```bash
python forex_seasonality_generator.py                                   # 12 actifs par défaut, 2020-2025
python forex_seasonality_generator.py --assets EURUSD GOLD OIL --start 2015-01-01 --end 2025-12-31
```
Chaque PDF de 5 pages contient :
1. les pips moyens par mois et le nuage des rendements mensuels ;
2. les boxplots et le tableau mensuel (directionnalité, rendement moyen, écart-type) ;
3. le classement des mois haussiers, baissiers et neutres ;
4. le profil par jour de la semaine et le profil annuel cumulé ;
5. la corrélation avec 6 moteurs macro (DXY, EUR, JPY, NZD, or, pétrole).

Il faut un accès internet à Yahoo Finance.

### 2. Mettre à jour les messages du canal
Exportez le canal depuis Telegram Desktop au format HTML (avec les photos), puis :
```bash
python scripts/telegram_html_to_jsonl.py ChatExport_AAAA-MM-JJ data/telegram_messages.jsonl
```
Le texte et les dates obtenus sont identiques à l'export JSON pour les 14 925 messages communs (vérifié).

### 3. Extraire les événements de trade
```bash
python scripts/extract_trade_events.py     # écrit data/trade_events.csv + tableau par année
```

### 4. Télécharger les captures TradingView
```bash
python scripts/fetch_tradingview_snapshots.py --start 2019 --end 2027 --out assets/tradingview
```
- **Ce que fait le script** : il télécharge en parallèle les 1 243 images liées dans le canal et les range par mois.
- **Nommage** : `2026-09-01_10h06_msg15271_ZdyH7sGq.png` (date et heure UTC, numéro du message, identifiant TradingView).
- **Index** : un `index.csv` relie chaque message à son image.
- **Accès réseau** : il faut pouvoir joindre `s3.tradingview.com` et `www.tradingview.com`.

---

## Principaux résultats

### Saisonnalité calculée par le projet (2020-2025, 6 ans)
| Actif | Meilleurs mois | Pires mois |
|---|---|---|
| AUDJPY | juin (+2,10 %), avril (+1,55 %), octobre (+1,42 %) | juillet (−1,50 %), septembre (−0,33 %) |
| EURUSD | décembre (+1,17 %), novembre (+1,06 %), mai (+0,73 %, le plus régulier avec 83 % de mois positifs) | **septembre (−1,11 %, 33 % de mois positifs)**, janvier (−0,71 %) |
| EURJPY | juin (+2,17 %), octobre (+2,02 %), mars (+1,78 %) | juillet (−1,30 %) |

Six années de données, c'est peu : un seul mois exceptionnel suffit à déplacer une moyenne.

### Les trades d'Amirou (détail dans [`analyses/TRADES_SEPTEMBRE.md`](analyses/TRADES_SEPTEMBRE.md))
- **Tout le canal** : on relève **54 messages « TP touché » contre 72 « SL touché »**. L'audit d'Antigravity annonçait 167 gains pour 41 pertes, sans méthode.
- **Septembres 2019-2026, vérifiés à la main** : environ 29 gains, souvent flottants ou non chiffrés, pour 15 à 16 pertes. Beaucoup d'ordres ne sont jamais déclenchés, et plusieurs pertes ne sont pas annoncées.
- **Point fort vérifiable : la lecture macro.** En septembre 2026 par exemple, toutes les décisions de banques centrales anticipées dans le canal (BCE, Fed, BoE, BoJ, RBA) se sont produites comme annoncé. Le dollar a monté comme prévu (EURUSD −240 pips).
- **Point faible : le risque réel visible sur les captures.** On voit 120 lots avec un stop de 4 pips en 2020, et un compte de 100 $ qui risquait environ 80 % de son solde en 2026. C'est loin des 0,5 à 2 % recommandés en public.

### Fiabilité des rapports d'Antigravity (détail dans [`docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md`](docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md))
- **Fiable** : le résumé des 21 PDF SignalX, les grands faits macro, l'existence des messages cités.
- **À ne pas utiliser sans vérification** :
  - les statistiques de trades ;
  - les citations « complétées » ;
  - l'attribution de la « Chandler Signature » à Marc Chandler, absente de toutes les sources (l'utilisateur précise qu'Amirou utilise les analyses de Marc to Market : le lien est plausible, mais le contenu attribué à Chandler par Antigravity restait inventé) ;
  - la « règle de la semaine 1 », que le moteur ne calcule pas ;
  - la saisonnalité d'EURUSD en mai, présentée à tort comme baissière ;
  - la description technique des PDF (ReportLab, seaborn).

---

## Historique
| Date | Étape |
|---|---|
| sept. 2026 | Antigravity : générateur Python, 13 PDF de saisonnalité, analyse de `result.json`, trois rapports de synthèse |
| 01/10/2026 | Ajout de l'export HTML complet du canal (avec photos) |
| 01/10/2026 | Vérification : parseur HTML, extraction des trades, vérification des septembres et des rapports d'Antigravity, scripts TradingView, README |

## Avertissement
Ce dépôt documente et vérifie des contenus publiés par un tiers. Ce n'est **pas un conseil en investissement**. Le trading sur marge comporte un risque élevé de perte en capital. Les archives du canal et les rapports SignalX restent la propriété de leur auteur : vérifiez la visibilité du dépôt avant tout partage.
