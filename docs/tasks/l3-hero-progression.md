# L3 — pouvoirs permanents, bonus et atelier

L’utilisateur a validé la proposition de Game Design avant l’implémentation. Référence L2 : `4de2eb0`. Périmètre : pouvoirs N1 à N3 des cinq héros, bonus de terrain et lecture des pouvoirs dans l’atelier. Intégration unique sur la branche `feat/l3-hero-progression`.

- `d857fe9` : interception de Tom, railgun anti-bouclier et marquage orbital, interaction du feu avec la régénération et météores orientés, contrôle de Jordan, pénétration et Rage mise en réserve de POY. Les frappes d’une nouvelle Apocalypse résolvent leurs trois cercles au même instant et n’infligent qu’un impact par ennemi. Les frappes historiques en attente suivent leur règle d’origine.
- `6653288` : Balise aérienne, Brèche et Long hiver. La quatrième carte dépend du terrain, du choix et de l’indice de tentative. La rotation est sauvegardée. Les anciennes sauvegardes qui n’ont pas d’indice dans l’état du terrain utilisent la rotation zéro pour ce terrain. Les neuf bonus existants restent disponibles aux mêmes vagues.
- `96d9d71` : prochain pouvoir et rôle visibles, détail des trois paliers à la demande, avec état, prix et synergie. Les prix de 5, 12 et 24 étoiles, les barèmes de puissance de L2 et les ressources graphiques existantes sont conservés.

## Résultats

Campagnes avec le moteur réel, achats, revenus, fuites et reprises réels. Les niveaux permanents sont préchargés pour comparer les profils. Même politique d’achat, mêmes compositions et même pas de 1/30 s que la référence L2. Dans l’ordre mixte / air / sniper / zone :

| Profil | L2 | L3, bonus classiques |
| --- | --- | --- |
| Zéro | 7 / 8 / 7 / 7 | 7 / 8 / 7 / 7 |
| Quelques | 9 / 9 / 19 / 14 | 9 / 9 / 19 / 14 |
| Intermédiaire | 32 / 31 / 34 / 31 | 32 / 31 / 34 / 31 |
| Maximum | 70 / 70 / 70 / 70 | 70 / 69 / 70 / 70 |

Avec la rotation 1 et la préférence systématique pour les nouvelles cartes, le profil maximum termine 59 vagues en mixte et 70 en zone. Avec la rotation 2, la composition aérienne termine les 70 vagues en sélectionnant les nouvelles cartes. Voir les [résultats détaillés](../simulations/l3-results.json). Une politique d’achat automatique fournit des points de comparaison, avec des résultats qui dépendent de la composition et des bonus choisis.

```sh
node tools/simulations/run.cjs --ref d857fe9 --compositions mixed
node tools/simulations/run.cjs --ref 6653288 --profiles few,intermediate,max --compositions mixed,zone --perks rotating --variation 1
node tools/simulations/run.cjs --compositions mixed,air,sniper,zone
node tools/simulations/run.cjs --profiles max --compositions mixed,air,sniper,zone --perks rotating --variation 2
node tools/simulations/prove-bastion.cjs
```

## Validation

- 55 cas Node et 30 tests Chromium, dont aperçu des trois paliers et achat v38 en 854 × 393, offre stable après rechargement en 320 × 568 et sauvegarde dans le checkpoint du nouveau bonus.
- Les résultats du validateur restent identiques sur 1 252 états historiques v38. Les champs nouveaux sont facultatifs. Les clés de stockage, les étoiles, les paliers acquis et la séparation du profil développeur sont conservés.
- L’énumération des armées abordables à zéro pouvoir donne toujours zéro dégât à l’ouverture du Bastion. Les 52 images intégrées et 15 SVG sont identiques à L2.
- Validation mobile en Chromium émulé. Safari et appareil physique non testés. Le rendu en paysage conserve les limites traitées par L5.
