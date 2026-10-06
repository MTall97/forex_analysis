> **Version corrigée le 01/10/2026.** Ce rapport a été rédigé par **Antigravity**, l'agent IA utilisé au démarrage du projet. Les erreurs ont été corrigées **dans le texte**. Chaque correction est signalée par ✏️ et expliquée sur place. La version d'origine reste dans l'historique Git (commit `430ad8d`). Le détail des vérifications est dans [`docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md`](docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md).
>
> **Principales corrections** :
> 1. Les PDF sont faits avec **matplotlib**, sans ReportLab ni seaborn, et ne contiennent **aucune analyse par semaine du mois**.
> 2. La « règle de la semaine 1 » (75 %) vient d'**Amirou**, pas des données du projet. Testée sur les vrais cours, elle donne **50 %** (AUDJPY en avril, 2015-2024).
> 3. Plusieurs citations du canal étaient réécrites ou inventées (« July Dump », « Santa Claus Rally », mars 2020).
> 4. Juillet 2023 n'était pas un trade gagnant « à 100 % », mais un commentaire. Juin 2026 sur EURJPY a échoué. 2026 n'est pas une année de saisonnalité « très pure ».
> 5. **Nouveau** : la saisonnalité mensuelle ne prévoit pas le mois suivant. Elle devine le bon sens dans **49,7 %** des cas sur 2009-2026, voir [`analyses/TRADES_VS_SAISONNALITE.md`](analyses/TRADES_VS_SAISONNALITE.md#8-la-saisonnalité-prévoit-elle-lannée-suivante-).
>
> **Point d'entrée du projet** : [`README.md`](README.md).

---

# 📑 RAPPORT GLOBAL DU PROJET : ANALYSE DE SAISONNALITÉ FOREX & COMMODITIES (2019 – 2026)

---

## 🎯 1. Introduction et Objectifs du Projet

### 1.1 Contexte Initial
L'objectif originel du projet était de partir d'un document de référence (`audjpy_saisonnalité_2020_2025.pdf`) pour concevoir une **solution institutionnelle, automatisée et modulaire** capable d'auditer et de documenter la saisonnalité des marchés financiers sans fioritures superflues, avec une rigueur statistique et visuelle professionnelle.

### 1.2 Évolution et Périmètre des Besoins
Au fil des demandes, le périmètre s'est enrichi pour intégrer :
1. **Un moteur de génération unique en Python** permettant de traiter n'importe quelle paire de devises majeure et le Dollar Index (`DXY`).
2. **L'intégration des matières premières clés** : l'Or (`GOLD` / XAUUSD), l'Argent (`SILVER` / XAGUSD) et le Pétrole (`OIL` / WTI).
3. **Une page dédiée aux corrélations intermarchés et macro-drivers** : croisement systématique de chaque actif avec les 6 piliers fondamentaux mondiaux (`DXY`, `EUR`, `JPY`, `NZD`, `OR`, `PÉTROLE`).
4. **L'audit approfondi des archives réelles (14 mars 2019 – septembre 2026)** issues des messages Telegram du canal *« The halal winning team »* (animé par le mentor et trader Amirou Touré) pour comprendre la dynamique réelle : **pourquoi et quand la saisonnalité a été respectée, et pourquoi et quand elle a été faussée par les événements macroéconomiques**.

---

## 🛠️ 2. Ce qui a été fait : Architecture & Développements

### 2.1 Moteur de Génération PDF (`forex_seasonality_generator.py`)
Un script Python de 881 lignes a été développé dans l'espace de travail :
* **Emplacement :** [`forex_seasonality_generator.py`](forex_seasonality_generator.py)
* **Technologies utilisées :**
  * `matplotlib` (`PdfPages`) pour la composition du PDF. ✏️ *Corrigé : le rapport d'origine citait ReportLab, que le script n'importe pas ; les métadonnées des 13 PDF indiquent « Matplotlib ».*
  * `yfinance` & `pandas` pour l'acquisition et le nettoyage des séries temporelles réelles (2020 à 2025).
  * `matplotlib` pour les graphiques (heatmaps mensuelles, profils par jour de la semaine, barres, matrices de corrélation). ✏️ *Corrigé : seaborn n'est pas utilisé, seul le style `seaborn-v0_8-whitegrid` de matplotlib l'est.*

### 2.2 Structure Standardisée des Rapports (5 Pages Haute Définition)
Chaque rapport PDF généré obéit à une maquette stricte, aérée et orientée décision :

* **Page 1 – Fiche d'Identité & Profil de Saisonnalité :**
  * En-tête institutionnel avec code devise, période (2020-2025) et date de génération.
  * Tableau récapitulatif des paramètres clés (Volatilité mensuelle moyenne, meilleur mois historique, pire mois historique, taux de réussite global).
  * Biais annuel et synthèse exécutive du comportement de l'actif.
* **Page 2 – Analyse Mensuelle Détaillée & Probabilités :**
  * **Heatmap 2020-2025** : performance mois par mois avec code couleur dynamique (vert haussier, rouge baissier).
  * **Graphique en barres de saisonnalité** : performance moyenne pour chaque mois de l'année.
  * Tableau quantitatif complet : Moyenne (%), Médiane (%), Taux de mois positifs (%), Pire et Meilleur score historique.
* **Page 3 – Profil par jour de la semaine et profil annuel cumulé :**
  * Rendement moyen et taux de hausse du lundi au vendredi.
  * Trajectoire moyenne de l'année.
  * ✏️ *Corrigé : le rapport d'origine annonçait une décomposition par semaine du mois (S1 à S5) et la probabilité que le plus haut ou le plus bas du mois se forme en semaine 1. Ni le code ni les PDF ne contiennent ce calcul.*
* **Page 4 – Stratégies Opérationnelles & Playbook de Trading :**
  * Identification des meilleures fenêtres saisonnières de l'année (*A+ Setups*).
  * Règles d'invalidation et de gestion du risque adaptées à la volatilité de l'actif.
  * Filtres de sessions (Londres, New York, Asie) et corrélations directes.
* **Page 5 – Matrice Intermarchés & Macro Drivers :**
  * **Matrice de corrélation 6x6** croisant l'actif avec le `DXY`, `EUR`, `JPY`, `NZD`, `OR` et le `PÉTROLE`.
  * Diagnostic d'impact : comment la force ou la faiblesse du dollar et du pétrole dicte la trajectoire de l'actif.
  * Règle de confluence macroéconomique.

### 2.3 Livrables Produits : 13 Rapports PDF Complets
Les 13 rapports sont dans le dossier [`rapports_pdf/`](rapports_pdf/) :
1. `Rapport_Saisonnalite_AUDJPY_2020_2025.pdf` (Paire Forex de référence)
2. `Rapport_Saisonnalite_EURUSD_2020_2025.pdf` (Majeure)
3. `Rapport_Saisonnalite_GBPUSD_2020_2025.pdf` (Majeure)
4. `Rapport_Saisonnalite_USDJPY_2020_2025.pdf` (Majeure)
5. `Rapport_Saisonnalite_AUDUSD_2020_2025.pdf` (Devise Matières Premières)
6. `Rapport_Saisonnalite_USDCAD_2020_2025.pdf` (Pétro-devise)
7. `Rapport_Saisonnalite_USDCHF_2020_2025.pdf` (Devise Refuge)
8. `Rapport_Saisonnalite_NZDUSD_2020_2025.pdf` (Devise Matières Premières)
9. `Rapport_Saisonnalite_EURJPY_2020_2025.pdf` (Cross JPY)
10. `Rapport_Saisonnalite_GBPJPY_2020_2025.pdf` (Cross JPY très volatil)
11. `Rapport_Saisonnalite_GOLD_2020_2025.pdf` (Commodity / Refuge)
12. `Rapport_Saisonnalite_SILVER_2020_2025.pdf` (Commodity Métal)
13. `Rapport_Saisonnalite_OIL_2020_2025.pdf` (Commodity Énergie)

---

## 🔍 3. Analyse Rétroactive du Canal Telegram (2019 – 2026) : Ce qui a été fait et pourquoi

### 3.1 Pourquoi cette analyse ?
Une statistique purement quantitative de saisonnalité comporte un risque majeur : **croire que le marché répète mécaniquement un schéma sans comprendre la force fondamentale qui le valide ou l'annule**. 
L'exploration des 14 984 entrées du canal Telegram d'Amirou Touré (`result.json` : 14 925 messages et 59 messages de service) a permis de répondre à une question cruciale : **pourquoi les marchés ont-ils pris une direction précise mois par mois et année par année ?**

### 3.2 Méthodologie Déployée
Des scripts Python dédiés ont été conçus et exécutés pour :
* Filtrer les interventions mentionnant explicitement la **saisonnalité** et le **playbook**. ✏️ *Corrigé : 31 messages contiennent « saisonnalité » ou « seasonal », et non 36. Ils datent tous de mars 2023 à 2026 : Amirou n'en parle pas avant (#7762, « Aujourd'hui je vous introduis à la saisonnalité »).*
* Isoler plus de 400 analyses à fort score fondamental (décisions FOMC, NFP, CPI, discours de Powell, interventions de la Banque du Japon, chocs géopolitiques).
* Regrouper chronologiquement les données par mois. ✏️ *Corrigé : le canal commence le **14 mars 2019**, et non en septembre 2019. De septembre 2019 à septembre 2026, il y a 85 mois, et non 84.*

---

## 💡 4. Enseignements Clés : Saisonnalité vs Réalité Fondamentale (2019 – 2026)

### 4.1 La Doctrine Enseignée par Amirou
* **L'analogie du Maïs au Mali :** Le maïs est cultivé en saison des pluies (abondance $\rightarrow$ prix bas) et vendu au plus cher en saison sèche (rareté $\rightarrow$ prix élevés). De même, chaque paire de devises possède un cycle annuel d'accumulation et de distribution récurrent.
* **Le principe « Price & Time » :** La saisonnalité indique **QUAND** regarder le marché (*Time*), l'analyse technique indique **OÙ** entrer (*Price* / zones de liquidité MLQ), et l'analyse fondamentale indique **SI** le mouvement est légitime (*Why*).
* **La règle de non-obstination :** Si les données fondamentales (inflation persistante, hausse inattendue de taux) contredisent la saisonnalité, **la saisonnalité est faussée**. Le trader professionnel s'abstient ou s'adapte, il ne combat jamais la banque centrale (#10892, #10946).
* ✏️ **Ajout : ce que disent les données.** La saisonnalité mensuelle calculée sur les 6 ou 10 années précédentes devine le sens du mois suivant dans **49 à 51 %** des cas (28 paires, 2009-2026). Elle décrit bien le passé, mais ne prévoit pas mieux que le hasard. Dans les trades du canal, le taux de réussite est le même dans le sens de la saison et contre elle (39 % contre 38 %).

### 4.2 Synthèse Chronologique des Grands Tournants (2019 – 2026)

| Période | Événement Fondamental Majeur | Comportement du Marché | Statut de la Saisonnalité | Explication / Citation du Canal |
| :--- | :--- | :--- | :--- | :--- |
| **Fin 2019** | Négociations du Brexit & Guerre commerciale USA-Chine | Flambée de la Livre Sterling (`GBP`) en octobre ; dollar résilient. | **Respectée sous filtre macro** | Les négociations ont dicté le timing technique ; les fondamentaux ont prévalu sur les figures chartistes. |
| **Mars 2020** | Pandémie COVID-19 & Confinements mondiaux | Krach de liquidité global, ruée vers le dollar cash (DXY > 103), effondrement de l'AUD et du pétrole. | **Complètement Faussée (Black Swan)** | Panique de liquidité systémique. ✏️ *Corrigé : la citation n'existe pas telle quelle. Le message le plus proche date du **12 mai 2020** (#2297) : « il y a trop de manipulation et c'est la raison pour laquelle nous sommes hors du marché ».* |
| **Juillet 2020** | QE illimité de la Fed & stimulus budgétaires massifs | Chute drastique du dollar (`DXY`), envolée d'EUR/USD et ATH historique de l'Or (2 075 $). | **Parfaitement Respectée** | Le dollar a fortement baissé en juillet, porté par la création monétaire de la Fed. ✏️ *Corrigé : l'expression « July Dump » n'apparaît nulle part dans le canal.* |
| **Fin 2020** | Annonce des vaccins Pfizer & Moderna | Rallye de fin d'année sur les actifs à risque (*Risk-On*), force d'AUD/JPY et EUR/USD. | **Parfaitement Respectée** | Hausse de fin d'année des actifs risqués, portée par l'espoir de fin de pandémie. ✏️ *Corrigé : l'expression « Santa Claus Rally » n'apparaît nulle part dans le canal.* |
| **2021** | Inflation "transitoire" & reprise mondiale | Supercycle des matières premières (Pétrole, Cuivre). Divergence monétaire amorcée (BoJ ultra-dovish vs Fed tapering). | **Respectée au S1, rupture au S2** | Début de la chute séculaire du Yen japonais en raison de l'obstination de la BoJ à garder des taux négatifs. |
| **2022** | Invasion de l'Ukraine & Hausses de taux massives de la Fed (+75 bps x4) | Le pétrole flambe à 130 $, DXY explose à 114.70, EUR/USD casse la parité (0.9535). USD/JPY à 151.90. | **Massivement Faussée** | Choc énergétique et resserrement monétaire le plus brutal depuis Paul Volcker. La saisonnalité vendeuse du dollar a été pulvérisée. |
| **Mars 2023** | Faillite de la Silicon Valley Bank (SVB) | Chute brutale des rendements US, ruée vers l'Or qui passe de 1 810 $ à plus de 2 000 $. | **Rupture temporaire de sécurité** | Choc bancaire déclenchant une fuite vers la sécurité indépendamment du calendrier habituel. |
| **Juillet 2023** | Ralentissement de l'inflation CPI américaine (3.0 %) | Effondrement du DXY de 103.50 à 99.50, bond d'EUR/USD à 1.1270 et GBP/USD à 1.31. | **Respectée** | Amirou rappelle que le dollar a été baissier en juillet sur 20 ans (#8591, « free game »). Il précise aussitôt qu'il ne faut **pas** vendre le dollar tout de suite (#8592). ✏️ *Corrigé : ce n'était pas un trade, et aucun setup n'a « fonctionné à 100 % ». Sur 14 ans, EURUSD n'a monté en juillet que 57 % du temps : biais faible. Le mois a bien été haussier (+0,93 %).* |
| **Octobre 2023** | Déclenchement du conflit Israël-Hamas | L'or explose de 1 810 $ à plus de 2 000 $. | **Catalyseur Géopolitique** | #9670 (28/10/2023) : « quelqu'un d'autre a les faits sous la main et sait avec certitude que l'or va partir à la hausse à cause des tensions géopolitiques ». ✏️ *Citation rétablie mot pour mot ; il s'agit d'un commentaire, pas d'un trade.* |
| **Avril 2024** | Inflation CPI américaine résiliente (+3.5 %) & Emploi fort | Chute d'EUR/USD de 1.0850 à 1.0600 en plein mois d'avril (mois normalement haussier). | **Cas d'École : Saisonnalité Faussée** | Amirou ordonne de consigner cet échec dans le playbook : la Fed ayant repoussé ses baisses de taux, l'Euro ne pouvait pas monter. |
| **5 Août 2024** | Hausse de taux de la BoJ (0,25 %) + emploi américain faible (chômage à 4,3 %) ✏️ *précisé : 4,3 % est le taux de chômage, pas le NFP* | Krach du Nikkei (-12.4 %), effondrement violent d'USD/JPY et d'AUD/JPY (-1200 pips). | **Dénouement du Carry Trade** | La saisonnalité estivale de range a été balayée par l'effet de levier et le débouclage forcé des fonds spéculatifs mondiaux. |
| **Année 2025** | Tarifs douaniers de Trump & craintes de récession US | Dollar paradoxalement baissier (-10 % sur l'année), l'Or dépasse les 3 000 $. | **Inversion du statut de refuge** | Le dollar a chuté lors des tensions au lieu de monter, car le marché anticipait des baisses de taux agressives de la Fed. |
| **Année 2026** | Supercycle de l'Or (> 4 500 $) & Normalisation de la BoJ | Hausse d'AUD/JPY en avril (+3,2 %, après le cessez-le-feu avec l'Iran du 07/04), légère baisse d'EUR/USD en mai (−0,4 %), **EUR/JPY en légère baisse en juin (−0,2 %)**, dollar en baisse en août. | **Mitigée** | ✏️ *Corrigé : le rapport d'origine parlait d'un « retour d'une saisonnalité très pure » et d'un « rallye d'EUR/JPY en juin ». Juin a échoué. En août, Amirou annonçait une saisonnalité haussière du dollar (#15204) qui n'existe pas dans les statistiques (40 % de hausses), et le dollar a baissé. Pour mai, il annonçait un EURUSD « très très baissier » (#14815) alors que le PDF du projet donne mai haussier (+0,73 %).* |

---

## 🧭 5. Guide Pratique pour l'Utilisateur : Comment Utiliser ces Travaux

Pour exploiter au maximum les 13 rapports PDF et l'analyse historique :

1. **Étape 1 : Consulter le Rapport PDF au début de chaque mois**
   * Identifier la tendance historique (Page 2) : quel est le taux de hausse du mois en cours ? (ex : avril sur AUD/JPY, juillet sur EUR/USD).
   * ✏️ *Précision : c'est un contexte, pas une prévision. Un mois « haussier 5 fois sur 6 » ne l'est l'année suivante que dans environ 51 % des cas.*
2. ~~**Étape 2 : Appliquer la règle temporelle intra-mensuelle (Page 3)**~~ ✏️ **Supprimée.**
   * Le rapport d'origine affirmait que, sur AUD/JPY ou EUR/JPY, le plus haut ou le plus bas du mois se forme « dans la première semaine dans plus de 75 % des cas ».
   * Cette règle vient des messages d'Amirou (#14662, #14907). Les PDF ne la calculent pas.
   * Testée sur 2012-2026 ([`analyses/MASTERCLASS_VERIFIEE.md`](analyses/MASTERCLASS_VERIFIEE.md#4-audjpy-en-avril-et-le--plus-bas-du-mois-en-1re-semaine--t4-14662)), elle donne **50 %** pour AUDJPY en avril, et 45 % sur l'ensemble des mois.
   * Elle ne monte à 72 % que pour les mois qui finissent en hausse, ce qu'on ne sait qu'à la fin du mois.
3. **Étape 3 : Le Filtre Fondamental Impératif**
   * Poser la question clé : *Les banques centrales et l'inflation confirment-elles ou contredisent-elles le biais statistique ?*
   * Si les chiffres d'inflation ou d'emploi contredisent la saisonnalité (comme en avril 2024), **ne forcez pas le trade**.
4. **Étape 4 : Surveiller la Matrice Intermarchés (Page 5)**
   * Toujours vérifier l'orientation du `DXY` et du `PÉTROLE` avant d'engager un trade sur une paire de devises ou une matière première.

---

## 📁 6. Inventaire des Fichiers et Chemins d'Accès

✏️ *Corrigé : le rapport d'origine donnait les chemins de la machine d'Antigravity (`L:\the big T\…`, `C:\Users\dani\.gemini\antigravity\…`). Ses scripts d'extraction n'ont jamais été ajoutés au dépôt et ne sont pas reproductibles. Les chemins ci-dessous sont ceux du dépôt.*

* **Script générateur principal :** [`forex_seasonality_generator.py`](forex_seasonality_generator.py)
* **Les 13 rapports PDF :** [`rapports_pdf/`](rapports_pdf/)
* **Archives Telegram :** [`data/telegram_messages.jsonl`](data/telegram_messages.jsonl) (export complet jusqu'au 01/10/2026 ; l'ancien `ChatExport_2026-09-17/result.json` s'arrête au 17/09/2026)
* **Scripts d'extraction reproductibles :** [`scripts/`](scripts/), décrits dans [`docs/DONNEES_ET_SCRIPTS.md`](docs/DONNEES_ET_SCRIPTS.md)
