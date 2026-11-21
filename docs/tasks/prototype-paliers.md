# Campagne et paliers

Les nouveaux tracés sont actifs pour chaque nouveau terrain de la campagne en ligne. Le jeu lit la sauvegarde habituelle. Un terrain déjà enregistré poursuit son tracé historique jusqu’à sa prochaine transition ou au lancement d’une nouvelle tentative. Les paliers précédemment atteints sont retrouvés à partir des records et de la campagne en cours.

Le menu d’essai reste disponible avec `?prototype=1`. Sa campagne et ses sept essais utilisent des sauvegardes distinctes. Pour un essai local, lancer `python -m http.server 8000 --bind 127.0.0.1`, puis ouvrir <http://127.0.0.1:8000/>.

## Sept terrains

| Terrain | Décision de placement |
| --- | --- |
| La Plaine | La clairière laisse assez d’espace pour créer un détour et resserrer la défense. |
| La Mare | L’îlot couvre le couloir aérien. Des tours de rive peuvent rallonger le chemin terrestre de 16 à 18 cases. |
| Les Deux Forteresses | Un pont relie deux cours. On peut concentrer ses tirs au pont ou garder une seconde ligne dans la cour arrière. |
| Le Bastion | Un zigzag de 22 cases, avec des terrasses à l’entrée, au coude et près de la sortie. |
| Le Défilé | Un anneau autour du massif central. Bloquer le passage nord envoie les ennemis au sud. |
| L’Archipel | Deux entrées au sol et une jonction avec une sortie commune. Les ennemis terrestres utilisent les deux branches et les boss arrivent par l’entrée haute. |
| La Couronne | Une diagonale brisée délimite trois poches de construction. Le placement détermine à quel moment attaquer le boss et son escorte. |

## Paliers

Terminer le terrain 3 débloque le départ au Bastion. Terminer le terrain 6 débloque la finale à la Couronne. L’atelier propose les départs acquis et le bilan privilégie le plus avancé. Chaque départ crée une nouvelle tentative au budget de la carte, avec les évolutions du profil et zéro cœur. Les bonus et la doctrine de la tentative précédente repartent à zéro. Les vagues sautées ne donnent ni étoiles ni nouveau record. Les cœurs permettent toujours de reprendre depuis la préparation de la dernière vague.

## Résultats des simulations

Huit comparaisons de campagnes entre les deux versions du prototype, avec quatre profils, les compositions air et zone, la politique équilibrée et une graine fixe. Les nombres de vagues terminées sont identiques dans toutes les paires.

| Profil | Air | Zone |
| --- | ---: | ---: |
| Sans évolution | 8 | 7 |
| Premières évolutions | 9 | 17 |
| Intermédiaire | 31 | 31 |
| Maximum | 70 | 70 |

Dans huit essais supplémentaires au départ de l’Archipel ou de la Couronne, les deux compositions au maximum terminent la campagne. Les profils intermédiaires testés perdent dès la première vague de ces deux départs directs. Le verrou du Bastion à zéro évolution tient. Une comparaison antérieure à la première version du prototype a aussi montré un recul de deux vagues à la Mare pour une composition zone avec peu d’évolutions. Ces résultats dépendent de la politique de placement automatisée.

```sh
node tools/simulations/run.cjs --ref b59246b --prototype --compositions air,zone
node tools/simulations/run.cjs --prototype --compositions air,zone
node tools/simulations/run.cjs --prototype --profiles intermediate,max --compositions air,zone --start-terrain 6
node tools/simulations/run.cjs --prototype --profiles intermediate,max --compositions air,zone --start-terrain 7
node tools/simulations/prove-bastion.cjs --prototype
```
