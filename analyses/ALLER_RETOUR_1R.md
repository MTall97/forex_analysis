# « +1 R en 3 à 9 heures, retour à l'entrée, puis stop » : un schéma réel ?

*Rédigé le 06/10/2026, à partir d'une observation de l'utilisateur sur ses propres trades. Script : [`scripts/tester_aller_retour_1r.py`](../scripts/tester_aller_retour_1r.py) ; données : [`data/aller_retour_1r/chemins.csv`](../data/aller_retour_1r/chemins.csv).*

## Méthode

- **Trades** : les trades d'Amirou publiés avant l'entrée, rejoués en cours horaires (décembre 2023 - octobre 2026), avec entrée, stop et objectif au-delà de +1 R : **137 trades**. Le trade démarre à la première bougie horaire qui touche l'entrée.
- **Témoin** : pour chaque trade, 20 entrées au hasard sur la même paire, même sens, même stop et même objectif (2 740 trades).
- **Chemin heure par heure** : +1 R atteint avant le stop ? en combien d'heures ? retour à l'entrée ensuite ? puis stop, ou de nouveau +1 R ? Si une bougie touche deux niveaux, le pire est compté d'abord.

## Résultats

| | Trades d'Amirou | Témoin (hasard) |
|---|---|---|
| +1 R atteint avant le stop | **58 %** | 50 % |
| Délai médian pour atteindre +1 R | **6 h** | 11 h |
| +1 R atteint entre 3 et 9 h (parmi ceux qui l'atteignent) | 38 % | 27 % |
| Après +1 R, retour au prix d'entrée | 51 % | 55 % |
| Après ce retour : stop | 46 % | 48 % |
| Après ce retour : de nouveau +1 R | 54 % | 49 % |
| **Schéma complet (+1 R, retour à l'entrée, stop)** | **14 %** des trades | 13 % |
| dont +1 R atteint en 3 à 9 h | 4 % | 4 % |
| Trades finis au stop qui étaient d'abord passés par +1 R | 25 % | 21 % |

- **La première partie de l'observation est juste** : les trades d'Amirou atteignent +1 R plus souvent et plus vite qu'au hasard (6 h en médiane contre 11 h).
- **La suite, non** : une fois à +1 R, le prix revient à l'entrée une fois sur deux, et, de là, finit au stop une fois sur deux. C'est exactement ce que donne le hasard. Le schéma complet touche 14 % des trades, comme le témoin (13 %).
- **Les trois quarts des trades perdants n'ont jamais vu +1 R.**
- Le schéma marque la mémoire parce qu'il est frustrant (un gain visible devient une perte), pas parce qu'il est fréquent.

## Et pour la gestion ?

- Comparer « sortir à +1 R », « point mort à +1 R » et « tenir jusqu'à l'objectif » donne des écarts qui changent de signe selon la façon de compter les trades non terminés en 10 jours (17 % des trades), et le témoin, censé être nul, ne l'est pas. **Aucune règle de sortie n'est démontrée** sur 137 trades.
- Ce qui est sûr : après +1 R, le retour à l'entrée est un pile ou face. Passer au point mort **à +1 R** (et pas avant) protège sans couper plus de gagnants que le hasard ne le veut.
