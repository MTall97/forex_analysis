# Les trades de septembre d'Amirou Touré (2019 – 2026), vérifiés

> **Source** : canal Telegram « The halal winning team », export HTML du 01/10/2026, converti en [`data/telegram_messages.jsonl`](../data/telegram_messages.jsonl). Les numéros `#12345` sont les identifiants des messages ; les heures sont en UTC.
> **Méthode** : lecture de **tous** les messages de septembre de chaque année (1 583 messages) et des captures d'écran qui accompagnent les trades. Un trade n'est compté comme gagnant ou perdant que si le canal en donne l'issue (texte, capture MT4/MT5 ou graphique).
> **Captures TradingView** : celles de septembre 2026 ont été récupérées avec [`scripts/fetch_tradingview_snapshots.py`](../scripts/fetch_tradingview_snapshots.py) et intégrées. Pour 2021–2025, les liens TradingView (100 en septembre de 2021 à 2025) ne sont pas encore téléchargés : les issues qui n'apparaissent que sur ces liens restent marquées ❔ ou ⚠️, à compléter.

**Légende** : ✅ gain documenté · ❌ perte documentée · ➖ breakeven / clôture neutre · ⏸ ordre non déclenché, annulé ou non pris · ❔ issue non documentée · ⚠️ résultat publié après coup ou invérifiable

## Synthèse

| Septembre | Trades relevés | ✅ Gains | ❌ Pertes | ➖ BE | ⏸ Non déclenchés | ❔/⚠️ | Remarque principale |
|---|---|---|---|---|---|---|---|
| 2019 | 23 | 7 | 9 | 2 | 0 | 5 | Seule année où les signaux sont donnés en direct avec suivi systématique ; plus de pertes que de gains. |
| 2020 | 10 | 1 | 1 (−3 948 $) | 1 | 1 | 6 | Presque tout est publié en « case study », après coup. |
| 2021 | 6 | 2 | 1 | 0 | 1 | 2 | Résultats montrés via TradingView, souvent après coup ; un TP redessiné (EURJPY). |
| 2022 | 6 | 1 | 1 | 0 | 1 | 3 | Mois dominé par la promotion d'OmegaPro. |
| 2023 | 7 | 3 (dont +~2 200 $ flottants) | 0 | 1 | 2 | 1 | Bonne lecture du dollar et du CAD. |
| 2024 | 10 | 2 (dont +6 000 $ USDJPY) | 1–2 | 1 | 4 | 1–2 | Beaucoup de trades « ratés de quelques pips ». |
| 2025 | 9 | 3 (+~1 440 $ flottants) | 0 | 1 | 2 | 3 | Lancement de SignalX : le direct passe dans le groupe payant. |
| 2026 | 24 | 10 | 2 | 2 | 5 | 3 | Annonce de « 10 000 $ minimum » ; ~2 500 $ visibles sur les captures. |

### Ce qu'il faut retenir
1. **Le taux de réussite réel est bien plus bas que ce qu'affirmait l'audit d'Antigravity.** Ce dernier comptait 167 gains pour 41 pertes, sans méthode reproductible. Sur les septembres vérifiés à la main, on compte environ 29 gains, dont beaucoup seulement flottants ou non chiffrés, pour 15 à 16 pertes. Sur tout le canal, le script [`scripts/extract_trade_events.py`](../scripts/extract_trade_events.py) trouve **54 messages « TP touché » contre 72 messages « SL touché »**, soit 43 % de TP parmi les issues annoncées (détail plus bas).
2. **Les pertes sont sous-déclarées.** Exemple : la vente EURGBP du 16/09/2026 (−157,66 $) n'apparaît que dans une capture d'historique. À partir de 2020, les résultats sont souvent publiés après coup, ou réservés au programme payant puis à SignalX.
3. **La lecture macro est souvent juste.** C'est le point fort vérifiable : EURUSD et la BCE (2022), le dollar et le CAD (2023), USDJPY (2024), EURUSD après le NFP (2025), le dollar haussier et toutes les banques centrales de septembre 2026.
4. **Beaucoup de trades ne sont jamais déclenchés.** Le canal les présente comme des preuves de précision (« raté de 3 pips », « TP touché sans être déclenché »). Pour un suiveur, ces trades valent zéro.
5. **Le risque réel affiché ne correspond pas aux règles données en public.** Le canal recommande 0,5 à 2 % de risque par trade, mais on voit 120 lots sur USDCAD avec un stop de 4 pips (2020), 14 lots sur USDJPY (2024), 10,37 lots sur EURGBP (2026), et un compte de 100 $ qui risquait environ 80 % de son solde (2026).

## 2026 (analyse détaillée)

Annonce de départ (31/08) : « Septembre est un mois à minimum 10 000 $ de bénéfice » (#15267), « je suis haussier sur le dollar, EURUSD sera ma tchiza » (#15269).
- **Captures du canal** : dans [`assets/trades/2026-09/`](../assets/trades/2026-09/), nommées `date_heure UTC_numéro de photo`, notées « ph. » dans le tableau.
- **Captures TradingView** : dans [`assets/tradingview/2026-09/`](../assets/tradingview/2026-09/), notées « TV » ; l'heure de création TradingView est imprimée sur chaque image.

| # | Date | Paire | Ordre (entrée / SL / TP) | Annonce | Issue documentée | Verdict | Preuves |
|---|---|---|---|---|---|---|---|
| 1 | 01/09 | EURUSD | Vente limite 1.16110 / 1.16262 / 1.15726 (R ≈ 2,5) | scénario daily TV 00h52 (#15271), #15279 | plus haut 1.16082 : « raté de 3 pips » #15281 | ⏸ Non déclenché | [TV](../assets/tradingview/2026-09/2026-09-01_10h06_msg15271_ZdyH7sGq.png), [ph.3562](../assets/trades/2026-09/2026-09-01_10h14_photo3562.jpg), [ph.3564](../assets/trades/2026-09/2026-09-01_14h51_photo3564.jpg) |
| 2 | 01→02/09 | EURAUD | Vente 1.62502 / 1.62993 / 1.61474 (R ≈ 2) | TV du 01/09 21h40 (#15286) | déclenchée le 02/09 vers 11h, 1.61774 à 13h49 (TV #15292) ; clôture non montrée | ✅ Gain flottant | [TV 01/09](../assets/tradingview/2026-09/2026-09-02_12h29_msg15286_1DGTtL1w.png), [TV 02/09](../assets/tradingview/2026-09/2026-09-02_13h49_msg15292_6UMGn5oC.png), [ph.3567](../assets/trades/2026-09/2026-09-02_12h30_photo3567.jpg) |
| 3 | 03→08/09 | EURNZD | Achat 1.97502 / 1.97098 / 1.98347 (plan TV) ; 1.97508 / 1.97000 / 1.98510 (capture du 08/09) | TV du 03/09 02h05 (#15295) | entrée touchée le 03/09 vers 16h (TV #15304) ; 1.98658 le 08/09, au-dessus des deux TP | ✅ TP | [TV 03/09](../assets/tradingview/2026-09/2026-09-03_02h05_msg15295_21ngeVjC.png), [TV entrée](../assets/tradingview/2026-09/2026-09-03_18h01_msg15304_LyCO82W1.png), [ph.3571](../assets/trades/2026-09/2026-09-08_09h54_photo3571.jpg) |
| 4 | 01/09 | NZDUSD | Scénario baissier (pas de niveaux) | #15276 | aucun suivi | ❔ | [ph.3559](../assets/trades/2026-09/2026-09-01_10h09_photo3559.jpg) |
| 5 | 10→11/09 | EURUSD (BCE) | Compte réel de 100 $ (+20 $ de crédit). Vente limite 0,54 lot @1.16300 / 1.16450 / 1.15670 (TV : 1.16305 / 1.16460 / 1.15669), **soit ≈ 81 $ de risque sur 100 $** ; annulée, puis vente manuelle 0,2 lot @1.16142 | #15319–#15324 (« 95 % de probabilité », « tout risquer ») | +38,80 $ à 1.15946 (#15337) ; TP 1.15843 atteint le 11/09 (« Done ✅ » #15343) | ✅ Gain (montant final non affiché) | [TV](../assets/tradingview/2026-09/2026-09-10_11h24_msg15331_7XJKnJbq.png), [ph.3573](../assets/trades/2026-09/2026-09-10_11h27_photo3573.jpg), [ph.3575](../assets/trades/2026-09/2026-09-10_12h40_photo3575.jpg), [ph.3579](../assets/trades/2026-09/2026-09-11_12h37_photo3579.jpg) |
| 6 | 16/09 (FOMC) | USDJPY | Plan partagé : achat 154.998 / 154.690 / 155.672 + achat limite 154.612 / 154.205 / 155.672 (« 0,5 % de risque sur chaque trade »). Exécuté : achat 2,58 lots @155.056, fermé avant la Fed ; **puis achat 3,8 lots @155.293, SL 155.270, pris pendant la Fed et absent du plan partagé** | #15359–#15362 | historique MT5 : +68,20 $ et +1 433,40 $ | ✅ Gain | [TV 12h07](../assets/tradingview/2026-09/2026-09-16_12h07_msg15359_BpwPaame.png), [TV 13h16](../assets/tradingview/2026-09/2026-09-16_13h16_msg15365_FdtOFBc9.png), [ph.3584](../assets/trades/2026-09/2026-09-16_18h19_photo3584.jpg), [ph.3585](../assets/trades/2026-09/2026-09-16_19h08_photo3585.jpg) |
| 7 | 16/09 | EURGBP | Vente 1,86 lot @0.85678 | **jamais annoncée dans le canal** | −157,66 $ (même historique MT5) | ❌ Perte non déclarée | [ph.3585](../assets/trades/2026-09/2026-09-16_19h08_photo3585.jpg) |
| 8 | 17/09 (BoE) | EURGBP | Projection baissière vers 0.8530 (TV) ; vente 10,37 lots @0.85857, SL remonté à 0.85850 | #15387–#15389 | +1 025,93 $ flottant ; « trade sécurisé » #15393 ; clôture non montrée | ✅ Gain flottant (sécurisé) | [TV](../assets/tradingview/2026-09/2026-09-17_10h54_msg15388_rewastuP.png), [ph.3586](../assets/trades/2026-09/2026-09-17_11h35_photo3586.jpg), [ph.3587](../assets/trades/2026-09/2026-09-17_11h42_photo3587.jpg) |
| 9 | 16→17/09 | EURUSD | Vente limite 1.14999 / 1.15250 / 1.14474 | TV du 16/09 23h28 (#15381) | « venu à 2 pips de notre point d'entrée » #15395 (1,7 pip) | ⏸ Non déclenché | [TV](../assets/tradingview/2026-09/2026-09-16_23h28_msg15381_eiKejJIx.png), [ph.3588](../assets/trades/2026-09/2026-09-17_16h29_photo3588.jpg) |
| 10 | 16→17/09 | NZDUSD | Vente vers 0.57503 (sans SL ni TP visibles ; plan du 16/09 23h30 transmis aux membres SignalX) | #15396–#15397 | touché puis 0.57316 au moment de la capture | ❔ | [TV](../assets/tradingview/2026-09/2026-09-17_16h49_msg15396_XleNC655.png), [ph.3589](../assets/trades/2026-09/2026-09-17_16h50_photo3589.jpg) |
| 11 | 16→18/09 | NZDJPY | Achat 89.372 / 89.123 / 89.869 (plan Wyckoff du 16/09 23h33) | republié le 21/09 : « ce trade on l'a anticipé tellement bien » #15433–#15434 | prix au-dessus de 90 le 18/09, donc TP dépassé ; le passage par l'entrée et la survie du SL ne sont pas démontrés. Le 18/09, Amirou avait renoncé à acheter la paire (#15414) | ⚠️ Présenté après coup comme réussi | [TV plan](../assets/tradingview/2026-09/2026-09-21_19h11_msg15434_6eNKoon4.png), [TV 21/09](../assets/tradingview/2026-09/2026-09-21_19h10_msg15432_j7lpxiiC.png) |
| 12 | 18/09 | GBPAUD | Vente 1.87806 / 1.88017 / 1.87340 (0,5 %) | TV 00h47 (#15399–#15400) | 1.87568 à 03h07, « mettez-vous à BE » #15407, « nous a bien servi » #15418 ; TP non montré | ✅ Gain (non chiffré) | [TV 00h47](../assets/tradingview/2026-09/2026-09-18_00h48_msg15399_lnKhOCpk.png), [TV 02h51](../assets/tradingview/2026-09/2026-09-18_02h51_msg15408_p3b5qzUz.png), [TV 03h07](../assets/tradingview/2026-09/2026-09-18_03h07_msg15417_p17LysDN.png) |
| 13 | 18/09 (BoJ) | NZDJPY | Achat limite 89.248 / 88.985 / 89.993 | #15401–#15404 | le prix a bondi à 89.655 sans revenir à l'entrée (« raté de justesse » #15409) | ⏸ Non déclenché | [TV](../assets/tradingview/2026-09/2026-09-18_02h48_msg15403_EI3jKk9S.png), [TV après](../assets/tradingview/2026-09/2026-09-18_02h56_msg15410_bLaFYjuy.png) |
| 14 | 18/09 (BoJ) | AUDJPY | Achat limite 111.055 / 110.799 / 111.615 | #15405–#15406 | « lui il est parti direct au TP » sans entrée #15412 | ⏸ Non déclenché | [TV](../assets/tradingview/2026-09/2026-09-18_02h57_msg15413_AMtzCSjN.png) |
| 15 | 21→22/09 | EURGBP | Vente 0.85812 / 0.85962 / 0.85509 (« setup à 80 % ») ; exécuté 2,2 lots @0.85813 le 22/09 | TV du 21/09 19h08 (#15430–#15431) | +164,71 $ flottant, puis BE #15443 | ➖ BE | [TV](../assets/tradingview/2026-09/2026-09-21_19h08_msg15430_pUJjmgvc.png), [ph.3594](../assets/trades/2026-09/2026-09-22_12h28_photo3594.jpg), [ph.3595](../assets/trades/2026-09/2026-09-22_14h35_photo3595.jpg) |
| 16 | 21/09 | ? | – | – | « mettez-vous à BE » #15438 alors que l'EURGBP n'était pas encore déclenché : trade concerné non identifié (probablement SignalX) | ➖ BE (non identifié) | [ph.3592](../assets/trades/2026-09/2026-09-21_22h55_photo3592.jpg) |
| 17 | 29/09 (RBA) | AUDUSD | Deux ventes : 0.70140 / 0.70340 / 0.69738 et 0.70008 / 0.70160 / 0.69702 ; exécutées @0.70080 et 0.70003 | #15458–#15459 (veille) | 0.69764 à 15h22 (à 2,6 pips du 1er TP) ; « tout était pourtant là » #15468 ; TP non montré | ✅ Gain flottant | [TV](../assets/tradingview/2026-09/2026-09-29_15h22_msg15466_AuLy2YiP.png), [ph.3602](../assets/trades/2026-09/2026-09-29_04h39_photo3602.jpg), [ph.3606](../assets/trades/2026-09/2026-09-29_14h14_photo3606.jpg) |
| 18 | 29/09 | GBPAUD | Achat 1.88636 / 1.88306 / 1.89298 (0,5 %, SignalX) | #15462 | « TP sur gbpaud ! » #15463 | ✅ TP (R = 2) | [ph.3604](../assets/trades/2026-09/2026-09-29_06h48_photo3604.jpg), [ph.3605](../assets/trades/2026-09/2026-09-29_06h48_photo3605.jpg) |
| 19 | 29→30/09 | USDJPY | Vente 157.506 / 157.869 / 156.459 (0,5 %) | #15481 | « TP sur usdjpy » #15482 | ✅ TP (R ≈ 2,9) | [ph.3609](../assets/trades/2026-09/2026-09-30_04h31_photo3609.jpg), [ph.3610](../assets/trades/2026-09/2026-09-30_04h31_photo3610.jpg) |
| 20 | ~29→30/09 | EURGBP | Vente 0.85855 / 0.86028 / 0.85506 (SignalX) | – | 0.85520 (à 1,4 pip du TP) « comme sur des roulettes » #15484 | ✅ Gain (TP probable, non confirmé) | [ph.3612](../assets/trades/2026-09/2026-09-30_09h52_photo3612.jpg) |
| 21 | 30/09 | GBPJPY | Avis haussier (sans niveaux) | #15483 | 208.12 → 208.72 (#15489), puis 209.33 le 01/10 | ✅ Direction juste | [ph.3611](../assets/trades/2026-09/2026-09-30_07h59_photo3611.jpg), [ph.3613](../assets/trades/2026-09/2026-09-30_11h43_photo3613.jpg), [TV 01/10](../assets/tradingview/2026-10/2026-10-01_00h47_msg15506_4RTzsjXN.png) |
| 22 | 30/09 | AUDUSD | Vente limite 0.69980 / 0.70230 / 0.69480 | #15490–#15491 | « TP touché sans être déclenché » #15493 | ⏸ Non déclenché | [ph.3614](../assets/trades/2026-09/2026-09-30_16h20_photo3614.jpg), [ph.3616](../assets/trades/2026-09/2026-09-30_16h20_photo3616.jpg) |
| 23 | 30/09→01/10 | USDJPY | Achat 157.012 / 156.654 / 157.736 (0,5 %) | #15491 | SL touché le 30/09 vers 12h, puis TP dépassé le 01/10 : « toucher notre SL et partir direct au TP » #15505 | ❌ Perte | [ph.3615](../assets/trades/2026-09/2026-09-30_16h20_photo3615.jpg), [TV 30/09](../assets/tradingview/2026-09/2026-09-30_16h20_msg15492_W0Tqm9yy.png), [TV 01/10](../assets/tradingview/2026-10/2026-10-01_00h38_msg15504_BGrlkMGs.png) |
| 24 | 29/09 | US30 | Avis baissier : « ce mouvement a l'air inévitable », 51 165 → 50 000 | #15473–#15474 | 51 067 le 01/10, en cours | ❔ En cours | [TV](../assets/tradingview/2026-09/2026-09-29_16h13_msg15474_g60N4wkH.png), [ph.3624](../assets/trades/2026-09/2026-10-01_00h54_photo3624.jpg) |

### Bilan de septembre 2026
- **Résultats** : 10 gains (4 TP atteints, 1 gain réalisé sur USDJPY, 5 gains flottants ou non chiffrés) et 1 avis directionnel juste · **2 pertes** (USDJPY du 30/09 et EURGBP du 16/09, cette dernière jamais annoncée) · 2 BE · 5 non déclenchés (dont 3 « ratés de justesse ») · 2 sans issue · 1 trade présenté après coup comme réussi (NZDJPY, #11).
- **Argent visible sur les captures** : +1 319,22 $ net le 16/09 (1 501,60 $ de gains − 157,66 $ de perte − 24,72 $ de commission), +1 025,93 $ flottant le 17/09, +164,71 $ flottant le 22/09, +38,80 $ flottant sur le compte de 100 $. **L'objectif de « 10 000 $ minimum » n'est pas vérifiable** : les autres trades sont exprimés en % de risque sur un capital inconnu.
- **« 1 500 $ en live » (#15374)** : c'est la somme des deux gains USDJPY. Le résultat net de la journée est de 1 319,22 $, après la perte EURGBP et les commissions.
- **Lecture macro : juste.** L'appel « dollar haussier » du 31/08 s'est réalisé (EURUSD ≈ 1.165 → 1.141 au 23/09, soit −240 pips ; capture [3597](../assets/trades/2026-09/2026-09-23_09h26_photo3597.jpg)). C'est cohérent avec la saisonnalité calculée par le projet : septembre est le pire mois d'EURUSD sur 2020–2025 (33 % de mois haussiers, −1,11 % en moyenne). Les décisions de banques centrales anticipées dans le canal sont confirmées par la presse :
  - BCE, 10/09 : +25 pb, taux de dépôt à 2,50 % ([OrbitRemit](https://blog.orbitremit.com/ecb-rate-decision-september-2026/)).
  - Fed, 16/09 : +25 pb à 3,75–4 %, vote 12-0, présidence de Kevin Warsh ([CNBC](https://www.cnbc.com/2026/09/16/fed-rate-decision-september-2026.html)).
  - BoE, 17/09 : statu quo à 3,75 % par 6 voix contre 3, comme annoncé ([SPF](https://www.spf.co.uk/insights/market-insights/bank-of-england-holds-base-rate-in-september-2026/)).
  - BoJ, 18/09 : +25 pb à 1,25 %, et le yen a malgré tout baissé ([Bloomberg](https://www.bloomberg.com/news/articles/2026-09-18/boj-hikes-rates-at-fastest-pace-since-1990-as-inflation-persists)).
  - RBA, 29/09 : +25 pb à 4,60 %, conforme au consensus ([RBA](https://www.rba.gov.au/media-releases/2026/mr-26-27.html)).
- **Ce que montrent les captures TradingView** : les plans publiés ne correspondent pas toujours à ce qui est exécuté. Le 16/09, le gain principal (3,8 lots USDJPY) vient d'une entrée prise pendant la Fed, absente du plan partagé. Le 21/09, un setup NZDJPY abandonné le 18/09 est republié comme « anticipé tellement bien ».
- **Gestion du risque** : les messages publics parlent de 0,5 % de risque par trade, mais les tailles affichées vont de 2 à 14 lots, et le compte de 100 $ du 10/09 risquait environ 80 % de son solde.
- **Biais de présentation** : « précision sniper », « zéro drawdown »… Les trades manqués de 2 ou 3 pips sont présentés comme des preuves de précision, et la perte EURGBP du 16/09 n'apparaît que dans une capture d'historique.

## 2019 – 2025 (registre trade par trade)

### 2019
| Date | Paire | Sens | Annonce (msg) | Issue documentée (msg) | Verdict |
|---|---|---|---|---|---|
| fin août → 03-04/09 | USDCAD | – | #1105 | « fermez avec 55 pips de profit » #1134, #1148 | ✅ Gain (+55 pips, clôture manuelle) |
| 03→05/09 | GBPAUD | Achat | #1139 (achat si bougie verte) | BE #1158, TP #1168, « 246 pips » #1169 | ✅ Gain (+246 pips annoncés) |
| 04/09 | GBPNZD | – | aucune annonce préalable trouvée | « en profit » #1147 | ❔ Non documenté |
| 04/09 | AUDCAD | Vente | #1144 (attendre son accord) | « a presque touché profit » #1149 | ❔ Non documenté |
| 03→05/09 | EURNZD | – | #1142 / #1162 | « a touché profit » #1164 | ✅ Gain |
| 04→05/09 | NZDUSD | Vente | #1159 | « stop loss touché » #1166 | ❌ Perte |
| 04→05/09 | USDCAD | Achat | #1160 | « STOP LOSS TOUCHé » #1165 | ❌ Perte |
| 05/09 | USDCHF | Achat | #1161 | « take profit touché » #1167 | ✅ Gain |
| 06/09 | NZDCAD | Vente | #1175 | aucun suivi | ❔ Non documenté |
| 17→19/09 | AUDUSD | Vente (TP 0.6740) | #1188, #1189 | SL à l'entrée #1203, clôture manuelle #1213 | ➖ Clôture manuelle, résultat non chiffré |
| 17→20/09 | EURAUD | Achat | #1194 | SL en profit 1.62180 #1216, tout fermer #1222 | ✅ Gain verrouillé |
| 18→20/09 | NZDCAD | Vente | #1199 | SL en profit 0.83715 #1215 | ✅ Gain verrouillé |
| 18→19/09 | CADJPY | Vente | #1202 | « a touché notre stop loss » #1204 | ❌ Perte |
| 19→20/09 | GBPJPY | Vente | #1211 | « a touché stop loss » #1214 (commenté #1239) | ❌ Perte |
| 23→24/09 | GBPJPY | Vente | #1246 | « nos 3 trades ont touché stop loss » #1251 | ❌ Perte |
| 23→24/09 | USDJPY | Vente | #1248 | idem #1251 | ❌ Perte |
| 23→24/09 | GBPUSD | Vente | #1249 | idem #1251 | ❌ Perte |
| 24/09 | USDJPY | Vente (SL 107.625, TP 104.285) | #1255–#1258 | aucun suivi explicite | ❔ Non documenté |
| 24→27/09 | GBPJPY | Vente (ré-entrée) | #1260 | SL en profit #1267 | ✅ Gain verrouillé |
| 25/09 | USDCAD | – | #1263 | « en profit, SL à l'entrée » #1264 ; fermé « à cause du non-sens du marché » #1289 | ➖ BE / clôture |
| 25/09 | USDCHF | Vente | #1265 | aucun suivi | ❔ Non documenté |
| 27/09→01/10 | GBPAUD | Achat (SL 1.81340) | #1271–#1273 | « mon stop loss a été touché » #1283 (probable) | ❌ Perte (probable) |
| 30/09→01/10 | USDCHF | Vente | #1281 | « usdchf a touché stop loss » #1285 | ❌ Perte |

Bilan : 7 gains (dont 3 « verrouillés ») · 9 pertes (dont 1 probable) · 2 BE/clôtures · 5 non documentés.

### 2020
Particularité : presque tout est publié **après coup** sous forme de « case study » (pas de signal préalable).
| Date | Paire | Sens | Annonce (msg) | Issue documentée (msg) | Verdict |
|---|---|---|---|---|---|
| 01/09 | US30 | – | « posté hier soir » : **aucun message correspondant dans le canal** | « 1:11 RR » #2625 | ⚠️ Invérifiable |
| 03/09 | USDCAD | Vente 1.30968, SL 4 pips | #2629 (annoncé) | 3 ventes de 50 + 40 + 30 lots, **−3 947,84 $** (capture #2633) | ❌ Perte |
| 04/09 | XAUUSD | Achat | aucune annonce | 5 + 25 lots, +3 878,50 $ flottant (#2644) | ⚠️ Après coup (gain flottant) |
| 16/09 | XAUUSD | Vente zone bleue | #2681 (annoncé le matin) | 1:8 RR, TP 1965.345 atteint (#2686, capture) | ✅ Gain |
| 17/09 | XAUUSD / GBPCHF | Vente | aucune annonce | « premier TP » #2694 ; GBPCHF vente 1.18172 proche TP #2699 | ⚠️ Après coup |
| 21/09 | 3 trades (vidéos) | – | aucune annonce | « 3 trades gagnants aucun SL » #2725 | ⚠️ Après coup |
| 24/09 | NZDCAD | – | #2730 | monté à 1:6 RR mais **fermé à BE** #2733 | ➖ BE |
| 28/09 | AUDUSD | Vente | #2750 | « pas de point d'entrée, non exécuté » #2752 | ⏸ Non déclenché |
| 28/09 | EURUSD, AUDUSD, EURJPY | – | captures « en cours » #2744–#2746 | aucun suivi | ❔ Non documenté |
| 30/09 | CADCHF | – | vidéo « en cours 1:10 » #2756 | aucun suivi | ❔ Non documenté |

Bilan : 1 gain annoncé à l'avance · 1 perte (−3 948 $) · 1 BE · 1 non déclenché · 4 résultats publiés uniquement après coup · reste non documenté.

### 2021
Particularité : les trades sont montrés via des liens TradingView (images non accessibles depuis cet environnement) et presque toujours **après coup**.
| Date | Paire | Sens | Annonce (msg) | Issue documentée (msg) | Verdict |
|---|---|---|---|---|---|
| 01→03/09 | XAUUSD | – | « gold view » #4441 | « setup raté » #4446 ; rejet comme prévu mais non tradé #4450 | ⏸ Non déclenché |
| 25/08→09/09 | EURJPY | Achat 128.797 / SL 128.757 / TP 129.270 (plan du 25/08, SL de 4 pips, R ≈ 12) | lien du 25/08 #4415, re-transféré #4478 | Le 09/09 : « 190 pips avec un SL de 8 pips », « 1:23 RR » #4468–#4476. Mais les captures du 09/09 montrent un plan **redessiné** (entrée 128.778, SL 128.697, TP 130.682 placé sur le plus haut atteint). Le TP d'origine (+47 pips) a bien été dépassé. | ✅ Gain probable d'environ +47 pips selon le plan initial ; ⚠️ les « 190 pips » viennent d'un TP redessiné après coup | [TV 25/08](../assets/tradingview/2021-08/2021-08-25_13h18_msg4415_gTzbQl7k.png), [TV 09/09](../assets/tradingview/2021-09/2021-09-09_13h24_msg4475_o9uPE6Bs.png) |
| 13→15/09 | AUDCAD | Vente 0.92963 / 0.93013 / 0.92692 | aucune annonce (lien publié après) | 0.92698 sur la capture, soit au TP | ⚠️ Après coup (TP atteint d'après la capture) | [TV](../assets/tradingview/2021-09/2021-09-15_14h32_msg4484_E085XGoU.png) |
| 13→15/09 | NZDUSD | Achat 0.70995 / 0.70973 / 0.71456 (SL de 2,2 pips) | aucune annonce | TP atteint le 14/09 d'après la capture ; « 1:20 RR » #4500 | ⚠️ Après coup (TP atteint d'après la capture) | [TV](../assets/tradingview/2021-09/2021-09-15_19h49_msg4498_sSzQMGsU.png) |
| 22→23/09 | AUDUSD | Vente (FOMC + Evergrande) | #4513–#4516 (annoncé avant la Fed) | « floating 1:4RR » #4526 | ✅ Gain flottant (issue finale non donnée) |
| 29→30/09 | XAUUSD | Achat 1724.119 / 1723.156 (stop d'environ 1 $) / 1760.416 | publié après coup #4544 | SL touché le 30/09 vers 06h, puis le prix a atteint le TP : « ça m'a fait sortir quand je dormais » #4545 | ❌ Perte | [TV](../assets/tradingview/2021-09/2021-09-30_18h34_msg4544_Itm2AHOs.png) |

Bilan : 1 trade annoncé à l'avance avec un résultat (AUDUSD, gain flottant) · 1 gain probable (EURJPY, mais revendiqué au-delà de son plan) · 2 gains publiés après coup · **1 perte** (or, SL d'environ 1 $ touché avant la hausse).

### 2022
Contexte : une grande partie du mois est consacrée à la promotion d'**OmegaPro** (#6248, #6296–#6300, #6322–#6325). En juillet 2025, le Département de la Justice américain a inculpé son cofondateur et un promoteur pour une fraude présumée de type Ponzi de plus de 650 M$ ([CoinDesk](https://coindesk.com/policy/2025/07/09/omegapro-founder-and-co-conspirator-charged-by-us-doj-in-650m-ponzi-scheme), [TRM Labs](https://www.trmlabs.com/resources/blog/doj-charges-omegapro-founder-and-promoter-in-650m-global-fraud-scheme)). Plusieurs « trades » du mois sont ceux de membres (messages transférés), pas d'Amirou.
| Date | Paire | Sens | Annonce (msg) | Issue documentée (msg) | Verdict |
|---|---|---|---|---|---|
| 07→08/09 | EURUSD | Vente après la BCE | #6273, #6278 (annoncé la veille et le matin) | BCE à 1,25 % « comme prévu » #6282 (exact : hausse de 75 pb) ; « EURUSD a coulé comme prévu » #6292 | ✅ Direction juste (gain non chiffré) |
| 07/09→ | AUDUSD | Achat | #6265, #6275–#6276 | aucune issue chiffrée ; vidéo « décortiqué » #6339 | ❔ Non documenté |
| 20→21/09 | EURUSD | Vente limite (11 lots) | capture « avant le trade » #6360 | « a refusé de toucher mon point d'entrée » #6358, #6362 | ⏸ Non déclenché |
| 18→21/09 | NZDUSD | – | session du dimanche (non publiée dans le canal) | « 1/7 tp hit » d'un membre #6372 | ⚠️ Résultat d'un membre, pas d'annonce publique |
| 22/09 | EURUSD / EURJPY (jour de l'intervention BoJ) | – | « tout était dans la session du dimanche » (non publiée) | « perfection absolue » #6378–#6385 (vidéos/liens après coup) | ⚠️ Après coup |
| 26→27/09 | AUDJPY | Vente | #6417 | « Audjpy SL touché » #6427 (plan : vente limite 93.623 / 93.824 / 91.553) | ❌ Perte | [TV](../assets/tradingview/2022-09/2022-09-26_18h45_msg6416_KDBL8bP9.png) |

Bilan : 1 analyse annoncée et juste (EURUSD/BCE) · 1 perte (AUDJPY) · 1 non déclenché · le reste après coup ou délégué aux membres.

### 2023
| Date | Paire | Sens | Annonce (msg) | Issue documentée (msg) | Verdict |
|---|---|---|---|---|---|
| 01/09 | GBPCAD | Vente | « vente imminente » #9165 ; « allez à breakeven » #9166 | – | ➖ BE conseillé le jour même |
| 06/09→25/09 | GBPCAD | Vente limite 1.71935, SL 1.72494, TP 1.70573 | #9239 | « regardez comment gbpcad a coulé » #9415 : capture −759 pips depuis le 01/09 | ✅ Direction juste ; exécution de l'ordre limite non démontrée |
| 05→08/09 | USDCAD | Vente 1.36991, SL 1.375, TP 1.3581 | lien #9219 | « raté à cause de quelques pips » #9258, #9260 | ⏸ Non déclenché |
| 12→20/09 | EURNZD | – | « case study », « fondamentalement pas convaincu » #9286 | « réaction au TP avec perfection » #9350 | ⚠️ Pas de position annoncée |
| 15→20/09 | GBPJPY | Achat | #9314–#9315 (« >90 % ») | entrée non atteinte #9321, puis « annulez le setup » #9345 | ⏸ Annulé |
| 20/09 | EURUSD | Vente 5 lots @1.07132 | « trade pris avec le programme avancé » #9357 (annoncé au programme payant) | +1 115 $ flottant (capture #9360) | ✅ Gain flottant (clôture non montrée) |
| 28→29/09 | EURUSD | Vente 4 lots @1.06044 | « scénario pas invalidé » #9444 | +1 112 $ flottant (#9454) ; « plus riche qu'en quittant le Mali » #9432 | ✅ Gain flottant (clôture non montrée) |

Bilan : 3 gains (direction juste sur le CAD via GBPCAD, et 2 ventes EURUSD avec ~2 200 $ de gains flottants) · 1 BE · 2 non déclenchés/annulés · aucune perte affichée ce mois-ci.

### 2024
| Date | Paire | Sens | Annonce (msg) | Issue documentée (msg) | Verdict |
|---|---|---|---|---|---|
| 02→03/09 | NZDJPY, AUDUSD, GBPAUD | – | session payante du lundi (non publiée) | liens publiés après coup #11766–#11776 | ⚠️ Après coup |
| 03→04/09 | USDJPY | Vente 14 lots @145.132 | #11787 (si clôture sous l'ouverture), « 90 % de chance » #11798, « je viens de me positionner » #11803 | 2 200 $ flottant #11808 ; « TP touché, cashout 6 000 $ » #11812 | ✅ Gain annoncé à l'avance (6 000 $ revendiqués ; ≈ 62 pips à 14 lots, cohérent) |
| 05→06/09 | AUDNZD | Vente limite | #11823–#11827 | « pas eu d'entrée, annulez » #11828 (à 7 pips) | ⏸ Non déclenché |
| 10→11/09 | EURNZD | Vente | #11841 | « fermé à BE » #11853 ; ré-entrée vers 1.8000 puis « fermé à BE » #11863 | ➖ BE (×2) |
| 10/09 | AUDNZD | – | « avorté à la dernière minute » #11872 | – | ⏸ Non pris |
| 12/09 | GBP (vers 1.3000) | Vente | #11882–#11885 | « Dommage, SL » #11891 : vente limite 1.30724 / 1.30976 / 1.29960 ; le prix monte à 1.31006, au-dessus du SL | ❌ Perte (confirmée par la capture) | [TV](../assets/tradingview/2024-09/2024-09-12_17h57_msg11890_viA0TIut.png) |
| 17/09 | EURNZD | Vente | #11927 (« moins de risque, j'ai déjà pris un SL ») | – | ❌ (SL antérieur mentionné) / ❔ |
| 17→18/09 | EURNZD | Vente limite 1.79997, SL 1.80194, TP 1.78970 | – | « raté un 1:6 RR à cause de 5 pips… 12 000 $ raté » #11932 (plus haut ≈ 1.7990 sur la capture) | ⏸ Non déclenché |
| 18/09 | GBPAUD | – | #11941 | « le spread a refusé d'exécuter mon trade » #11955 | ⏸ Non exécuté |
| 19→20/09 | GBPAUD | Achat 1.94481, SL 1.93974, TP 1.96095 | entrée décrite après coup #11985 | 1.9552 en profit, « trade le plus facile du monde » #11981 | ✅ Gain flottant (annoncé après l'entrée) |

Bilan : 1 gros gain annoncé à l'avance (USDJPY) · 1–2 pertes · 2 BE · 4 non déclenchés/non exécutés.

### 2025
Contexte : lancement de SignalX, le service de signaux payant (#13881). À partir du 18/09, les trades « en temps réel » sont réservés au groupe payant ; le canal public reçoit surtout les résultats.
| Date | Paire | Sens | Annonce (msg) | Issue documentée (msg) | Verdict |
|---|---|---|---|---|---|
| 05→16/09 | EURUSD | Achat 1.17306 / 1.16575 / 1.19593 (plan du 12/09, swing daily) | après le NFP #13798 ; « le low d'hier sera le low du mois » #13803 ; #13808 ; « je maintiens » #13816 | « EURUSD est arrivé à bon port » #13835, illustré par une capture où le **TP a été déplacé à 1.18722, c'est-à-dire au prix du moment** ; le TP d'origine (1.19593) n'est pas atteint | ✅ Gain flottant (≈ +141 pips) ; ⚠️ TP redessiné | [TV 12/09](../assets/tradingview/2025-09/2025-09-12_10h28_msg13808_eVclllNQ.png), [TV 16/09](../assets/tradingview/2025-09/2025-09-16_23h30_msg13836_WVsX2BUl.png) |
| 17/09 | CADJPY | Vente | « let's goo sur CADJPY » #13843 | « mettez-vous à breakeven » #13856 | ➖ BE |
| 17/09 | GBPCAD | – | #13850–#13851 | « quelques pips seulement et ça aurait été un bon trade » #13855 | ⏸ Non déclenché |
| 16→17/09 | EURAUD | – | #13834, zone d'entrée #13858–#13861 | aucune issue | ❔ Non documenté |
| 18/09 | GBPNZD | – | « probablement le plus intéressant » #13877–#13879 | aucune issue | ❔ Non documenté |
| 22/09 | GBPAUD | Vente | « idée de trade » #13924 (posté le 22 à 01h, republié le 24) | +515,12 $ flottant (#13905, capture à 2.04337) | ✅ Gain flottant |
| 22→23/09 | GBPJPY | Vente | « GJ sera une vente » #13918 | « GBPJPY bouge enfin » (SignalX) #13919 | ❔ Non chiffré |
| 24/09 | AUDUSD | Achat | « le plus beau setup de 2025 », annulé quelques minutes avant l'entrée #13929 | – | ⏸ Annulé |
| 25→29/09 | CADJPY | Vente @107.43 (TP non renseigné) | #13946 (« allée sans retour »), analyses #13943–#13958 | « Trop facile ! » #13959 ; +926,77 $ flottant à 106.958 #13969 | ✅ Gain flottant |

Bilan : 3–4 gains (2 chiffrés, ≈ 1 440 $ flottants) · 1 BE · 2 non déclenchés/annulés · aucune perte affichée · plusieurs setups sans issue.

## Tout le canal (2019 – 2026) : extraction automatique

Le script [`scripts/extract_trade_events.py`](../scripts/extract_trade_events.py) classe chaque message par mots-clés (entrée, TP, SL, BE, raté, profit flottant) et écrit [`data/trade_events.csv`](../data/trade_events.csv). Les résultats transférés depuis des membres sont exclus. Un échantillon relu à la main donne environ 80–85 % de classements corrects. Les comptes ci-dessous sont des ordres de grandeur, pas un registre exact : un même trade peut donner plusieurs messages.

| Année | entree | tp | sl | be | rate | profit_flottant | TP / (TP+SL) |
|---|---|---|---|---|---|---|---|
| 2019 | 68 | 10 | 18 | 19 | 3 | 35 | 36% |
| 2020 | 107 | 12 | 19 | 17 | 19 | 24 | 39% |
| 2021 | 8 | 5 | 5 | 9 | 14 | 30 | 50% |
| 2022 | 3 | 2 | 3 | 2 | 6 | 8 | 40% |
| 2023 | 7 | 2 | 7 | 8 | 6 | 10 | 22% |
| 2024 | 6 | 7 | 11 | 13 | 9 | 19 | 39% |
| 2025 | 3 | 6 | 6 | 20 | 9 | 11 | 50% |
| 2026 | 14 | 10 | 3 | 30 | 4 | 15 | 77% |
| **Total** | **216** | **54** | **72** | **118** | **70** | **152** | **43%** |

**Lecture** : jusqu'en 2020, le canal annonce ses entrées en direct (« sell now at market price ») et ses SL. Ensuite, les entrées passent dans les groupes payants (programme avancé, puis SignalX) et le canal public montre surtout des résultats, ce qui fait mécaniquement monter le ratio affiché (77 % en 2026). Paires où les SL annoncés reviennent le plus : EURAUD, AUDJPY (5 chacune), AUDUSD, GBPJPY, GBPUSD, EURUSD (3). Paire où les TP annoncés reviennent le plus : GBPAUD (5).

## Sources externes utilisées
- BCE, 10/09/2026 : [OrbitRemit](https://blog.orbitremit.com/ecb-rate-decision-september-2026/), [communiqué BCE](https://www.ecb.europa.eu/press/press_conference/monetary-policy-statement/shared/pdf/ecb.ds260910~fbf0ab9b8d.en.pdf)
- Fed, 16/09/2026 : [CNBC](https://www.cnbc.com/2026/09/16/fed-rate-decision-september-2026.html), [Fox Business](https://www.foxbusiness.com/economy/federal-reserve-interest-rate-decision-september-16-2026)
- BoE, 17/09/2026 : [SPF](https://www.spf.co.uk/insights/market-insights/bank-of-england-holds-base-rate-in-september-2026/), [MoneyWeek](https://moneyweek.com/economy/news/live/uk-interest-rates-september-bank-of-england)
- BoJ, 18/09/2026 : [Bloomberg](https://www.bloomberg.com/news/articles/2026-09-18/boj-hikes-rates-at-fastest-pace-since-1990-as-inflation-persists), [Japan Times](https://www.japantimes.co.jp/business/2026/09/18/economy/boj-meeting-september/)
- RBA, 29/09/2026 : [RBA](https://www.rba.gov.au/media-releases/2026/mr-26-27.html), [ABC News](https://www.abc.net.au/news/2026-09-29/asx-markets-business-news-live-updates-tuesday-29-september/107206212)
- OmegaPro : [CoinDesk](https://coindesk.com/policy/2025/07/09/omegapro-founder-and-co-conspirator-charged-by-us-doj-in-650m-ponzi-scheme), [TRM Labs](https://www.trmlabs.com/resources/blog/doj-charges-omegapro-founder-and-promoter-in-650m-global-fraud-scheme)

## Ce qu'apportent les captures TradingView de 2021 à 2025

Les 1 243 captures récupérées (voir [`assets/tradingview/`](../assets/tradingview/)) ont servi à vérifier les septembres 2021 à 2025. Elles confirment la plupart des issues citées dans le canal, et en corrigent trois :

1. **Des objectifs (TP) redessinés après coup pour gonfler les gains.**
   - **EURJPY 2021** : le plan du 25/08 visait +47 pips ; le 09/09, le TP est replacé sur le plus haut atteint (≈ +190 pips), et c'est ce chiffre qui est annoncé.
   - **EURUSD 2025** : TP d'origine à 1.19593 ; le 16/09, il est déplacé au prix du moment (1.18722) pour illustrer « arrivé à bon port ».
   - **GBPCAD 2023** : TP d'origine 1.70026 le 01/09, puis 1.70462 sur la capture du 06/09, au niveau du plus bas atteint ([TV 01/09](../assets/tradingview/2023-09/2023-09-01_12h45_msg9164_nfgyWp8i.png), [TV 06/09](../assets/tradingview/2023-09/2023-09-06_14h14_msg9235_QtjuV30n.png)).
2. **Une perte sur l'or (septembre 2021) que le texte du canal laissait ambiguë.** Le stop était d'environ 1 $ sous l'entrée (1724.119 / 1723.156) : il a été touché avant que le prix ne monte jusqu'au TP.
3. **Des stops très serrés**, qui expliquent les ratios de 1:12 à 1:21 mis en avant : 2,2 pips sur NZDUSD 2021, 4 pips sur EURJPY 2021, 3,4 pips sur AUDUSD 2021. Ce sont des trades où un faible écart d'exécution (spread, glissement) suffit à faire sortir la position.

Les autres niveaux (EURUSD 2022 et 2023, AUDJPY 2022, GBPJPY 2023, EURNZD, GBPUSD et GBPAUD 2024, CADJPY et GBPCAD 2025) correspondent à ce qui est écrit dans le canal.
