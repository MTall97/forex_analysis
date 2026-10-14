# La « fourchette » : trader seulement quand COT, banques centrales et tendance sont d'accord

*Rédigé le 14/10/2026, à la demande de l'utilisateur. Script : [`scripts/tester_fourchette.py`](../scripts/tester_fourchette.py) ; résultats : [`data/fourchette/`](../data/fourchette/).*

## L'idée

Au morpion, on gagne en créant une « fourchette » : deux menaces à la fois, l'adversaire ne peut en bloquer qu'une. L'équivalent au Forex serait de ne trader une paire que quand **plusieurs raisons indépendantes** vont dans le même sens :
- les positions des spéculateurs (COT) ;
- la politique des banques centrales (taux) ;
- la tendance des cours.

## Méthode

- **28 paires** formées par les 8 grandes devises (USD, EUR, GBP, JPY, AUD, NZD, CAD, CHF), **chaque semaine de 2007 à 2026** : décision le vendredi, jour de publication du COT, position tenue jusqu'au vendredi suivant.
- **Raisons testées**, seules puis combinées par trois (une « fourchette » = les trois d'accord) :

| Raison | Règle |
|---|---|
| COT suivi | suivre les fonds à effet de levier quand l'écart de leurs positions entre les deux devises (z-score sur 3 ans) est d'au moins 1 |
| COT accélération | suivre la variation de leurs positions sur 4 semaines |
| COT contrarien | aller contre eux quand l'écart est extrême (z-score ≥ 2) |
| Divergence de taux | le différentiel de taux directeurs a monté (ou baissé) sur 13 semaines |
| Portage | différentiel de taux d'au moins 0,5 point |
| Tendance | sens de la paire sur 4 semaines (variante : 13 semaines) |

- **Rendement** : variation de change + intérêts encaissés ou payés, moins 0,03 % par ouverture, fermeture ou retournement.
- **Significativité** : les 28 paires se recoupent (EURUSD et GBPUSD bougent ensemble), donc elle est mesurée sur le rendement hebdomadaire du portefeuille, pas trade par trade.
- **Validation** : trois sous-périodes (2007-2014, 2015-2019, 2020-2026) ; tous les seuils ont été fixés avant de voir les résultats.

## Résultats (2007-2026)

| Règle | Positions-semaines | Gagnantes | Rendement annuel | Sharpe | t |
|---|---|---|---|---|---|
| Portage seul | 20 905 | 52,5 % | **+1,1 %** | 0,18 | 0,8 |
| Portage + tendance 13 semaines | 10 492 | 51,9 % | +0,5 % | 0,08 | 0,3 |
| COT suivi seul | 13 237 | 49,0 % | −1,0 % | −0,15 | −0,7 |
| COT contrarien seul | 4 748 | 50,8 % | −1,0 % | −0,12 | −0,5 |
| Divergence de taux seule | 13 326 | 49,6 % | −1,5 % | −0,20 | −0,9 |
| Tendance 4 semaines seule | 28 793 | 49,2 % | −1,0 % | −0,19 | −0,9 |
| COT accélération seule | 28 810 | 48,8 % | −1,9 % | −0,46 | −2,1 |
| **Fourchette : COT suivi + portage + tendance 13 s** | 3 015 | 50,1 % | −1,9 % | −0,24 | −1,1 |
| **Fourchette : COT suivi + portage + tendance 4 s** | 2 351 | 49,6 % | −2,4 % | −0,31 | −1,4 |
| **Fourchette : COT suivi + divergence + tendance 4 s** | 2 233 | 46,8 % | −2,7 % | −0,29 | −1,3 |
| Fourchette : COT accélération + portage + tendance 4 s | 5 923 | 50,8 % | −1,0 % | −0,15 | −0,7 |
| Fourchette : COT contrarien + divergence + tendance 4 s | 201 | 49,8 % | −0,8 % | −0,25 | −1,1 |

Par sous-période, aucune fourchette n'est positive de façon stable : la meilleure (COT suivi + portage + tendance 13 semaines) fait +0,9 % par an en 2007-2014, −9,0 % en 2015-2019 et +0,1 % en 2020-2026.

## Ce qu'il faut retenir

1. **Empiler les raisons ne crée pas d'avantage** : toutes les fourchettes font moins bien que leurs raisons prises seules, et sont légèrement négatives.
   - Ces raisons ne sont pas vraiment indépendantes : le COT suit la tendance (les spéculateurs achètent ce qui monte) et la tendance suit les taux. Trois signaux d'accord, c'est souvent le même signal compté trois fois, et cela arrive en fin de mouvement.
2. **Seul le portage (acheter la devise qui rapporte le plus d'intérêts) reste positif**, de façon modeste et non significative (+1,1 % par an), comme dans [`AUTRES_ALGORITHMES.md`](AUTRES_ALGORITHMES.md).
3. **Suivre ou contrer les spéculateurs au COT ne donne rien** en hebdomadaire, quelle que soit la version.
4. **La leçon du morpion tient quand même, mais à l'envers** : contre un adversaire qui joue bien (le marché), on ne trouve pas de fourchette gagnante en combinant des informations publiques que tout le monde voit. Le résultat normal est le nul, et le spread le transforme en légère perte.
5. **Limites** :
   - le sentiment des particuliers (Myfxbook) n'a pas d'historique disponible et n'a pas pu être testé ;
   - le COT utilisé est celui des fonds à effet de levier (rapport TFF), pas celui des « non-commerciaux » du rapport historique ;
   - test hebdomadaire : il ne dit rien des entrées intrajournalières.

## Relancer

```
python scripts/tester_fourchette.py
```
