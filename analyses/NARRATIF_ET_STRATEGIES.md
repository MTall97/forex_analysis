# Le narratif d'Amirou ajouté à ses stratégies

*Rédigé le 14/10/2026, à la demande de l'utilisateur. Script : [`scripts/tester_narratif_et_strategies.py`](../scripts/tester_narratif_et_strategies.py) ; résultats : [`data/narratif_strategies/resultats.csv`](../data/narratif_strategies/resultats.csv).*

## La question

Si l'on prend le « narratif » d'Amirou (son avis sur les devises) et qu'on n'applique ses stratégies que dans son sens, gagne-t-on ?

## Ce qui avait déjà été mesuré

([`MODELE_FONDAMENTAL_ET_MLQ.md`](MODELE_FONDAMENTAL_ET_MLQ.md))
- **Son avis écrit**, tiré de 640 messages et rapports SignalX de 2019 à 2026, annonce le bon sens d'une devise dans **46 à 59 % des cas** selon la devise, et **49 % sur le dollar**.
- **Ses propres trades ne gagnent pas plus quand ils suivent ce qu'il a écrit** : +0,82 R dans le sens, +0,88 R contre.

## Le test

- **Narratif** : pour une paire A/B, son avis écrit sur A moins son avis écrit sur B, sur les 14 jours précédents, connu la veille du signal.
- **Stratégies** : les trades déjà simulés de l'englobante sur un MLQ et de la cassure puis retour sur un MLQ (objectif 2 R), classés en trois groupes : dans le sens du narratif, contre, sans avis.

| Stratégie | Dans le sens du narratif | Contre | Sans avis |
|---|---|---|---|
| Englobante + MLQ, journalier 2020-2026 | **+0,23 R** (200 trades, ±0,08) | 0,00 (218) | +0,05 (458) |
| Englobante + MLQ, horaire 2024-2026 | +0,13 (182, ±0,09) | +0,05 (200) | +0,12 (375) |
| Cassure puis retour sur MLQ, journalier 2019-2026 | +0,08 (313, ±0,08) | +0,03 (288) | −0,12 (696) |
| Cassure puis retour sur MLQ, horaire 2024-2026 | −0,02 (985, ±0,05) | **+0,05** (964) | +0,01 (1 983) |

## Ce qu'il faut retenir

1. **Un seul résultat encourageant** : l'englobante sur un MLQ, en journalier depuis 2020, fait +0,23 R quand elle suit son narratif, contre 0,00 R quand elle va contre. L'écart est d'environ deux erreurs types.
2. **Il ne se confirme pas ailleurs** :
   - en horaire sur 2024-2026, la même stratégie fait aussi bien sans avis (+0,12) que dans le sens du narratif (+0,13) ;
   - pour la cassure puis retour sur MLQ, le narratif aide un peu en journalier et nuit en horaire.
   - Sur quatre essais, un écart de deux erreurs types peut venir du hasard.
3. **Le narratif tel qu'il l'écrit n'améliore pas ses stratégies de façon fiable.** Ce test ne mesure toutefois que ce qu'il publie. Le narratif qu'il garde en tête, ou celui qu'il réserve à SignalX, n'est pas mesurable.
4. Une piste se suit sans changer la règle en démo : noter, pour chaque signal du suivi englobante + MLQ, si le narratif récent d'Amirou va dans son sens, et comparer les deux groupes dans 6 à 12 mois.

## Relancer

```
python scripts/tester_narratif_et_strategies.py
```
