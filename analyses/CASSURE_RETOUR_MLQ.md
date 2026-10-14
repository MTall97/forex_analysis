# « Cassure puis retour sur le MLQ » : la règle d'octobre 2026 testée

*Rédigé le 14/10/2026, à la demande de l'utilisateur. Script : [`scripts/tester_cassure_retour_mlq.py`](../scripts/tester_cassure_retour_mlq.py) ; résultats : [`data/cassure_retour_mlq/`](../data/cassure_retour_mlq/).*

## La règle

C'est celle qui ressort des trades d'Amirou d'octobre 2026 ([`OCTOBRE_2026.md`](OCTOBRE_2026.md)) et de sa vidéo « setup 3 » : « le prix avait cassé sous une zone que les institutions surveillaient […] il remonte exactement dessus. C'est là que je place ma vente. » Ses entrées d'octobre sont toutes sur des multiples de 250 pips : 1,6250, 157,50, 0,8500, 2,0000, 1,1250, 1,9000, 210,000.

Version testée (vente ; l'achat est symétrique), fixée avant de lancer le test :
- **niveau** : multiple de 250 pips (MLQ) ;
- **cassure** : une bougie clôture sous le niveau alors que la précédente clôturait au-dessus ;
- **confirmation** : le prix s'éloigne d'au moins 0,3 ATR(14) journalier sous le niveau dans les 48 heures, sans reclôturer au-dessus ; sinon la cassure est abandonnée ;
- **entrée** : ordre de vente limite sur le niveau, valable 5 jours ;
- **stop** : 0,35 ou 0,5 ATR au-dessus du niveau (25 à 50 pips sur les paires principales, comme ses stops) ;
- **objectif** : 1, 2 ou 3 R ; sortie au plus tard 5 jours après l'entrée ; spread déduit.

**Témoin** : la même règle sur des niveaux décalés de 125 pips (1,1375, 1,1625…), des niveaux sans aucune signification. Si le MLQ compte, il doit faire nettement mieux.

**Cours** :
- horaire Yahoo, 22 paires, décembre 2023 - octobre 2026 (rejeu principal, environ 3 900 configurations par groupe) ;
- journalier Dukascopy, 10 paires, 2012-2026, pour vérifier sur la durée. En journalier, quand une même bougie touche le stop et l'objectif, l'ordre est inconnu : le résultat est donné avec le stop d'abord.

## Résultats

**Horaire, 22 paires, 2024-2026** (R moyen par trade, ± erreur type) :

| Stop | Objectif | MLQ | Niveaux décalés (témoin) |
|---|---|---|---|
| 0,35 ATR | 1 R | −0,02 (52 % gagnants) | −0,04 |
| 0,35 ATR | 2 R | −0,02 | −0,05 |
| 0,35 ATR | 3 R | −0,00 | −0,09 |
| 0,5 ATR | 1 R | +0,00 | −0,02 |
| 0,5 ATR | 2 R | +0,01 (±0,02) | −0,04 |
| 0,5 ATR | 3 R | +0,02 (±0,03) | −0,05 |

- **Le MLQ fait à peine mieux que des niveaux pris au hasard** : +0,055 R d'écart (stop 0,5 ATR, objectif 2 R), avec une erreur type de ±0,032. Ce n'est pas significatif.
- **Pas de façon stable** : 2024 −0,01 R, 2025 +0,08 R, 2026 −0,06 R, contre −0,05, −0,05 et −0,03 R pour le témoin. En 2026, le témoin fait mieux.
- **Les ventes, celles d'octobre, perdent** : −0,05 R (contre +0,08 R pour les achats). Le témoin montre le même écart (−0,10 contre +0,02) : il vient de la tendance de la période, pas du niveau.

**Journalier, 10 paires, 2012-2026** (stop 0,5 ATR, objectif 2 R, stop compté d'abord) :

| Période | MLQ | Niveaux décalés (témoin) |
|---|---|---|
| 2012-2019 | −0,10 (1 430 trades) | −0,04 (1 525) |
| 2020-2026 | −0,04 (1 207) | −0,06 (1 254) |

Sur quinze ans, le MLQ ne fait pas mieux que le témoin, et fait même moins bien sur 2012-2019.

## Ce qu'il faut retenir

1. **La cassure puis le retour sur un MLQ n'a pas d'avantage mesurable** : à peu près zéro, comme des niveaux sans signification, sur 2024-2026 en horaire comme sur 2012-2026 en journalier.
2. **Ce qui faisait la différence dans les trades d'Amirou n'est pas le niveau.** S'il y a un avantage, il vient du choix du sens (son « narratif » : euro faible, yen acheté avant une intervention, réaction au NFP), que cette règle mécanique ne reproduit pas, et du choix des trades montrés (8 sur 11 publiés après coup en octobre).
3. Le seul usage du MLQ qui reste positif est **l'achat sur englobante qui touche un MLQ, depuis 2020** ([`ENGLOBANTE_MLQ_ET_SUIVI_TENDANCE.md`](ENGLOBANTE_MLQ_ET_SUIVI_TENDANCE.md)), toujours suivi en démo.
4. **Limites** :
   - 2,8 ans de cours horaires ;
   - la confirmation (0,3 ATR en 48 heures) et la durée de validité de l'ordre (5 jours) sont des choix raisonnables mais arbitraires ;
   - le sens fondamental choisi par Amirou n'est pas testable sans un historique de ses analyses, qui n'existe que pour quelques trades.

## Relancer

```
python scripts/tester_cassure_retour_mlq.py
```
