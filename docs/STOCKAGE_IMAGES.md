# Stockage des images : constat et proposition

## Constat (01/10/2026)
| Contenu | Taille | Fichiers | Utilité pour l'analyse |
|---|---|---|---|
| `ChatExport_2026-10-01/photos/` (export Telegram) | **400 Mo** | 3 577 photos + 3 577 miniatures (`_thumb`, 76 Mo) | Faible au quotidien : seules quelques centaines de captures montrent un trade |
| `ChatExport_2026-09-17/rapport Amirou/` (PDF SignalX) | 40 Mo | 21 PDF + 1 image | Moyenne : le texte est extrait avec `pdftotext` |
| `ChatExport_2026-09-17/result.json` | 10 Mo | 1 | Remplacé par `data/telegram_messages.jsonl` (4 Mo, plus complet) |
| Historique Git (`.git`) | **368 Mo** compressés | – | Chaque clone télécharge tout l'historique |
| Captures TradingView (à télécharger) | ≈ 100–250 Mo estimés | 1 243 images | Indispensables pour vérifier les trades publiés par lien |

Ces images sont déjà dans l'historique de `main`. Les retirer aujourd'hui ne réduit pas la taille d'un clone tant que l'historique n'est pas réécrit.

## Proposition (recommandée) : séparer les « données brutes » des « preuves utiles »

1. **Les exports bruts sortent de Git**
   - **Quoi** : `ChatExport_*`, soit les photos, les miniatures et les PDF SignalX.
   - **Où** : une archive ZIP attachée à une **Release GitHub** (par exemple `donnees-brutes-2026-10-01`), ou un dossier Google Drive partagé.
   - **Pourquoi** : rien n'est perdu, l'export se re-télécharge en une fois, et le dépôt redevient léger (≈ 10 Mo de texte, de scripts et de rapports).
2. **Seules les images qui servent de preuve restent dans le dépôt**
   - **Quoi** : les captures de trades citées dans les analyses (`assets/trades/AAAA-MM/`, par exemple 2,7 Mo pour septembre 2026) et les captures TradingView (`assets/tradingview/AAAA-MM/`).
   - **Nommage** : chaque fichier porte la date, l'heure UTC et le numéro du message, ce qui le relie directement à la conversation.
3. **Git LFS pour ces images si leur volume grossit**
   - **Quand** : au-delà d'environ 200 Mo, par exemple quand toutes les captures TradingView et toutes les captures de trades seront ajoutées.
   - **Avantage** : un clone ne télécharge alors que les images de la version courante.
   - **À vérifier** : le quota LFS gratuit du compte GitHub avant de migrer.
4. **Réécriture de l'historique (optionnelle)**
   - **But** : récupérer réellement les 368 Mo.
   - **Coût** : `git filter-repo` puis un *force push* sur `main`. C'est **irréversible** sur GitHub, et les clones existants devront être refaits.
   - **Condition** : à faire seulement si vous le décidez explicitement.

## Commandes (à lancer seulement après votre accord)

```bash
# 1. Archiver les exports bruts puis les publier dans une Release GitHub (ou sur Drive)
zip -r donnees-brutes-2026-10-01.zip ChatExport_2026-09-17 ChatExport_2026-10-01

# 2. Arrêter de les suivre dans Git (les fichiers restent sur le disque)
git rm -r --cached ChatExport_2026-09-17 ChatExport_2026-10-01
printf 'ChatExport_*/\n' >> .gitignore
git commit -m "Sort les exports Telegram bruts du dépôt (archivés dans la Release)"

# 3. (option) Suivre les images de preuve avec Git LFS
git lfs install
git lfs track "assets/**/*.jpg" "assets/**/*.png"
git add .gitattributes && git commit -m "Suit les captures avec Git LFS"

# 4. (option, irréversible) Purger l'historique sur main
# pip install git-filter-repo
# git filter-repo --path ChatExport_2026-10-01 --path ChatExport_2026-09-17 --invert-paths
# git push --force origin main
```

## Récupérer les captures TradingView
```bash
python scripts/fetch_tradingview_snapshots.py --start 2019 --end 2027 --out assets/tradingview
```
- **Résultat** : `assets/tradingview/AAAA-MM/AAAA-MM-JJ_HHhMM_msg<id>_<idTradingView>.png` et un `index.csv`, qui relie chaque message à son image (un lien republié plusieurs fois n'est téléchargé qu'une fois).
- **Accès réseau** : le script a besoin de `s3.tradingview.com` et `www.tradingview.com`.
  - Dans l'environnement cloud de Claude Code, ajoutez ces deux domaines dans **Edit → Network access**.
  - Sinon, lancez le script sur votre machine.
