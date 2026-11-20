# Prototype des paliers et des terrains

Ouvrir `index.html?prototype=1` depuis un serveur local pour essayer la campagne. Le menu de départ propose aussi **Essai · Mare** et **Essai · Bastion**. Ces essais commencent au terrain choisi avec quelques évolutions permanentes déjà équipées. La campagne pilote, les deux essais et le mode développeur utilisent chacun leur propre sauvegarde. L’URL standard conserve les cartes et sauvegardes actuelles.

```sh
python -m http.server 8000 --bind 127.0.0.1
```

Ouvrir ensuite <http://127.0.0.1:8000/index.html?prototype=1>.

## Terrains

| Terrain | Partie à observer |
| --- | --- |
| La Mare | Sur la grille 11 × 8, l’îlot central peut recevoir une tour qui vise le couloir des volants. Les tours de rive peuvent dévier le chemin de 16 à 18 cases. Le fond de l’eau ferme le passage terrestre. |
| Le Bastion | Les terrasses bordent un zigzag de 22 cases. Le chemin est réservé aux ennemis. Les positions près de l’entrée, du coude et de la sortie permettent de concentrer les tirs à des moments différents. |

Le prototype reprend les sprites, les vagues, les coûts, les boosts et les valeurs de combat existants. Il garde le verrou du Bastion sans évolution permanente. Les cinq autres terrains suivent leurs règles actuelles.

## Palier du Bastion

Dans la campagne pilote, vaincre le boss final et terminer le terrain 3 déverrouille le départ au Bastion. Après une fin de tentative, l’atelier propose les deux départs. Au Bastion, le joueur commence à la vague 1 avec 215 Z, ses évolutions permanentes et zéro cœur. Les bonus et la doctrine d’une tentative précédente repartent à zéro. Un départ avancé ne crédite aucune vague sautée, même si la tentative est abandonnée pendant la première vague. La sauvegarde conserve le départ choisi et les cœurs gardent leur logique de reprise par vague.

Le départ de la finale après le terrain 6 reste à prototyper.

## Premiers résultats

Les comparaisons utilisent le moteur réel, un départ au terrain étudié, les compositions air et zone, la politique d’achat équilibrée et la graine 1. Il s’agit de douze paires de simulations, avec trois profils par terrain.

- À la Mare, la composition air avec les premiers pouvoirs termine huit vagues dans les deux versions. La composition zone passe de neuf à sept vagues terminées. Les profils intermédiaire et maximum franchissent les dix vagues avec les deux compositions.
- Au Bastion, les deux compositions avec les premiers pouvoirs perdent en vague 1 sur les deux tracés. Les deux compositions intermédiaires terminent la vague 1 et les deux profils maximum franchissent les dix vagues sur les deux tracés. Au profil maximum, le premier achat air se déplace de la grille compacte à la terrasse centrale. Le profil maximum orienté zone privilégie une terrasse près de l’entrée.
- Les résultats montrent des placements différents. La viabilité de la zone à faible progression sur la Mare et le confort du départ intermédiaire au Bastion restent à vérifier en jouant.

```sh
git show eeabe13:index.html >/tmp/paliers-reference.html
node tools/simulations/run.cjs --source /tmp/paliers-reference.html --profiles few,intermediate,max --compositions air,zone --start-terrain 2
node tools/simulations/run.cjs --prototype --profiles few,intermediate,max --compositions air,zone --start-terrain 2
node tools/simulations/run.cjs --source /tmp/paliers-reference.html --profiles few,intermediate,max --compositions air,zone --start-terrain 4
node tools/simulations/run.cjs --prototype --profiles few,intermediate,max --compositions air,zone --start-terrain 4
node tools/simulations/prove-bastion.cjs --prototype
```
