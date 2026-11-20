# Récompenses de progression et bilan de vague

Référence `9c28d06`. Le barème de base, le bonus de record et le bonus de victoire sont conservés. Les primes suivantes donnent une raison de poursuivre après les premières vagues :

- +1 étoile à chacune des vagues 3, 6 et 9 de la Plaine réellement terminées.
- +2 étoiles si le premier boss est vaincu et sa vague terminée. L'offre de doctrine ouverte ou le choix enregistré prouve ce résultat.
- +1 étoile par terrain complet nouvellement franchi dans le record du profil, avec un maximum de 7 sur une tentative.

Une vague non terminée reste exclue du compteur et ne donne aucune prime. Tester une première vague terminée sans nouveau record donne toujours 5 étoiles. Aucun reçu v38 déjà payé n'est recalculé. Les champs de détail du reçu sont facultatifs.

Les reçus historiques peuvent contenir les fuites de la dernière vague. Le bilan de terrain affiche désormais les PV retirés par type de tour et la part du total. Il s’affiche à la victoire, à la défaite et avant une reprise par cœur. Les cinq cartes reprennent les sprites de combat et la forme la plus élevée déployée par héros. Jordan affiche le nombre d’ennemis distincts ralentis.

Le cumul de terrain est sauvegardé dans un champ v38 facultatif. Une reprise restaure le cumul du checkpoint et le terrain suivant commence à zéro. Les sauvegardes antérieures comptent les dégâts observés à partir de la reprise du jeu et le bilan signale le caractère partiel lorsque des vagues ont précédé le suivi.

## Simulation

Seize campagnes comparables, avec le moteur du jeu, la même graine et les mêmes choix automatiques. Les vagues atteintes sont identiques. Avec les profils de test partant d'un record à zéro :

| Profil | Plan air, étoiles | Plan zone, étoiles |
| --- | ---: | ---: |
| Zéro | 7 → 9 | 6 → 8 |
| Quelques pouvoirs | 7 → 12 | 10 → 16 |
| Intermédiaire | 15 → 23 | 15 → 23 |
| Maximum | 36 → 48 | 36 → 48 |

Les deux gains de 48 correspondent à une campagne gagnée pour la première fois, premier boss vaincu compris. Les simulations ne mesurent pas le temps d'apprentissage réel. Le test du Bastion à zéro pouvoir reste valide.

```sh
git show 9c28d06:index.html >/tmp/rewards-reference.html
node tools/simulations/run.cjs --compositions air,zone --source /tmp/rewards-reference.html
node tools/simulations/run.cjs --compositions air,zone
```
