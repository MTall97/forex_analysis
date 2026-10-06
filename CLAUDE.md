# Contexte du projet (pour les agents IA et les nouveaux contributeurs)

## Objet
Étudier la saisonnalité du Forex et des matières premières, et vérifier les analyses et les trades publiés par Hamma dit Amirou Touré :
- canal Telegram « The halal winning team », de mars 2019 à octobre 2026 ;
- rapports SignalX de 2026.

L'utilisateur travaille en français.

## Historique
1. **Antigravity**, l'agent IA utilisé au départ, a écrit `forex_seasonality_generator.py`, produit les 13 PDF de `rapports_pdf/` et rédigé `RAPPORT_GLOBAL_PROJET.md`, `AUDIT_TRADES_AMIROU_WINS_LOSSES.md` et `RAPPORT_SYNTHESE_SIGNALX_2026.md` à partir de `ChatExport_2026-09-17/result.json`. Ses scripts d'extraction sont restés sur sa machine (`C:\Users\dani\.gemini\antigravity\…`). Ses rapports ont été **corrigés dans le texte** le 01/10/2026, à la demande de l'utilisateur : chaque correction est marquée ✏️ et expliquée, et la version d'origine reste dans l'historique Git (commit `4610e69`).
2. **Vérification du 01/10/2026** :
   - export HTML complet converti en `data/telegram_messages.jsonl` ;
   - scripts reproductibles dans `scripts/` ;
   - vérification des rapports d'Antigravity (`docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md`) ;
   - vérification des trades de septembre 2019–2026 (`analyses/TRADES_SEPTEMBRE.md`) ;
   - proposition de stockage des images (`docs/STOCKAGE_IMAGES.md`).

## Règles de travail
- **Source de vérité des messages** : `data/telegram_messages.jsonl` (id, date_utc, text, photo, media, reply_to, forwarded_from). Les ids sont ceux de Telegram, identiques dans `result.json` ; les heures sont en UTC. Pour le régénérer : `python scripts/telegram_html_to_jsonl.py ChatExport_… data/telegram_messages.jsonl`.
- **Citer** un message par son id (`#15374`). Ne jamais compléter une citation ni présenter un commentaire comme un trade : c'est l'erreur principale des rapports d'Antigravity.
- **Classer chaque trade selon ce que le canal montre** : ✅ gain, ❌ perte, ➖ BE, ⏸ non déclenché, ❔ non documenté, ⚠️ après coup ou invérifiable. Un gain « flottant » n'est pas un TP.
- **Captures** :
  - photos du canal : `ChatExport_2026-10-01/photos/photo_N@JJ-MM-AAAA_HH-MM-SS.jpg` (heure UTC) ;
  - captures citées dans les analyses : copiées dans `assets/trades/AAAA-MM/` ;
  - liens TradingView : `scripts/fetch_tradingview_snapshots.py` les télécharge dans `assets/tradingview/AAAA-MM/AAAA-MM-JJ_HHhMM_msg<id>_<idTV>.png`, avec un `index.csv`.
- **Accès réseau** : Yahoo Finance, Stooq et TradingView peuvent être bloqués dans l'environnement cloud. Dans ce cas, les données de cours ne sont pas vérifiables en direct ; le dire plutôt que deviner.
- **Saisonnalité « du projet »** : uniquement ce que calcule le générateur (mois et jours de la semaine, 2020-2025). La « règle de la semaine 1 » vient d'Amirou, pas du projet.

## Données de cours
- `data/prix/fx_daily_fred.csv` (Fed H.10 via github.com/datasets/exchange-rates, accessible depuis le cloud) et `data/prix/gold_monthly.csv`. `scripts/saisonnalite_mensuelle.py` en tire `data/rendements_mensuels.csv` et `data/saisonnalite.csv`.
- Registre de tous les trades : `scripts/construire_registre_trades.py` → `data/trades.csv` (corrections manuelles dans `data/trades_corrections.csv`) ; confrontation : `scripts/confronter_trades_saisonnalite.py` → `analyses/TRADES_VS_SAISONNALITE.md`.

## Captures et simulation (2021-2026)
- OCR : `scripts/lire_captures_ocr.py` (Tesseract, `apt install tesseract-ocr`, `OMP_THREAD_LIMIT=1`) → `data/captures_niveaux.csv` ; résolution des niveaux et de la paire : `scripts/resoudre_niveaux.py` → `data/captures_trades.csv`.
- Prix : `scripts/prix_yahoo.py` (Yahoo Finance, cache **suivi par Git** dans `data/prix/yahoo/` : horaire depuis 12/2023, seule copie car Yahoo ne garde que 730 jours ; compléter avec `python scripts/prix_yahoo.py --mettre-a-jour`). Journalier fiable : Dukascopy (`data/prix/journalier_dukascopy.csv`, cache brut dans `data/prix/dukascopy/`), limité en débit depuis le cloud.
- Inventaire des données et ordre des scripts : `docs/DONNEES_ET_SCRIPTS.md`.
- Simulation : `scripts/simuler_trades_dukascopy.py` → `data/trades_simules.csv` ; algorithme : `scripts/algo_amirou_backtest.py` ; modèle : `scripts/modele_meta.py`. Synthèse : `analyses/STRATEGIE_ET_MODELE.md`.
- Fondamentaux : `scripts/collecter_fondamentaux.py` → `data/fondamental/` (calendrier TradingView, COT CFTC, taux BIS) ; `scripts/biais_textuel.py` (biais écrit d'Amirou) ; `scripts/modele_fondamental.py` (tests A, B, C) ; `scripts/algo_mlq_backtest.py` (MLQ = niveaux de 250 pips, mercredi). Synthèse : `analyses/MODELE_FONDAMENTAL_ET_MLQ.md`.
- Son style change selon l'époque (2021-2022 : stops de 10-16 pips, ratios 1:7-1:10 ; depuis 2023 : stops de 40-50 pips, ratios 1:2-1:3,5) : ne pas mélanger les périodes sans le dire. Analyse par époque : `scripts/analyse_par_epoque.py` → `analyses/TRADES_PAR_EPOQUE.md`.
- Flashcards « Naruto » (mai 2025 - juin 2026, #13305, #13327…#14986) : statistiques de rupture des englobantes journalières ; vérification : `scripts/tester_flashcards_englobante.py` → `analyses/FLASHCARDS_ENGLOBANTE.md`. Les bougies journalières Yahoo du Forex sont fausses (open, high/low) : reconstruire le journalier à partir de l'horaire.
- Autres algorithmes (carry, momentum, intrajournalier) : `scripts/tester_carry_momentum.py`, `scripts/tester_saisonnalite_intraday.py` → `analyses/AUTRES_ALGORITHMES.md`. Masterclass : `scripts/tester_masterclass.py`, `scripts/tester_strategie_bombe.py`, `scripts/tester_bebe_abandonne.py`, `scripts/strategie_combinee.py` (bougies journalières Dukascopy : `scripts/prix_dukascopy_journalier.py`, l'année en cours complétée par l'horaire Yahoo) → `analyses/MASTERCLASS_VERIFIEE.md` ; par paire et par année : `scripts/analyse_par_paire.py` → `analyses/STRATEGIES_PAR_PAIRE.md`, `data/par_paire/`. Trades datés 2020-2026 de chaque règle : `scripts/trades_masterclass_par_date.py` → `data/masterclass_2020_2026/`, `analyses/MASTERCLASS_TRADES_DATES.md` ; piste englobante + MLQ (achats) : `scripts/tester_englobante_mlq_recent.py`. Selon l'utilisateur, Amirou utilise les analyses de Marc to Market (Marc Chandler) ; ce n'est écrit dans aucune source du canal. Toujours comparer à un témoin (toute bougie, niveaux décalés) et vérifier que l'entrée est à un prix effectivement atteint.
- Figures des rapports : `scripts/figures_rapports.py` → `assets/figures/*.png` (à relancer après les scripts d'analyse).

## Travaux en attente
- Les 1 243 captures TradingView sont dans `assets/tradingview/` et ont été intégrées aux septembres 2021–2026. Les autres mois du canal ne sont pas encore vérifiés trade par trade.
- Images : triées (`data/photos_classification.csv`) et envoyées sur `s3://images-forex-analyse` (us-east-1) le 01/10/2026 ; elles ne sont plus suivies par Git, sauf les 67 citées dans les analyses. Pas d'identifiants AWS dans le dépôt : `scripts/upload_images_s3.py` lit les variables d'environnement standard. La purge de l'historique reste à décider par l'utilisateur ; ne jamais la faire sans son accord explicite.
- Rapport de la session du 01/10/2026 : `docs/RAPPORT_TRAVAUX.md`.
