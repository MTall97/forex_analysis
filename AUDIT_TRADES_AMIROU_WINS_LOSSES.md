> **Version corrigée le 01/10/2026.** Cet audit a été rédigé par **Antigravity**, l'agent IA utilisé au démarrage du projet. Les erreurs ont été corrigées **dans le texte**. Chaque correction est signalée par ✏️ et expliquée sur place. La version d'origine reste dans l'historique Git (commit `4610e69`). Le détail des vérifications est dans [`docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md`](docs/VERIFICATION_RAPPORTS_ANTIGRAVITY.md).
>
> **Principales corrections** :
> 1. Les chiffres « 167 gains, 41 pertes, 134 BE » n'avaient ni méthode ni fichier source. Les chiffres reproductibles donnent **environ 40 % de TP** parmi les issues annoncées, et non 80 %.
> 2. **Deux des quatre « trades gagnants » n'étaient pas des trades** : le DXY en juillet 2023 et l'or en octobre 2023 sont des commentaires.
> 3. Plusieurs citations avaient été complétées par des phrases qui n'existent pas dans les messages. Elles sont rétablies mot pour mot.

---

# 🎯 AUDIT EXHAUSTIF DES TRADES D'AMIROU (2019 – 2026) : SUCCÈS, ÉCHECS ET ENSEIGNEMENTS

---

## 📌 1. Vue d'Ensemble des Données Extraites
Le canal Telegram *« The halal winning team »* va du **14 mars 2019** au 1er octobre 2026 (14 984 entrées dans l'export du 17/09/2026).

✏️ **Corrigé : bilan des trades.** Le rapport d'origine annonçait 340 cas, dont **167 gains, 41 pertes et 134 BE**, soit 80 % de réussite. Ces chiffres n'avaient aucune méthode ni aucun fichier source, et ne se retrouvent pas. Voici les comptages reproductibles :

| Source | Gains / TP | Pertes / SL | Réussite (gains ÷ gains + pertes) |
|---|---|---|---|
| Messages « TP touché » et « SL touché » ([`scripts/extract_trade_events.py`](scripts/extract_trade_events.py)) | 54 | 72 | 43 % |
| Registre des 281 trades ([`analyses/TRADES_VS_SAISONNALITE.md`](analyses/TRADES_VS_SAISONNALITE.md)) | 24 | 36 | 40 % (et 52 BE, 44 non déclenchés, 125 sans issue connue) |
| Septembres 2019-2026 vérifiés à la main ([`analyses/TRADES_SEPTEMBRE.md`](analyses/TRADES_SEPTEMBRE.md)) | ≈ 29 (dont beaucoup seulement flottants) | 15 à 16 | ≈ 65 % |
| 518 trades lus sur les captures 2021-2026 et rejoués sur les cours ([`analyses/STRATEGIE_ET_MODELE.md`](analyses/STRATEGIE_ET_MODELE.md)) | | | **40 %** pour les trades annoncés à l'avance, 65 % pour ceux publiés après l'entrée |

Les pertes sont sous-déclarées dans le canal : certaines n'apparaissent que sur des captures d'historique.

---

## 🏆 2. Les Trades qui ont Marché (Wins) et POURQUOI

### Cas n°1 : La hausse d'AUD/JPY en avril 2026
* **Date / Message :** 7 avril 2026 (Message #14662)
* ✏️ *Corrigé : le message ne donne **ni gain de « +350 pips », ni entrée, ni résultat**. Amirou commente la hausse : « Regardez l'explosion de audjpy vers le haut conformément à sa saisonnalité ! ». On ne sait pas s'il a pris un trade ni à quel prix. AUD/JPY a fait +3,2 % sur le mois.*
* **Les raisons qu'il donne (#14662) :**
  1. **Saisonnalité :** « Nous savions que c'est un mois haussier ». ✏️ *Corrigé : avril n'est pas « le mois le plus haussier » d'AUD/JPY. Dans le PDF du projet (2020-2025), juin (+2,10 %) devance avril (+1,55 %).*
  2. **Règle de la semaine 1 :** « 75 % du temps, il établit le low du mois dans la première semaine ». ✏️ *Corrigé : c'est l'affirmation d'Amirou, pas un résultat du projet. Testée sur les cours 2015-2024, elle donne **50 %** ([`analyses/MASTERCLASS_VERIFIEE.md`](analyses/MASTERCLASS_VERIFIEE.md)). « Le trade a été acheté exactement à la fin de cette 1re semaine » ne figure pas dans le message.*
  3. Le prix était sur un MLQ.
  3. **Catalyseur Fondamental :** Apaisement des tensions géopolitiques mondiales et retour du sentiment *Risk-On*, propulsant le dollar australien face au Yen.

### ~~Cas n°2 : Le Short Historique du Dollar Index (DXY) en Juillet 2023~~ ✏️ Ce n'était pas un trade
* **Date / Messages :** 5 et 12 juillet 2023 (Messages #8591, #8592, #8635)
* ✏️ *Corrigé : aucun trade n'a été pris. #8591 est un « free game » sur la saisonnalité : « étudier les raisons pour lesquelles le dollar est généralement baissier en juillet et voir si ces conditions sont réunies ». #8592 précise : « Est-ce que cela veut dire qu'il faut vendre le dollar tout de suite ? **Non absolument pas** ». #8635 est un copier-coller de #8591. Il n'y a ni vente du DXY à 103,50, ni entrée, ni résultat.*
* **Ce qui est exact :**
  1. **Saisonnalité :** le dollar a souvent baissé en juillet. ✏️ *Précision : sur 14 ans, EURUSD n'a monté en juillet que 57 % du temps (+0,64 % en moyenne). Le biais est faible, pas « quasi systématique ».*
  2. **Catalyseur Macroéconomique :** La publication d'un CPI américain plus faible que prévu (3.0 % le 12 juillet 2023) a validé le reflux de l'inflation et poussé la Fed vers la fin de son cycle de hausse.
  3. ✏️ *Supprimé : « Amirou a attendu le retest de session pour exécuter, générant une vague de profits massifs ». Aucun message ne le montre.* Le dollar a bien baissé ce mois-là (EURUSD +0,93 %).

### Cas n°3 : Le Swing Trade Vendeur sur CAD/CHF (+200 pips)
* **Date / Messages :** 21 et 24 mars 2019 (Messages #102, #144)
* **Setup :** cassure de la ligne de tendance (#102 : « cadchf just broke the trendline as predicted »).
* **Ce que disent les messages :**
  1. Il conseille d'attendre une confirmation, mais **lui est entré tôt** : « I took the trade early that's why I am already 30 pips in profit ». ✏️ *Corrigé : le rapport d'origine disait l'inverse (« Amirou a refusé de trader la cassure… et a attendu la confirmation en session de Londres »).*
  2. Objectif : « at least 200 pips to get » (#102). Le 24/03, le trade est en profit (#144). ✏️ *Précision : aucun message ne confirme un gain final de 200 pips. Le « +200 pips » est l'objectif annoncé, pas un résultat.*
  3. ✏️ *Supprimé : « stop loss de 25 pips, ratio > 1:8 », « double sommet en H4 », « pétrole / franc suisse ». Rien de tout cela n'est dans les messages.*

### ~~Cas n°4 : Le Breakout Fondamental de l'Or (XAU/USD) en Octobre 2023~~ ✏️ Ce n'était pas un trade
* **Date / Message :** 28 octobre 2023 (Message #9670)
* ✏️ *Corrigé : #9670 est un **sermon** sur l'analyse fondamentale, sans entrée, sans stop et sans résultat. Le message dit, mot pour mot : « Pendant que vous êtes là en train de vous casser la tête si l'or va monter ou pas de façon technique, quelqu'un d'autre a les faits sous la main et sait avec certitude que l'or va partir à la hausse à cause des tensions géopolitiques. » La citation du rapport d'origine avait été réécrite pour lui faire dire « l'or va partir à la hausse avec certitude ».*
* Le contexte de marché est exact : l'or est passé d'environ 1 810 $ à plus de 2 000 $ après le 7 octobre 2023.

---

## ❌ 3. Les Trades qui ont Échoué (Losses) et POURQUOI

### Échec n°1 : Le Short d'AUD/USD lors de la Faillite de SVB (Mars 2023)
* **Date / Messages :** trade déclenché le 16 mars 2023 (#7713), stop touché le 17 mars (#7718) ; #7721 est le récapitulatif macro. ✏️ *Corrigé : le rapport d'origine ne citait que #7721.*
* **Setup Initial :** Vente d'AUD/USD.
* **Pourquoi il a échoué (Stop Loss touché) :**
  1. **Choc Exogène Bancaire (Risk-Off Déformé) :** La faillite surprise de Silicon Valley Bank (SVB) et le sauvetage du Credit Suisse par la BNS ont provoqué une chute violente des anticipations de taux de la Fed.
  2. **Surprise Statistique Australienne :** Le taux de chômage australien est sorti bien meilleur que prévu le même jour, propulsant le dollar australien à la hausse.
  3. **Enseignement d'Amirou (#7718) :** « Il faut admettre que la probabilité de ce trade avait changé depuis ce matin, c'est pourquoi j'observais le sentiment général du marché. » ✏️ *Corrigé : « probabilité de perte à 80 % » et « il a réduit son exposition avant de couper, sauvant le capital du groupe » ne figurent dans aucun message. Le stop a été touché.*

### Échec n°2 : L'Achat d'EUR/USD en Avril 2024 (La Saisonnalité Faussée)
* **Date / Message :** 10 avril 2024 (Message #10946)
* **Setup Initial :** Achat basé sur la saisonnalité haussière d'avril sur l'euro. ✏️ *Précision : le 05/04/2024, Amirou avait déjà basculé vendeur : « Hier on était haussier et aujourd'hui on fausse la saisonnalité en étant baissier » (#10892). Le biais d'avril était faible : 60 % de hausses, +0,29 % en moyenne. Le mois a fini à −0,99 %.*
* **Pourquoi il a échoué :**
  1. **Persistance de l'Inflation US :** Le CPI américain est ressorti à 3.5 % (plus haut qu'attendu pour le 3e mois d'affilée).
  2. **Repoussement des Baisses de Taux Fed :** Les investisseurs ont repoussé la première baisse de la Fed de juin à septembre/décembre, provoquant un rallye imprévu du Dollar.
  3. **Enseignement d'Amirou (#10946), mot pour mot :** *« Pour l'histoire : vous allez noter dans votre playbook que Eurusd a faussé sa saisonnalité en 2024 car l'inflation a persisté et le marché de l'emploi était résilient. La Fed n'avait donc aucune raison de faire tomber les taux d'intérêt. »* ✏️ *Corrigé : la phrase « En période de conflit macro, les fondamentaux écrasent toujours les stats saisonnières » n'existe pas dans le message ; elle avait été ajoutée.*

### Échec n°3 : La Vente sur GBP/JPY (Septembre 2019) – La Chasse aux Stops
* **Date / Messages :** stop touché le 20 septembre 2019 (#1214), commenté le 22 septembre (#1239)
* **Setup Initial :** Vente sur cassure de support.
* **Pourquoi il a échoué temporairement :**
  1. **Manipulation institutionnelle :** Les market makers ont poussé le prix au-delà du support pour déclencher les stop loss des vendeurs particuliers avant de s'effondrer exactement dans la direction prévue.
  2. **Enseignement d'Amirou (#1239) :** « Les market makers ont manipulé le prix mais c'est pas grave. Nous prendrons position lorsque le 2e support est cassé. » ✅ *Fidèle.* À noter : septembre 2019 a été un mois de forte hausse des paires en yen (GBPJPY +2,9 %). Sept ventes ont touché leur stop en trois semaines ([`analyses/TRADES_SEPTEMBRE.md`](analyses/TRADES_SEPTEMBRE.md)).

### Échec n°4 : Période Trump de Décembre 2025 – Janvier 2026
* **Date / Message :** 11 février 2026 (Message #14412)
* **Contexte :** Série de trades touchant le Stop Loss ou clôturés à Break-Even sur des setups pourtant classés « A+ ».
* **Pourquoi ils ont échoué :**
  1. **Ce qu'il écrit (#14412) :** « Les agissements de Donald Trump étaient hostiles à ma méthodologie, nous trouvant 22 h dans un trade qui finit par toucher BE, ou bien un excellent setup A+ qui finissait SL. » ✏️ *Précision : le détail « surtaxes douanières sur le Japon et l'Europe » est un ajout d'Antigravity ; le message ne le mentionne pas.*
  2. **Enseignement d'Amirou :** Ne jamais tenter de « forcer » le marché pour se refaire. Réduire la taille de position, encaisser les petits BE, et attendre le retour de la liquidité saine.

---

## 🧠 4. Les Règles d'Or du Playbook d'Amirou face aux Pertes et aux Gains

1. **La règle « Money likes speed » (#13746, 26/08/2025) :**
   * Mot pour mot : *« Si le setup est vraiment bon et que le marché a le même état d'esprit que moi, normalement le prix doit exploser à la hausse vers mon tp en moins de 5 h de temps. »* ✏️ *La citation d'origine était une paraphrase.*
   * ✏️ *Ce que montrent les données : sur ses trades annoncés et gagnants, le TP est atteint en **29 h** en médiane ; seuls 10 % des TP arrivent en moins de 5 h ([`analyses/STRATEGIE_ET_MODELE.md`](analyses/STRATEGIE_ET_MODELE.md)).*
2. **Le concept psychologique « Unfazed » (#7823, 06/04/2023 : « J'ai inclus le mot Unfazed dans mon dictionnaire ») :**
   * ✏️ *Précision : la suite (« 3 à 5 pertes », « 1 % à 2 % ») est une interprétation d'Antigravity ; elle ne figure pas dans ce message.* Face à une série de 3 à 5 pertes consécutives, ne jamais douter de son système si celui-ci a été backtesté sur des milliers d'heures. L'accumulation de petites pertes maîtrisées (1 % à 2 %) est le coût normal pour attraper les vagues à 1:5 ou 1:10.
3. **Le piège des setups « trop évidents »** ✏️ *(non sourcé : aucun message n'est cité)* **:**
   * Un double sommet ou un niveau de support visible par tous les débutants sur YouTube a une très forte probabilité d'être d'abord manipulé par les market makers avant de partir. Amirou conseille de n'y risquer que 1 % maximum.
