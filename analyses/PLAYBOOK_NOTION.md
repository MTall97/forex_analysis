# Le playbook Notion d'Amirou, confronté au canal

*14/10/2026. Source : la page publique [Thehalalwinningteam Playbook](https://conscious-dirt-ada.notion.site/Thehalalwinningteam-Playbook-b1f8629244e04274aeebd97e1a624a90). Texte extrait par `scripts/collecter_playbook_notion.py` dans [`data/playbook_notion/playbook.txt`](../data/playbook_notion/playbook.txt). Trades « setup A+ » : `scripts/verifier_setups_a_plus.py` → [`data/setups_a_plus.csv`](../data/setups_a_plus.csv).*

## 1. Ce que contient le playbook

C'est un **modèle Notion destiné aux élèves**, presque entièrement vide. Les champs sont à remplir (« RISQUE/TRADE : …… A > % – B > % – C > % », « à votre sauce », « Mensuel : »). Le modèle compte plusieurs centaines de sous-pages vides : journal par mois de 2024 à 2029, fiches « TRADE N°1 », tableaux de statistiques par heure.

**Les seules parties remplies** :
- **Profil** : swing trader et day trader ; paires majeures et croisées sur le yen ; sessions de Londres et de New York.
- **Jours de trading** : « mardi, mercredi, jeudi et le vendredi (uniquement quand il y a NFP) ».
- **Checklist du « SETUP A+ WEEKLY CYCLE »** :
  1. orderflow weekly et daily identifié ;
  2. premium/discount daily ;
  3. weekly open, utilisé comme premium/discount (« cf PO3 ») ;
  4. FVG et plus haut ou plus bas weekly ou monthly proche, à 200-300 pips au plus ;
  5. FVG daily pour l'entrée ;
  6. OTE H4 en corrélation avec le FVG daily ;
  7. confirmations sur les petites unités de temps (H4-H1) dans les « killzones » de New York ou de Londres (structure Wyckoff, MLQ, BPR H4) ;
  8. **stop de 50 pips au minimum**, sur le point pertinent le plus proche ;
  9. objectif sur un niveau weekly ou un MLQ/MWN.

  Ce sont des notions ICT (« smart money concepts ») ; le setup B est vide.
- **Les « caractéristiques de backtest » visées pour le setup A+** :
  - 5 dernières années, 100 trades au minimum ;
  - **taux de réussite de 90 % ou plus** ;
  - **ratio de 1:3 au minimum** ;
  - au moins 20 setups par an ;
  - rendement supérieur à 15 % par an.

  Les setups B et C visent 1:3, 60 setups par an et plus de 15 % par an, sans taux de réussite.
- **La formule du taux de réussite** : « ((nombre de trades totaux – nombre de SL) / nombre de trades totaux) × 100 ».
- **Une remarque** (19/03/2024, yen) : éviter de trader avant une réunion de banque centrale.
- **Un exemple de fiche de trade** : vente GBPAUD un jeudi, ratio 1,48, TP, risque de 1 %, « respecté ». Il est recopié tel quel dans des dizaines de fiches du modèle.

**Aucun tableau de statistiques n'est rempli** : ni taux de réussite, ni nombre de trades, ni rendement, ni répartition par heure. Le playbook décrit le backtest à faire, mais n'en publie aucun résultat.

## 2. Problèmes internes au playbook

- **Le taux de réussite compte les trades au point mort (BE) comme gagnants.** La formule retranche seulement les SL : un trade fermé au point d'entrée compte comme une réussite. Un « 90 % » mesuré ainsi peut cacher beaucoup de trades à 0 R.
- **90 % de réussite à 1:3 est irréaliste.** Cela ferait en moyenne 0,9 × 3 − 0,1 = **+2,6 R par trade**. Avec 20 setups par an à 1 % de risque, on obtiendrait environ +52 % par an. L'objectif affiché de « plus de 15 % par an » serait donc trois fois trop modeste. Aucune stratégie testée dans ce dépôt n'approche ces chiffres : la meilleure, l'englobante + MLQ, fait entre +0,1 et +0,2 R par trade avec environ 45 % de réussite.

## 3. Le playbook confronté au canal

### Les « setups A+ » : 39 % de réussite quand ils sont annoncés, 86 % quand ils sont montrés après coup
Amirou décrit le setup A+ comme « un trade qui a plus de 90 % de taux de réussite […] backtesté sur des années » (#12503, 10/12/2024). Il annonce aussi « plus de 95 % » (#12645) et « setup A+ donc 90 % de probabilité » (#15562). 38 trades sont qualifiés de A+ dans le canal (mis à jour le 17/10/2026 avec l'EURUSD « setup A+ » du 14/10, #15631-#15633, arrêté au stop) :

| Publication | Trades A+ | Exécutés | Gagnants | Perdants | Non déclenchés | Réussite | R moyen |
|---|---|---|---|---|---|---|---|
| **annoncés avant l'entrée** (copiables) | 24 | 18 | 7 | 11 | 6 | **39 %** | +0,18 |
| montrés après coup | 14 | 14 | 12 | 2 | — | 86 % | +1,76 |

- Si la vraie réussite était de 90 %, obtenir 7 gagnants ou moins sur 18 aurait une probabilité d'environ **1 sur 6 millions**. Sur les trades copiables, l'annonce de 90 % est démentie.
- Le chiffre de 86 % n'apparaît que sur les trades montrés **après coup**, c'est-à-dire choisis une fois le résultat connu. C'est l'effet de sélection déjà relevé dans tout le canal.
- Le R moyen des A+ annoncés, +0,18 R, est du même ordre que celui de tous ses trades copiables (+0,21 R ± 0,14, voir `analyses/TRADES_TOUS_LES_MOIS.md`). Être qualifié de A+ ne distingue pas les trades. Avec 18 trades, ce chiffre reste très imprécis.
- Le rapprochement entre chaque message « A+ » et son trade est automatique. Chaque ligne de `data/setups_a_plus.csv` donne les deux ids pour qu'on puisse la vérifier.

### Ses propres règles ne sont pas appliquées
- **Stop de 50 pips au minimum** : en octobre 2026, sur 10 plans en Forex avec un stop, un seul respecte cette règle (EURNZD, #15565 : 50,6 pips). Les autres vont de 15 à 41 pips. L'EURGBP du 05/10, qualifié de « setup A+ donc 90 % de probabilité », a un stop de **15 pips**. L'EURUSD du 14/10 au soir, « setup A+ », a 35 pips. Le GBPJPY « A+ » (#15625) a 25 pips.
- **Pas de trade le lundi** : le 05/10, un lundi, il publie trois plans (EURGBP « A+ », EURNZD, Dow Jones). Le 12/10, un autre lundi, il montre une position GBPUSD.
- **La définition du A+ change** : dans le playbook, c'est une checklist technique (FVG, OTE, killzones, MLQ). Dans le canal, le 01/07/2026, c'est « l'analyse fondamentale 40 %, l'analyse technique 25 %, l'analyse sentimentale 25 %, price action 10 % » (#14995).
- **Le ratio est réécrit après coup** : le GBPJPY du 14/10 était publié avec un objectif à 2,2 R (#15624). À 18h25, l'objectif a été redessiné là où le prix était déjà allé, et le trade, jamais déclenché, est présenté comme « un trade qui a fait 1:5 RR » (voir `analyses/OCTOBRE_2026.md`).

## 4. Ce qui est testable, et ce qui l'a déjà été
- **Déjà testé, sans résultat** :
  - entrée sur un FVG 1h ou 4h (`analyses/ENGLOBANTE_FVG.md`) ;
  - les MLQ, pas meilleurs que des niveaux décalés sans signification (`analyses/CASSURE_RETOUR_MLQ.md`, `analyses/MASTERCLASS_VERIFIEE.md`) ;
  - le narratif (`analyses/NARRATIF_ET_STRATEGIES.md`) ;
  - la sélection des trades a posteriori (`analyses/JOURNAL_ET_SELECTION_TRADES.md`).
- **La checklist A+ complète, traduite en règles, a été testée le 14/10/2026** ([`analyses/CHECKLIST_A_PLUS.md`](CHECKLIST_A_PLUS.md)). Elle gagne 13 à 33 % du temps, pas 90 %. Elle fait +0,18 R par trade (±0,24) sur 2012-2026, un résultat compatible avec zéro, et ne se présente qu'environ 0,5 fois par an et par paire, contre au moins 20 setups par an annoncés.
