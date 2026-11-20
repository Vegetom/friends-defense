# Plans de terrain

La Plaine, la Mare et les Deux Forteresses servent de pilote. Le plan concerne le terrain en cours. Les doctrines restent des choix de tentative et les évolutions de l’atelier suivent le profil.

| Après la vague | Choix |
| --- | --- |
| 3 · Budget | Ravitaillement donne 75 Z maintenant. Contrat donne 55 Z après chacune des vagues 4 et 5 effectivement franchies. |
| 6 · Tactique | Ligne de tir augmente la portée de 0,20 case. Balise aérienne apparaît si des volants sont attendus. Long hiver ou Colère du nain dépendent des héros déployés. Aux Forteresses, Long hiver est proposé lorsque Jordan est présent. Coordination est une option de secours si un boost déjà acquis réduit le choix. |
| 9 · Dernière vague | Assaut augmente les dégâts directs au boss de 20 %. Nettoyage augmente les dégâts directs aux autres ennemis de 15 %. Réparation rend jusqu’à 3 vies et indique le nombre exact rendu. |

Les nouveaux choix apparaissent après la fin effective de la vague. Une sauvegarde qui attendait un choix avant la mise à jour garde les cartes correspondantes. Les anciens boosts acquis conservent leurs effets, y compris Dernier rempart. Le nouveau contrat et les autres plans sont conservés par les checkpoints. L’interface rappelle les plans actifs et leur durée. Les terrains 4 à 7 gardent leurs offres historiques.

## Simulation

Huit paires de campagnes sur le moteur réel avec des achats légaux, la composition air ou zone, la politique équilibrée et la graine 1. Le tableau donne le nombre de vagues terminées.

| Progression | Air, avant → après | Zone, avant → après |
| --- | ---: | ---: |
| Aucun pouvoir | 8 → 8 | 7 → 7 |
| Premiers pouvoirs | 9 → 9 | 19 → 19 |
| Intermédiaire | 31 → 31 | 31 → 31 |
| Maximum | 70 → 70 | 70 → 70 |

Les réglages initiaux à 55 Z immédiatement, 45 Z par versement et 15 % pour Assaut ont fait perdre du terrain aux compositions automatisées air sans pouvoir et zone avec ses premiers pouvoirs. Le réglage retenu restaure leurs résultats sur les scénarios de référence. Les simulations couvrent des politiques d’achat déterministes. Elles ne mesurent pas un taux de victoire ni la compréhension des cartes en jeu humain.

```sh
git show 6b8229e:index.html >/tmp/terrain-plans-reference.html
node tools/simulations/run.cjs --compositions air,zone --source /tmp/terrain-plans-reference.html
node tools/simulations/run.cjs --compositions air,zone
node tools/simulations/prove-bastion.cjs
```
