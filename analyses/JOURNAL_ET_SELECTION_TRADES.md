# Journal des trades des stratégies, et sélection des trades à partir des gagnants et des perdants

*14/10/2026 — scripts : `scripts/journal_trades_strategies.py` (journal), `scripts/tester_selection_trades.py` (sélection).*

## 1. Le journal, trade par trade

Le dossier `data/journal_trades/` contient un fichier par stratégie, avec une ligne par trade. Chaque ligne donne :
- la paire, le sens et le signal ;
- l'entrée (date, heure, prix), le stop et l'objectif ;
- la sortie (date, heure, prix, motif : objectif, stop, échéance ou « en cours ») ;
- le résultat en R, spread déduit.

Chaque trade peut ainsi être vérifié sur un graphique. Les variantes sont celles des rapports, et leurs règles n'ont pas été changées.

| Fichier | Stratégie | Cours | Trades | Gagnants | R moyen |
|---|---|---|---|---|---|
| `englobante_mlq_horaire.csv` | englobante + MLQ, objectif 2 R, sortie au plus tard à J+3 | Yahoo horaire, 22 paires, 12/2023-10/2026 | 767 | 48 % | +0,10 |
| `englobante_mlq_journalier.csv` | même règle | Dukascopy journalier, 10 paires, 2012-2026 | 1 973 | 44 % | +0,00 |
| `cassure_retour_mlq.csv` | cassure puis retour sur MLQ, stop 0,5 ATR, objectif 2 R | Yahoo horaire, 22 paires, 2024-2026 | 3 948 | 36 % | +0,01 |
| `suivi_tendance.csv` | cassure du plus haut ou du plus bas de la veille dans le sens de la tendance (≥ 1 ATR sur 5 jours), stop 0,25 ATR, objectif 1 R, sortie à 20h | Yahoo horaire, 22 paires, 2024-2026 | 3 487 | 48 % | −0,13 |

Les chiffres retrouvent ceux des rapports. Les quelques trades supplémentaires viennent des cours d'octobre 2026, ajoutés depuis.

**Conventions** :
- toutes les heures sont en UTC ;
- l'heure d'une bougie horaire est celle de son ouverture : « 14:00 » désigne la bougie de 14h à 15h ;
- l'englobante est prise à la clôture de la bougie journalière, soit « 24:00 » UTC ;
- le journalier Dukascopy ne donne que le jour de sortie ;
- si une même bougie touche le stop et l'objectif, le stop compte (`r`) ; `r_optimiste` donne l'inverse ;
- les prix sont ceux de Yahoo ou de Dukascopy, et peuvent différer de quelques pips de ceux d'un courtier.

Exemples récents :

| Stratégie | Paire | Entrée (UTC) | Prix | Stop | Objectif | Sortie (UTC) | Prix | Motif | R |
|---|---|---|---|---|---|---|---|---|---|
| englobante + MLQ | EURUSD vente | 07/10/2026 24:00 (clôture) | 1.12032 | 1.12595 | 1.10908 | 12/10 23:00 (clôture) | 1.11632 | échéance | +0,70 |
| englobante + MLQ | AUDUSD vente | 07/10/2026 24:00 (clôture) | 0.69648 | 0.69882 | 0.69179 | 09/10 05:00 | 0.69882 | stop | −1,04 |
| suivi de tendance | EURGBP vente | 12/10/2026 07:00 | 0.84549 | 0.84618 | 0.84480 | 12/10 09:00 | 0.84480 | objectif | +0,83 |

Chaque ligne contient aussi les variables connues au moment de l'entrée, qui servent à la partie 2 :
- tendance sur 5 et 20 jours ;
- volatilité relative ;
- position dans le range de 60 jours ;
- risque en ATR ;
- jour et heure ;
- narratif écrit d'Amirou sur 14 jours ;
- écart de COT et écart de taux directeurs.

## 2. Peut-on choisir les bons trades en apprenant des gagnants et des perdants ?

### Le piège
En regardant les trades déjà joués, on trouve **toujours** des conditions qui séparent les gagnants des perdants : telle paire, tel jour, telle tendance. Mais une partie de ces différences est due au hasard. Elle ne se reproduira pas.

Le seul test honnête consiste à **choisir les règles avec le passé, puis les appliquer à des trades qu'on n'a pas encore vus**. Ici, le test se fait trimestre par trimestre : le modèle n'apprend que sur les trades terminés avant le début du trimestre, avec 7 jours de marge, puis choisit parmi les trades du trimestre. C'est un test « walk-forward ».

Trois façons de choisir ont été comparées :
- **« meilleures paires du passé »** : garder les couples paire × sens dont le R moyen passé est positif (au moins 10 trades). C'est ce qu'on fait en regardant ses trades à la main ;
- **régression linéaire** : elle prédit le R de chaque trade à partir des variables ; on garde les trades dont la prédiction est positive ;
- **arbres de décision** (gradient boosting peu profond) : même principe, avec un modèle capable de trouver des combinaisons de conditions.

### Résultats

R moyen par trade, spread déduit, ± erreur type :

| Stratégie | Méthode | Après coup : trades gardés | Hors échantillon : tous les trades | Hors échantillon : trades gardés |
|---|---|---|---|---|
| englobante + MLQ, journalier (test 2016-2026) | meilleures paires | +0,08 | +0,04 | +0,11 ± 0,06 |
| | régression | +0,13 | +0,04 | +0,01 ± 0,05 |
| | arbres | **+0,46** | +0,04 | +0,04 ± 0,05 |
| englobante + MLQ, horaire (test 2025-2026) | meilleures paires | +0,24 | +0,13 | +0,10 ± 0,11 |
| | régression | +0,25 | +0,13 | +0,15 ± 0,08 |
| | arbres | **+0,58** | +0,13 | +0,17 ± 0,08 |
| cassure puis retour MLQ, horaire (test 2025-2026) | meilleures paires | +0,17 | +0,03 | +0,08 ± 0,05 |
| | régression | +0,20 | +0,03 | +0,07 ± 0,05 |
| | arbres | **+0,46** | +0,03 | +0,03 ± 0,05 |
| suivi de tendance 1 R, horaire (test 2025-2026) | meilleures paires | +0,07 | −0,14 | −0,12 ± 0,06 |
| | régression | +0,09 | −0,14 | −0,09 ± 0,05 |
| | arbres | **+0,36** | −0,14 | −0,13 ± 0,06 |

Détail, avec le nombre de trades gardés et le R des trades rejetés : `data/selection_trades/resultats.csv`.

### Ce qu'il faut en retenir
- **Après coup, n'importe quelle stratégie paraît gagnante.** Le suivi de tendance passe de −0,13 R à +0,36 R par trade, et l'englobante horaire à +0,58 R. C'est l'illusion classique de l'optimisation : le modèle a appris les trades par cœur.
- **Sur des trades non vus, l'amélioration fond.** L'écart avec « prendre tous les trades » est compris entre −0,03 et +0,07 R, toujours à environ une erreur type ou moins. Sur 12 essais, quelques écarts positifs de cette taille sont attendus par hasard.
- **Le cas le moins décevant est « garder les paires qui ont marché »**, sur l'englobante journalière (+0,07 R) et sur la cassure-retour (+0,05 R). Il n'est pas significatif. La régression et les arbres ne font pas mieux sur ces mêmes stratégies, ce qui ressemble davantage à du bruit qu'à un effet stable.
- **Le suivi de tendance reste perdant**, quelle que soit la sélection.

En résumé, sélectionner les trades à partir des gagnants et des perdants du passé ne crée pas d'avantage là où la règle n'en a pas. Cela peut au mieux ajouter quelques centièmes de R, au prix de beaucoup moins de trades. Une sélection qui paraîtrait très bonne sur l'historique ne serait crédible qu'après une période de suivi en démo, avec une règle figée, comme pour `analyses/SUIVI_DEMO.md`.

## Limites
- Les variables testées sont simples : tendance, volatilité, calendrier, narratif écrit, COT, taux. Une autre information, comme le contexte d'annonce ou la structure intrajournalière, pourrait aider. Mais chaque variable ajoutée augmente aussi le risque de trouver un effet par hasard.
- Les périodes hors échantillon en horaire sont courtes (7 trimestres, 2025-2026).
- Le test sur une seule paire reste peu fiable : une paire compte 20 à 200 trades.
