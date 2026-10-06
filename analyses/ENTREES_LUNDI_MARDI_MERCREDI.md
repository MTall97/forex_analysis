# Lundi-mardi-mercredi (« trois barres ») : peut-on améliorer l'entrée ?

*Rédigé le 06/10/2026, à la demande de l'utilisateur. Script : [`scripts/tester_entrees_lmm.py`](../scripts/tester_entrees_lmm.py) ; résultats : [`data/lmm_entrees/`](../data/lmm_entrees/). Même démarche que pour l'englobante ([`ENGLOBANTE_FVG.md`](ENGLOBANTE_FVG.md)).*

## La règle (inchangée, T2 de [`MASTERCLASS_VERIFIEE.md`](MASTERCLASS_VERIFIEE.md))

En vente (l'achat est symétrique) :
- **lundi** haussier « plein » : corps ≥ 60 % du range, clôture dans le quart haut ;
- **mardi** rouge, qui clôture sous la clôture du lundi ;
- **stop** 2 pips au-dessus du plus haut du mardi ; **objectif** : plus bas du lundi ; **sortie** au plus tard à la clôture du vendredi ;
- **filtre de la masterclass** : au moins 60 pips jusqu'à l'objectif et RR ≥ 1,2, calculés avec l'entrée à la clôture du mardi.

## Les entrées comparées

Mêmes signaux, même stop, même objectif ; seul le prix d'entrée change, et le R est recalculé depuis l'entrée réelle.

| Entrée | Principe |
|---|---|
| **Clôture du mardi** | référence (règle testée jusqu'ici) |
| Londres 07h | au marché le mercredi à 07h UTC |
| Repli 30 % (24 h) | ordre limite à 30 % de la distance entrée-stop, valable le mercredi |
| FVG 4h du mardi (24 h) | ordre limite au bord du FVG 4h le plus récent du mardi, non comblé |
| Repli 30 % la nuit, sinon Londres | ordre limite entre 00h et 07h ; sinon entrée au marché à 07h (aucun signal raté) |
| FVG 4h la nuit, sinon Londres | même chose avec le FVG 4h |
| Ordre stop au-delà du mardi | vente : ordre stop sous le plus bas du mardi, valable le mercredi (confirmation) |
| Confirmation 1h | à la clôture de la première bougie 1h (mercredi ou jeudi) sous le plus bas du mardi |

**Données** : cours horaires Yahoo, 22 paires, de décembre 2023 à octobre 2026 ; stop prioritaire dans une même heure ; spread déduit ; un ordre non exécuté compte 0 R. L'écart avec la référence est calculé signal par signal.

## Résultats

**Avec le filtre de la masterclass (88 signaux)** :

| Entrée | Trades | Gagnants | R par signal | Écart avec la clôture (± erreur type) |
|---|---|---|---|---|
| **Clôture du mardi** | 88 | 43 % | **+0,39** | — |
| Repli 30 % la nuit, sinon Londres | 88 | 44 % | +0,37 | −0,02 (±0,10) |
| Repli 30 % (24 h) | 72 | 35 % | +0,36 | −0,03 (±0,14) |
| Ordre stop au-delà du mardi | 49 | 73 % | +0,25 | −0,13 (±0,14) |
| Confirmation 1h | 44 | 82 % | +0,20 | −0,19 (±0,15) |
| Londres 07h | 88 | 44 % | +0,16 | **−0,23 (±0,11)** |
| FVG 4h du mardi (24 h) | 7 | 86 % | +0,15 | −0,24 (±0,19) |
| FVG 4h la nuit, sinon Londres | 88 | 44 % | +0,14 | −0,25 (±0,10) |

**Toutes les configurations, sans le filtre (348 signaux)** : clôture du mardi +0,09 R ; toutes les autres entrées entre −0,02 et +0,08 R, soit un écart de −0,01 à −0,11 R avec la clôture.

- **Aucune entrée ne fait mieux que la clôture du mardi**, avec ou sans filtre.
- **Attendre le mercredi matin coûte cher** : −0,23 R en entrant à Londres. Le prix part souvent dans le sens du trade pendant la nuit de mardi à mercredi.
- **Les confirmations (ordre stop, clôture 1h) gagnent plus souvent** (73-82 % de gagnants), mais sur la moitié des signaux seulement et avec un ratio plus petit : elles rapportent moins par signal.
- **Le FVG 4h du mardi n'est presque jamais retouché** (7 fois sur 88) : quand la configuration fonctionne, le prix ne revient pas.

## Attention au +0,39 R

- Sur ces 2,8 ans, la règle à la clôture du mardi fait +0,39 R par signal, mais avec une erreur type de ±0,19, et de façon très inégale : **−0,11 R en 2024**, +0,61 R en 2025, +0,52 R en 2026.
- Sur 2012-2026 en journalier (Dukascopy, 11 instruments), la même règle faisait **−0,05 R** sur 311 trades. La bonne période récente ne suffit pas à en faire une stratégie : c'est la même mise en garde que pour GBPUSD depuis 2024 dans [`MASTERCLASS_VERIFIEE.md`](MASTERCLASS_VERIFIEE.md).

## Ce qu'il faut retenir

1. **Comme pour l'englobante, l'entrée à la clôture de la bougie signal (ici le mardi) reste la meilleure** des entrées testées.
2. Les replis, les FVG et les confirmations font gagner plus souvent ou améliorent le ratio affiché, mais ils ratent ou retardent les trades qui partent tout de suite, et ce sont eux qui paient.
3. S'il existe un avantage, il faut le chercher dans le choix des signaux (filtres) ou dans la gestion de la sortie, pas dans le point d'entrée.

## Relancer

```
python scripts/prix_yahoo.py --mettre-a-jour
python scripts/tester_entrees_lmm.py
```
