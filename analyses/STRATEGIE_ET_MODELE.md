# La stratégie d'Amirou : description, performance réelle, et peut-on la copier ?

> **Données** :
> - 2 758 captures (TradingView et photos, 2021-2026) lues par OCR : [`scripts/lire_captures_ocr.py`](../scripts/lire_captures_ocr.py), puis [`scripts/resoudre_niveaux.py`](../scripts/resoudre_niveaux.py) ;
> - chaque trade rejoué sur les cours réels (Yahoo Finance : horaire depuis décembre 2023, journalier avant) : [`scripts/simuler_trades_dukascopy.py`](../scripts/simuler_trades_dukascopy.py) ;
> - version algorithmique de la méthode : [`scripts/algo_amirou_backtest.py`](../scripts/algo_amirou_backtest.py) ;
> - modèle d'IA : [`scripts/modele_meta.py`](../scripts/modele_meta.py).
>
> **Fichiers produits** : [`data/captures_trades.csv`](../data/captures_trades.csv), [`data/trades_simules.csv`](../data/trades_simules.csv), [`data/backtest_algo.csv`](../data/backtest_algo.csv), [`data/meta_features.csv`](../data/meta_features.csv).

## 1. La stratégie telle qu'il l'enseigne

### Les concepts, année par année (nombre de messages qui les citent)
| Concept | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| Wyckoff (accumulation, spring, redistribution) | 6 | 20 | **39** | 25 | 15 | 7 | 9 | 4 |
| Smart money / order blocks | 7 | 1 | 19 | **25** | 15 | 18 | 6 | 0 |
| Zones d'offre et de demande | 18 | 29 | 18 | 16 | **40** | 28 | 35 | 20 |
| Quarter points / niveaux ronds | 0 | 0 | 1 | **21** | 8 | 9 | 6 | 2 |
| « Price & Time » | 0 | 0 | 0 | 3 | 16 | **27** | 4 | 3 |
| Sessions (Londres, New York) | 41 | 24 | 23 | 24 | 55 | 93 | **95** | 29 |
| Analyse fondamentale | 3 | 2 | 18 | 31 | **121** | 57 | 82 | 26 |
| Sentiment / COT | 0 | 2 | 0 | 7 | 21 | 21 | **74** | 31 |
| Annonces (NFP, CPI, taux) | 3 | 2 | 10 | 23 | 59 | **65** | 57 | 20 |
| Saisonnalité | 0 | 0 | 0 | 0 | **15** | 7 | 5 | 4 |
| Playbook / statistiques | 20 | 13 | 6 | 10 | 51 | **56** | 48 | 27 |

**Trois époques** :
- **2019-2020** : analyse technique pure (supports et résistances, figures, offre et demande) et signaux « sell now at market price ».
- **2021-2022** : Wyckoff, smart money et quarter points, avec des stops de quelques pips et des ratios de 1:10 à 1:20.
- **2023-2026** : l'analyse fondamentale et le sentiment passent au premier plan (« fondamentale 40 %, sentiment 25 %, technique 25 %, price action 10 % », #15478), avec la saisonnalité et le « Price & Time ». Les stops s'élargissent (≈ 40-50 pips) et les ratios redescendent vers 1:2 à 1:3.

### Ses règles écrites
| Règle | Message |
|---|---|
| Ratio d'au moins 1:2,5, puis « minimum 1:3, jusqu'à 1:15-1:20 » | #168 (2019), #2647 (2020) |
| Trader les sessions de Londres et de New York ; un setup peut « se déclencher après 14h » | #188, #15279, #15280 |
| Mettre le stop à l'entrée (BE) dès que possible (« à 50 pips de profit », puis « mettez-vous à BE maintenant ») | #1196, #1203, #15407 |
| « Money likes speed » : objectif en moins de 5 h, sinon sortie 2 h après l'ouverture de New York | #13746 |
| Entrer après une **prise de liquidité** ou une manipulation (le prix va chercher les stops avant de partir) | #470, #1133, #4755 |
| Niveaux de référence : quarter points, open hebdomadaire, mensuel ou annuel, minuit à New York | #6443, #10894, #11057 |
| Pas de trade juste avant une annonce majeure ; trader la réaction (« buy the rumor, sell the news ») | #11943, #15322 |
| Risque de 0,5 à 2 % par trade | #1198, #15360, #15530 |
| Jours : « mardi, mercredi, jeudi », plus tard « le jeudi je touche souvent SL ou BE » | #595, #14517 |

## 2. Sa performance réelle, mesurée sur les captures

**518 trades** ont été lus avec leur entrée, leur stop et leur objectif sur les captures de 2021-2026 (paire vérifiée par le prix réel du jour), puis rejoués sur les cours.

| Classement | Trades |
|---|---|
| **Annoncés à l'avance** (le prix n'avait pas encore dépassé l'entrée) | 350 |
| ↳ objectif atteint | 99 |
| ↳ stop touché | 147 |
| ↳ jamais déclenchés (objectif atteint sans passer par l'entrée, ou entrée jamais touchée) | 102 |
| ↳ encore ouverts après 20 jours | 2 |
| **Publiés après coup** (entrée déjà touchée, ou objectif déjà dépassé, au moment de la publication) | 126 |
| Lecture incohérente avec le prix (prix déjà au-delà du stop) | 42 |

**Sur les 246 trades annoncés et terminés : 40 % d'objectifs atteints.** Le registre texte du canal donnait le même 40 %, ce qui valide les deux méthodes.

| Année | Trades | Réussite | Stop médian | Espérance nette du spread | Hors ratios > 8 |
|---|---|---|---|---|---|
| 2021 | 58 | 40 % | 10 pips | +2,79 R | +0,15 R |
| 2022 | 33 | 30 % | 16 pips | +0,69 R | +0,60 R |
| 2023 | 62 | 43 % | 50 pips | +0,83 R | +0,93 R |
| 2024 | 28 | 32 % | 51 pips | **−0,09 R** | −0,05 R |
| 2025 | 36 | 44 % | 40 pips | +0,40 R | +0,44 R |
| 2026 | 31 | 48 % | 40 pips | +0,22 R | +0,26 R |
| **Total** | **248** | **40 %** | 31 pips | +1,03 R | **+0,47 R** |

**À retenir :**
- **Ses plans publiés à l'avance ont une espérance positive** : environ +0,4 à +0,9 R par trade en 2022-2026, spread déduit. C'est un vrai avantage, mais modeste. 2024 est à l'équilibre.
- **Les chiffres de 2021 sont gonflés par quelques trades à ratio extrême** (stop de 2 à 10 pips, objectif de 1:10 à 1:23), simulés en bougies journalières. En retirant les ratios supérieurs à 8, l'espérance de 2021 tombe à +0,15 R.
- **Série la plus longue : 14 stops d'affilée.** À 1 % de risque, cela fait −14 % sur le compte ; à 2 %, −26 %.
- **Le BE compte** : 46 des 147 stops avaient d'abord été en gain latent d'au moins 1 R. Avec la règle « BE à 1 R », l'espérance passe de +1,12 à +1,29 R (avant spread).
- **126 captures sur 518 (24 %) sont publiées après l'entrée**, et 26 alors que l'objectif était déjà dépassé. Le taux de réussite y est de 65 %, contre 40 % pour les trades annoncés à l'avance : c'est l'effet vitrine déjà relevé dans le canal.

## 3. Peut-on le copier avec un algorithme ?

J'ai traduit ses règles écrites en algorithme : prise de liquidité sur le plus haut ou le plus bas de la veille, retour dans le range, sessions de Londres et New York, sens de la tendance, saisonnalité en option, objectif 2,5 R, BE à 1 R. Backtest sur 13 paires en données horaires, de décembre 2023 à septembre 2026, spread déduit :

| Variante | Trades | Gagnants | Espérance | Total |
|---|---|---|---|---|
| Tendance seule | 2 393 | 28 % | −0,17 R | −410 R |
| Tendance + BE à 1 R | 2 393 | 19 % | −0,17 R | −412 R |
| Tendance + saisonnalité | 714 | 28 % | −0,16 R | −117 R |
| Tendance + saisonnalité + BE | 714 | 18 % | −0,21 R | −147 R |

**Les règles écrites, appliquées mécaniquement, perdent de l'argent.** L'avantage d'Amirou ne tient donc pas à la figure technique elle-même. Il vient de ce qui ne s'écrit pas en règle : le choix du jour (quelle annonce, quel sentiment), de la paire et du niveau.

## 4. Peut-on l'imiter avec un modèle d'IA ?

J'ai entraîné un modèle (régression logistique et gradient boosting) sur ses 246 trades annoncés et terminés. Les variables sont toutes connues au moment de la publication : ratio, taille du stop (en pips et en ATR), heure et session, jour, mois, tendance, saisonnalité, distance à un niveau rond, paire, sens. Il apprend sur le passé et est testé sur l'année suivante (2023, 2024, 2025, 2026).

| Modèle | AUC hors échantillon | Moitié jugée la meilleure | Moitié écartée |
|---|---|---|---|
| Régression logistique | 0,49 | +0,23 R | +0,64 R |
| Gradient boosting | 0,53 | +0,33 R | +0,53 R |

**Le modèle ne fait pas mieux que le hasard** (0,50). Rien dans le contexte observable ne permet de prévoir lesquels de ses trades vont gagner. Quelques tendances brutes, sur de petits échantillons et donc à ne pas exploiter seules :
- les trades publiés la nuit ou en session asiatique rapportent nettement moins (+0,28 R contre +1,36 R) ;
- aller contre la tendance de 20 jours ne pénalise pas, comme sa méthode de « retournement » le suppose ;
- la saisonnalité ne change rien (+0,94 R dans son sens, +1,10 R contre) ;
- les petits ratios (moins de 2,5) gagnent plus souvent (55 %) mais rapportent peu (+0,31 R).

**Pourquoi l'IA échoue ici** :
- 246 exemples, c'est très peu ;
- son choix repose sur une lecture macro et du sentiment (annonces, discours, positionnement) qui n'est pas dans les données de prix ;
- ses méthodes ont changé trois fois en six ans.

## 5. Conclusion et pistes réalistes
1. **Copier ses signaux** (et non sa méthode) a eu une espérance positive mais faible (≈ +0,4 R par trade sur 2022-2026), avec des séries de 14 pertes. Seule une taille de position prudente (0,5 % comme il le recommande désormais) le rend supportable. Il faut aussi exécuter exactement le plan annoncé, l'ordre limite compris, puisque 102 trades sur 350 ne se sont jamais déclenchés.
2. **Un robot qui reproduirait sa méthode à partir des seules règles techniques n'est pas viable** : le backtest est perdant.
3. **Pour aller plus loin avec l'IA**, il faudrait d'autres données que les prix :
   - le calendrier économique avec le consensus et la surprise de chaque annonce ;
   - le positionnement (COT) ;
   - le texte de ses rapports SignalX, qu'un modèle de langage pourrait transformer en biais par devise (haussier ou baissier) ;
   - puis un test de ce biais sur la période suivante.

   C'est la partie fondamentale et sentiment de sa méthode (65 % du poids selon lui), justement celle qui manque ici.
4. **Limites de cette étude** :
   - cours Yahoo en BID sans spread variable : la simulation déduit un spread fixe, mais le courtier d'Amirou peut différer de quelques pips (« raté de 3 pips ») ;
   - données journalières avant décembre 2023 : quand l'objectif et le stop sont touchés le même jour, on compte un stop ;
   - l'OCR n'a reconstitué que les captures avec l'outil de position lisible, environ un quart des captures.
