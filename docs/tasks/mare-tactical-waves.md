# La Mare — préparation tactique

Premier chantier issu de l’analyse de Game Design, sur la référence `e6960c2`. La Mare introduit les volants dès la vague 2. Les vagues 4 et 8 sont entièrement aériennes. Les vagues 2, 5, 7 et 10 sont mixtes, et la 6e comme la 9e reviennent au sol. Les boss restent aux vagues 5 et 10. Les autres terrains gardent leur calendrier.

Le briefing au-dessus du plateau annonce les volants, blindés, rapides et boss de la vague. Il utilise la même classification que les apparitions. La ligne de vol est mise en évidence lors des vagues concernées. Sur la Mare, toucher une tour déjà utilisée donne accès à un déplacement gratuit entre deux vagues. Le héros, sa forme et sa valeur restent les mêmes. Une case interdite ou un trajet bloqué ne consomme pas le déplacement. Le checkpoint reprend les mêmes règles qu’un achat de préparation : lors d’une seconde chance, les actions de la vague perdue sont annulées.

Une vague de la Mare déjà en cours dans une sauvegarde v38 continue avec son ancien calendrier. Les deux nouveaux champs sont facultatifs. Les sauvegardes historiques ont été validées dans leur état intégral, et le test de la première vague du Bastion à zéro pouvoir permanent reste concluant.

## Simulation

Commandes, avec le moteur du jeu et sans déplacement automatique :

```sh
git show e6960c2:index.html >/tmp/mare-reference.html
node tools/simulations/run.cjs --source /tmp/mare-reference.html --compositions air,zone --out /tmp/mare-before.json
node tools/simulations/run.cjs --compositions air,zone --out /tmp/mare-after.json
```

| Profil | Orienté air, vagues terminées avant → après | Orienté zone, avant → après |
| --- | ---: | ---: |
| Zéro | 8 → 8 | 7 → 7 |
| Quelques pouvoirs | 9 → 9 | 14 → 19 |
| Intermédiaire | 31 → 31 | 31 → 31 |
| Maximum | 69 → 69 | 70 → 70 |

Les deux profils intermédiaires terminent la Mare à 15 vies. Le plan aérien termine le terrain avec 20 Tom, 5 Raphaël et 1 Jordan. Le plan de zone utilise 3 Ylvine, 5 Raphaël, 3 Tom et 1 Jordan. Le profil à quelques pouvoirs orienté zone perd encore au boss de la dernière vague de la Mare. Ces comparaisons mesurent deux politiques automatiques, pas les résultats de joueurs humains.
