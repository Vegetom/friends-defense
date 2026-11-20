# Doctrines de tentative

Ce lot ajoute une décision de campagne après le premier boss vaincu de la Plaine (vague 5). Référence `356728e`. Le choix est unique par tentative, gratuit, et survit aux changements de terrain, aux rechargements et aux checkpoints. Une nouvelle tentative repart sans doctrine. Les bonus de la vague 3 et des vagues 6 et 9 restent locaux au terrain.

- **Escadron** : les attaques de Tom et Raphaël infligent 22 % de dégâts supplémentaires aux volants lorsque la tour se trouve à 1,25 case ou moins du trajet aérien. Le placement et l'inspecteur signalent l'activation.
- **Embuscade** : l'explosion principale d'Ylvine gagne 0,30 case de rayon si sa cible est un ennemi terrestre ralenti. Le feu et les impacts différés conservent leur rayon habituel.
- **Sans doctrine** : poursuivre avec les bonus de terrain habituels.

Le moteur propose les cartes uniquement après la résolution de la vague et la mort du boss. Une fuite du boss ne suffit pas. Le champ de sauvegarde facultatif `g.doctrine` est copié dans le checkpoint puis transmis au terrain suivant. Les sauvegardes v38 anciennes chargent sans ajout du champ ni attribution rétroactive. L'entrée du Bastion à zéro pouvoir reste bloquée : sa première vague est terrestre et le rayon supplémentaire ne permet pas de franchir le blindage par impact.

## Campagnes simulées

Même moteur, stratégie d'achat, profil et dépense avant/après. Le simulateur prend Escadron avec le plan air et Embuscade avec le plan zone. Les nombres indiquent les vagues terminées.

| Profil | Air | Zone |
| --- | ---: | ---: |
| Zéro | 8 → 8 | 7 → 7 |
| Quelques pouvoirs | 9 → 9 | 19 → 19 |
| Intermédiaire | 31 → 31 | 31 → 31 |
| Maximum | 69 → 70 | 70 → 70 |

Sur le même nouveau code, le profil maximum orienté air reste à 69 vagues avec « Sans doctrine ». Les effets sont isolés dans les tests de combat. Les résultats de campagne concernent les politiques automatiques testées avec une graine fixe, et non la difficulté ressentie par des joueurs.

```sh
git show 356728e:index.html >/tmp/doctrine-before.html
node tools/simulations/run.cjs --compositions air,zone --source /tmp/doctrine-before.html
node tools/simulations/run.cjs --compositions air,zone
node tools/simulations/run.cjs --profiles max --compositions air --doctrine sansDoctrine
```
