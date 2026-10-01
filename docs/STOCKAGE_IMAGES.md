# Stockage des images : état et marche à suivre

> **Mise à jour du 01/10/2026 (soir)**
> - **Envoi vers S3 fait** : 4 190 fichiers, 389,5 Mo, dans `s3://images-forex-analyse` (région `us-east-1`). Le décompte a été vérifié dans le bucket :
>   - `ChatExport_2026-10-01/photos/` : 2 899 photos de trading et de conversations, sans les miniatures ni les photos non liées au trading ;
>   - `assets/tradingview/` : 1 243 captures et `index.csv` ;
>   - `assets/trades/` : 47 captures.
> - **Branche allégée** : ces images ne sont plus suivies par Git (8 405 fichiers retirés du suivi, sans suppression locale), et `.gitignore` empêche de les rajouter. Les 67 images citées dans les analyses restent dans le dépôt pour que les liens fonctionnent.
> - **Reste à décider** : la purge de l'historique (étape 3 ci-dessous). Sans elle, un clone télécharge toujours les ≈ 480 Mo d'historique.

## État (01/10/2026)
| Contenu | Taille | Fichiers | Remarque |
|---|---|---|---|
| `ChatExport_2026-10-01/photos/` | 400 Mo | 3 568 photos + miniatures | Triées une par une : voir le tableau ci-dessous |
| `assets/tradingview/` | 135 Mo | 1 243 captures + `index.csv` | Toutes les captures TradingView du canal (2020-2026) |
| `assets/trades/` | 2,7 Mo | 47 captures | Preuves citées dans `analyses/TRADES_SEPTEMBRE.md` |
| `ChatExport_2026-09-17/` | 50 Mo | `result.json` + 21 PDF SignalX | `result.json` est remplacé par `data/telegram_messages.jsonl` |
| **Historique Git** | **≈ 480 Mo** compressés | – | Chaque clone télécharge tout l'historique |

## Tri des photos du canal
Classement fait à la main sur des planches de miniatures numérotées. Le résultat est dans [`data/photos_classification.csv`](../data/photos_classification.csv), avec une ligne par photo et les colonnes photo, message, date, catégorie et décision.

| Catégorie | Photos | Taille | Contenu | Décision |
|---|---|---|---|---|
| trading | 2 640 | 274 Mo | Graphiques, ordres, historiques MT4/MT5, comptes, journaux de trading, schémas pédagogiques | gardée |
| conversation | 199 | 24 Mo | Captures de discussions : témoignages, échanges avec des élèves, parfois avec un graphique | gardée (cas limites) |
| certificat | 153 | 18 Mo | Certificats de prop firms des élèves (FTMO, MyForexFunds, AQRE, TFT…) | à supprimer |
| autre | 576 | 86 Mo | Photos personnelles, voitures, voyages, événements, publicités, mèmes, publications Facebook/Instagram | à supprimer |

Supprimer les catégories `certificat` et `autre` libère **104 Mo**, soit 1 458 fichiers en comptant les miniatures. Le script est prêt :
```bash
python scripts/supprimer_photos_non_trading.py              # simulation : liste ce qui serait supprimé
python scripts/supprimer_photos_non_trading.py --confirmer  # suppression réelle
git add -A ChatExport_2026-10-01/photos && git commit -m "Supprime les photos non liées au trading"
```
Les pages `messages*.html` afficheront alors une image manquante pour ces messages. C'est normal : le CSV garde la trace de ce qui a été retiré.

## Envoi vers S3 (`s3://images-forex-analyse`)
```bash
pip install boto3
aws configure                                     # ou variables AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
python scripts/upload_images_s3.py --dry-run      # ce qui serait envoyé
python scripts/upload_images_s3.py                # envoi (relançable : saute ce qui est déjà en ligne)
```
- **Ce qui est envoyé** : `ChatExport_2026-10-01/photos`, `assets/tradingview` et `assets/trades`. Les chemins du dépôt servent de clés S3, par exemple `s3://images-forex-analyse/assets/tradingview/2026-09/2026-09-01_10h06_msg15271_ZdyH7sGq.png`.
- **Droits nécessaires** : `s3:ListBucket` et `s3:PutObject` sur le bucket.

## Alléger GitHub : ordre recommandé
1. **Envoyer les images sur S3**, puis vérifier dans la console AWS que le nombre d'objets correspond.
2. **Arrêter de suivre les images dans Git** (les fichiers restent sur le disque) :
   ```bash
   git rm -r -q --cached ChatExport_2026-10-01/photos assets/tradingview
   printf 'ChatExport_2026-10-01/photos/\nassets/tradingview/*.png\nassets/tradingview/*/*.png\n' >> .gitignore
   git commit -m "Images déplacées sur S3 (s3://images-forex-analyse)"
   ```
   `assets/tradingview/index.csv` et `data/photos_classification.csv` restent dans le dépôt : ils relient chaque message à son image sur S3.
3. **Purger l'historique (irréversible)**. C'est la seule étape qui réduit vraiment les ≈ 480 Mo :
   ```bash
   pip install git-filter-repo
   git filter-repo --path ChatExport_2026-10-01/photos --path assets/tradingview --invert-paths
   git push --force origin main claude/intelligent-ptolemy-27j5ht
   ```
   - **Conséquence** : les anciens commits contenant les images disparaissent de GitHub, et tous les clones existants doivent être refaits.
   - **Précaution** : ne le faites qu'**après** avoir vérifié la copie S3.

## Récupérer les captures TradingView
```bash
python scripts/fetch_tradingview_snapshots.py --start 2019 --end 2027 --out assets/tradingview
```
- **Résultat** : `assets/tradingview/AAAA-MM/AAAA-MM-JJ_HHhMM_msg<id>_<idTradingView>.png` et `index.csv`. Un lien republié plusieurs fois n'est téléchargé qu'une fois.
- **Accès réseau** : le script a besoin de `s3.tradingview.com` et `www.tradingview.com`, bloqués dans l'environnement cloud par défaut ; il se lance sans problème en local.
