# Données et scripts : tout relancer sans rien retélécharger

Toutes les données utilisées par les analyses sont **dans le dépôt**. Les scripts lisent d'abord ces fichiers et ne vont sur Internet que s'ils manquent. On peut donc refaire chaque calcul hors ligne, le modifier, ou tester autre chose.

## 1. Installation
```bash
pip install -r requirements.txt
# OCR des captures uniquement : apt install tesseract-ocr tesseract-ocr-fra
```
Tous les scripts se lancent **depuis la racine du dépôt** : `python scripts/<script>.py`.

## 2. Inventaire des données

### Canal Telegram
| Fichier | Contenu | Produit par |
|---|---|---|
| `data/telegram_messages.jsonl` | Les 15 500 messages du canal (id, date UTC, texte, photo, média, réponse, transfert) : **source de vérité** | `scripts/telegram_html_to_jsonl.py` à partir de l'export HTML |
| `data/photos_classification.csv` | Catégorie de chaque photo (trading, conversation, certificat, autre) | tri manuel |
| `data/trade_events.csv`, `data/trades.csv` (+ `trades_corrections.csv`) | Événements de trade (TP, SL, BE…) et registre des 281 trades du canal | `extract_trade_events.py`, `construire_registre_trades.py` |
| `data/captures_niveaux.csv`, `data/captures_trades.csv` | Niveaux lus par OCR sur 2 758 captures, puis 518 trades cohérents | `lire_captures_ocr.py`, `resoudre_niveaux.py` |
| `assets/tradingview/index.csv` | Index des 1 243 captures TradingView (les images sont sur S3, voir `docs/STOCKAGE_IMAGES.md`) | `fetch_tradingview_snapshots.py` |

### Cours de change
| Fichier | Contenu | Période | Source | Remarque |
|---|---|---|---|---|
| `data/prix/fx_daily_fred.csv` | Clôtures quotidiennes de 7 devises contre le dollar | 2009-2026 | Fed H.10 | pour la saisonnalité |
| `data/prix/fx_daily_fred_1999.csv` | Idem | 1999-2026 | Fed H.10 | pour le carry et le momentum |
| `data/prix/gold_monthly.csv` | Or, moyenne mensuelle | | | |
| `data/prix/yahoo/<PAIRE>_1h.csv` | **Bougies horaires** de 27 instruments | **déc. 2023 – sept. 2026** | Yahoo Finance | ⚠️ Yahoo ne donne que les 730 derniers jours : ces fichiers sont la seule copie des débuts. Pour les compléter **sans effacer** l'historique : `python scripts/prix_yahoo.py --mettre-a-jour` |
| `data/prix/yahoo/<PAIRE>_1d.csv` | Bougies journalières Yahoo | 2020-2026 | Yahoo | ⚠️ **fausses en Forex** (ouverture = clôture dans 30 % des cas) : préférer Dukascopy ou l'horaire regroupé |
| `data/prix/dukascopy/<PAIRE>/<AN>_d1.bi5` | Fichiers bruts Dukascopy (bougies journalières) | 2012-2026 | Dukascopy | cache, relu sans réseau |
| `data/prix/journalier_dukascopy.csv` | **Bougies journalières fiables** (paire, date, OHLC) ; l'année en cours vient de l'horaire Yahoo (Dukascopy ne publie l'année qu'une fois finie) | 2012-2026 | construit depuis le cache | `python scripts/prix_dukascopy_journalier.py --debut 2012` |
| `data/rendements_mensuels.csv`, `data/saisonnalite.csv` | Rendements mensuels et biais saisonniers | 2009-2026 | | `saisonnalite_mensuelle.py` |

### Données fondamentales (`data/fondamental/`)
| Fichier | Contenu | Source |
|---|---|---|
| `calendrier.csv` | 71 000 annonces économiques (publié, consensus, précédent, importance), 2019-2026 | calendrier TradingView |
| `cot.csv` | Positionnement des fonds sur 8 devises (hebdomadaire, juin 2006 – sept. 2026) | CFTC |
| `taux.csv` (2019-2026), `../prix/taux_directeurs_1999.csv` (1999-2026) | Taux directeurs quotidiens | BIS |
| `biais_amirou.csv` | Biais haussier ou baissier d'Amirou par devise et par jour | `biais_textuel.py` |
| `indicateurs.csv`, `resultats_tests.json` | Indicateurs par devise et résultats des tests A, B, C | `modele_fondamental.py` |

### Résultats des tests (une ligne par trade, datée)
| Fichier | Stratégie |
|---|---|
| `data/trades_simules.csv` | Les 518 trades d'Amirou rejoués sur les cours |
| `data/epoques_trades.csv` | Ses trades annoncés, avec époque, distance au MLQ, fondamentaux |
| `data/flashcards_englobante_detail.csv` | Englobantes et trade de la « rupture » |
| `data/bebe_abandonne_horaire.csv`, `data/bebe_abandonne_journalier.csv` | Bébé abandonné |
| `data/bombe_trades.csv` | Stratégie de la Bombe |
| `data/masterclass_trades.csv`, `data/masterclass_resultats.json` | Règles de la masterclass (lundi-mardi-mercredi, MLQ…) |
| `data/strategie_combinee_trades.csv`, `data/strategie_combinee.csv` | Combinaisons englobante / mercredi / MLQ |
| `data/backtest_algo.csv`, `data/backtest_mlq.csv` | Algorithmes « prise de liquidité » et MLQ |
| `data/carry_momentum_mensuel.csv` | Carry et momentum, rendement mensuel |
| `data/par_paire/occurrences_*.csv` | Chaque stratégie : toutes les occurrences datées avec leur résultat |
| `data/par_paire/resume_paire_annee.csv`, `validation.csv` | Synthèse par paire et par année |

## 3. Les scripts, dans l'ordre

| Étape | Commande | Lit | Écrit | Réseau |
|---|---|---|---|---|
| Messages | `python scripts/telegram_html_to_jsonl.py ChatExport_2026-10-01 data/telegram_messages.jsonl` | export HTML | `telegram_messages.jsonl` | non |
| Registre | `python scripts/extract_trade_events.py` puis `python scripts/construire_registre_trades.py` | messages | `trade_events.csv`, `trades.csv` | non |
| Saisonnalité | `python scripts/saisonnalite_mensuelle.py` puis `python scripts/confronter_trades_saisonnalite.py`, `python scripts/tester_persistance_saisonnalite.py` | Fed | `rendements_mensuels.csv`, `persistance_saisonnalite.csv`, `TRADES_VS_SAISONNALITE.md` | si cache absent |
| Captures | `python scripts/lire_captures_ocr.py` puis `python scripts/resoudre_niveaux.py` | captures (S3) | `captures_*.csv` | non (Tesseract) |
| Trades rejoués | `python scripts/simuler_trades_dukascopy.py` | captures, Yahoo | `trades_simules.csv` | si cache absent |
| Époques | `python scripts/analyse_par_epoque.py` | trades simulés | `epoques_trades.csv` | non |
| IA, algorithmes | `python scripts/modele_meta.py`, `python scripts/algo_amirou_backtest.py`, `python scripts/algo_mlq_backtest.py` | | `meta_features.csv`, `backtest_*.csv` | non |
| Fondamentaux | `python scripts/collecter_fondamentaux.py` (**seulement pour mettre à jour**), `python scripts/biais_textuel.py`, `python scripts/modele_fondamental.py` | | `data/fondamental/` | collecte : oui |
| Flashcards | `python scripts/tester_flashcards_englobante.py` | Yahoo horaire | `flashcards_englobante*.csv` | non |
| Masterclass | `python scripts/prix_dukascopy_journalier.py --debut 2012`, puis `python scripts/tester_masterclass.py`, `python scripts/strategie_combinee.py`, `python scripts/tester_bebe_abandonne.py`, `python scripts/tester_strategie_bombe.py` | Dukascopy, Yahoo | `masterclass_*`, `strategie_combinee*`, `bebe_*`, `bombe_trades.csv` | non (cache) |
| Autres algorithmes | `python scripts/tester_carry_momentum.py`, `python scripts/tester_saisonnalite_intraday.py` | Fed, BIS, Yahoo | `carry_momentum_mensuel.csv`, `saisonnalite_intraday_*` | non (cache) |
| Par paire | `python scripts/analyse_par_paire.py` | tous les fichiers de trades | `data/par_paire/`, `analyses/annexes/` (rapports : `MASTERCLASS_VERIFIEE.md`, `STRATEGIES_PAR_PAIRE.md`) | non |
| Figures | `python scripts/figures_rapports.py` | tout | `assets/figures/` | non |

## 4. Mettre à jour les données
```bash
python scripts/prix_yahoo.py --mettre-a-jour                 # complète l'horaire Yahoo (garde l'historique)
python scripts/prix_dukascopy_journalier.py --debut 2012       # ajoute l'année en cours (le cache garde les autres)
python scripts/collecter_fondamentaux.py --debut 2019-01-01    # calendrier, COT, taux
```
- Dukascopy limite fortement le débit (environ 25 s par fichier depuis le cloud) : relancer le script reprend là où il s'était arrêté.
- Pour ajouter une paire : `python scripts/prix_dukascopy_journalier.py --debut 2012 --paires EURCAD …`. Attention, sans `--paires`, le script réécrit le CSV avec la liste par défaut.

## 5. Essayer autre chose
- **Changer un paramètre** : les règles sont en tête de chaque script de test (seuils de bougie « pleine », 60 pips, RR 1,2, ±25 pips du MLQ, gestion 1 R / 2 R…). On modifie la valeur, on relance le script, puis `analyse_par_paire.py` et `figures_rapports.py`.
- **Tester une nouvelle stratégie** : écrire une fonction qui produit une ligne par trade avec au moins `date`, `paire`, `sens` et `r` (résultat en R, spread déduit), l'enregistrer dans `data/`, puis l'ajouter à `strategies()` dans `scripts/analyse_par_paire.py`. On obtient alors automatiquement le tableau par paire et par année, la carte de chaleur et la liste datée.
- **Éviter de se tromper soi-même** : choisir les règles sur une période (par exemple 2012-2019) et ne regarder le résultat sur l'autre (2020-2026) qu'une seule fois ; plus on essaie de variantes, plus il est facile d'en trouver une qui « marche » par hasard.
- **Spread** : `SPREAD` dans `scripts/modele_meta.py` (en pips, par paire).
