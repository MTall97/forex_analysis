# La checklist « SETUP A+ » du playbook, testée sur les cours

*14/10/2026 — script : [`scripts/tester_checklist_a_plus.py`](../scripts/tester_checklist_a_plus.py) ; trades : `data/checklist_a_plus/{horaire,journalier}.csv` (entrée, stop, objectif, sortie, R, et critères remplis) ; résultats : `data/checklist_a_plus/resultats.csv`. Source de la checklist : [`analyses/PLAYBOOK_NOTION.md`](PLAYBOOK_NOTION.md).*

## Les règles, fixées avant le test

La checklist du playbook est écrite en notions ICT. Voici comment chaque point a été traduit (achat ; la vente est symétrique). Le jour J, seule l'information disponible à la clôture de J−1 est utilisée.

| Point du playbook | Règle testée |
|---|---|
| 1. Orderflow weekly et daily | la dernière semaine terminée clôture au-dessus de la clôture d'il y a 4 semaines ; la clôture de J−1 est au-dessus de sa moyenne sur 20 jours |
| 2. Premium/discount daily | l'entrée est dans la moitié basse du range des 20 derniers jours |
| 3. Weekly open (PO3) | l'entrée est sous l'ouverture de la semaine |
| 4. Plus haut weekly proche, 200-300 pips au plus | cible = plus haut de la semaine précédente, à 300 pips au plus |
| 5. FVG daily pour l'entrée | FVG journalier formé dans les 20 derniers jours, pas encore comblé, sous le prix ; le prix revient dedans |
| 6. OTE H4 en corrélation avec le FVG | le FVG chevauche la zone de 62-79 % de retracement de la dernière jambe (plus bas des 20 jours → plus haut depuis) |
| 7. Confirmation LTF dans les killzones | une bougie H1 de Londres (07h-10h UTC) ou de New York (12h-15h UTC) clôture haussière au-dessus du FVG après l'avoir touché ; entrée à cette clôture |
| 8. Stop d'au moins 50 pips | sous le FVG et le plus bas du jour, élargi à 50 pips au minimum |
| 9. Objectif weekly, ratio minimum 1:3 | objectif = la cible du point 4 ; ratio d'au moins 3 |

**Conventions** :
- sortie au plus tard après 10 jours de bourse ;
- un seul trade par FVG ;
- stop prioritaire dans une même heure ;
- spread déduit.

**Témoin** : le déclencheur seul (points 5, 7 et 8, cible au-dessus de l'entrée), sans les autres filtres.

**Deux rejeux** :
- **horaire** : Yahoo, 22 paires, 2024-2026, toute la checklist ;
- **journalier** : Dukascopy, 10 paires, 2012-2026, sans le point 7. L'entrée se fait par ordre limite au haut du FVG, et si le jour d'entrée touche le stop, la perte compte.

## Résultats

| Rejeu | Groupe | Trades | Gagnants | R moyen (± erreur type) | Ratio moyen | Trades par an et par paire |
|---|---|---|---|---|---|---|
| Horaire 2024-2026 | **checklist complète** | **8** | **1 (13 %)** | −0,20 (±0,83) | 4,2 | 0,1 |
| | témoin (déclencheur seul) | 1 027 | 48 % | −0,05 (±0,04) | 1,5 | 17 |
| Journalier 2012-2019 | **checklist complète** | 43 | 33 % | +0,31 (±0,32) | 4,1 | 0,5 |
| | témoin | 3 016 | 37 % | −0,08 (±0,03) | 2,2 | 38 |
| Journalier 2020-2026 | **checklist complète** | 29 | 21 % | −0,01 (±0,39) | 4,3 | 0,4 |
| | témoin | 2 463 | 36 % | −0,13 (±0,03) | 2,2 | 36 |
| **Journalier 2012-2026** | **checklist complète** | **72** | **20 (28 %)** | **+0,18 (±0,24)** | 4,2 | 0,5 |

Chaque critère ajouté seul au témoin (détail dans `resultats.csv`) :
- **aucun ne dépasse 51 % de gagnants** ;
- **aucun n'est nettement positif** : de −0,15 à +0,04 R.

## Ce qu'il faut en retenir
- **On est très loin des 90 % de réussite.** Selon le rejeu, la checklist complète gagne de 13 % à 33 % du temps. Avec un ratio de 1:3 au minimum, c'est attendu : pour que le prix aille 3 fois plus loin dans un sens avant d'aller une fois dans l'autre, il ne peut pas gagner 9 fois sur 10.
- **Ce n'est pas non plus une stratégie perdante prouvée.** Sur 2012-2026, elle fait +0,18 R par trade (±0,24) : le résultat est compatible avec zéro comme avec un petit avantage. Il est positif sur 2012-2019, nul sur 2020-2026.
- **Le setup est extrêmement rare** : environ 0,5 trade par an et par paire, soit 5 par an sur 10 paires. Le playbook en annonce au moins 20 par an. Même si son espérance était réellement de +0,18 R, il faudrait des dizaines d'années pour le confirmer.
- **Les filtres éliminent beaucoup de trades, mais pas les mauvais.** Le témoin perd de 0,05 à 0,13 R. La checklist complète fait un peu mieux, mais avec une erreur type 8 à 20 fois plus grande, parce qu'il ne reste presque plus de trades.

## Limites
- Plusieurs points restent subjectifs : ce qu'est « l'orderflow », « une confirmation », la « jambe » de l'OTE. Ce test évalue **une** version en règles, choisie avant de voir les résultats ; Amirou peut appliquer ces critères autrement.
- Le rejeu horaire ne couvre que 2,8 ans. Le rejeu journalier ne peut pas tester la confirmation en H1.
- Les cours sont ceux de Yahoo et de Dukascopy, pas ceux de son courtier.
