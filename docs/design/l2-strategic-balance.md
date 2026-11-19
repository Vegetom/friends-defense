# L2 — équilibrage de la campagne

Sur les quatre stratégies de référence, les profils au maximum passent de 49–68 vagues terminées à 70. Les profils sans évolution atteignent toujours 7–8 vagues et gagnent 6 étoiles au premier essai. Les premières vagues de la Plaine conservent leur courbe de PV. Aux vagues 6 à 10, le multiplicateur passe de 1,20–1,50 à 1,12–1,28. Le boss final du premier terrain perd aussi son facteur supplémentaire de 1,10.

| Profil (Tom, Raphaël, Ylvine, Jordan, POY) | Avant, mixte / air / sniper / zone | Après, même ordre |
| --- | --- | --- |
| Aucun (0,0,0,0,0) | 7 / 8 / 7 / 7 | 7 / 8 / 7 / 7 |
| Quelques achats (1,1,0,0,0), 10 ★ | 9 / 9 / 19 / 9 | 9 / 9 / 19 / 14 |
| Intermédiaire (2,2,1,1,1), 49 ★ | 32 / 19 / 33 / 31 | 32 / 31 / 34 / 31 |
| Maximum (3,3,3,3,3), 205 ★ | 58 / 68 / 59 / 49 | 70 / 70 / 70 / 70 |

Les rapports de PV entre terrains diminuent, par exemple de 9,5 à 8,6 au Bastion et de 19 à 15 à la Couronne. Les coefficients de revenu en Z passent de 1,12 à 1,20 et de 1,28 à 1,52 sur ces deux terrains. Avec la stratégie mixte au maximum, les dix vagues du Bastion versent 3 020 Z contre 2 737 Z avant. Les facteurs supplémentaires de PV des boss baissent aux terrains 4 à 7. Le boss final continue d'imposer une défaite s'il franchit la sortie. Les coûts des tours, les pouvoirs permanents et le barème des étoiles restent ceux de V3.8. Les quatre victoires normales rapportent chacune 36 étoiles et n'utilisent aucun cœur de reprise.

La pression combine les trajets aériens, les tanks résistants, les mutants qui se régénèrent, les boucliers rechargeables, l'accélération à faibles PV et les boss. Les volants ignorent le labyrinthe et la portée des tours vaut 68 % contre eux. La stratégie orientée air passe de 68 à 70 au profil maximum, notamment au-delà de la vague aérienne 9 de la Couronne. Les équipes de fin de campagne diffèrent réellement. La stratégie air compte 13 Tom, la stratégie sniper 16 Raphaël, la stratégie zone 9 Ylvine et la stratégie mixte emploie les cinq héros dont POY. Elles utilisent toutes plusieurs rôles.

Au Bastion, le blindage retire 90 dégâts par impact avant bouclier et armure proportionnelle. Le marquage le réduit de 60 %, le gel de 20 % et le feu continu le traverse. Avec 215 Z et zéro évolution, le test énumère 32 armées non vides abordables. Le plus gros impact brut est de 85. Avec Jordan, son coût limite les combinaisons abordables et aucun impact n'atteint le seuil même en accordant un gel favorable. Sans feu permanent, aucune élimination ni revenu de combat n'est possible. Les 18 ennemis finissent par atteindre la base qui possède 15 vies. Le résultat vaut pour une entrée normale sur le terrain et ses reprises. Les ennemis déjà apparus dans une sauvegarde historique conservent leurs caractéristiques.

## Reproduction

Les simulations exécutent le noyau du jeu, avec budgets, placements, achats, primes, bonus, reprises et transitions réels. Les paliers permanents sont préchargés pour comparer les profils. La stratégie de placement est heuristique, et la graine départage certains choix. Chaque tentative se poursuit jusqu'à une défaite définitive ou une victoire.

```sh
node tools/simulations/run.cjs --ref 34dc9a8 --compositions mixed,air,sniper,zone --out /tmp/l2-before.json
node tools/simulations/run.cjs --compositions mixed,air,sniper,zone --out /tmp/l2-after.json
node tools/simulations/run.cjs --profiles max --compositions mixed,air,sniper,zone --dt 0.016666666666666666 --out /tmp/l2-step-sensitivity.json
node tools/simulations/run.cjs --profiles max --compositions mixed,sniper --hardcore --out /tmp/l2-hardcore.json
node tools/simulations/run.cjs --profiles max --compositions tom-only,sniper-only,zone-only --out /tmp/l2-single-hero.json
node tools/simulations/prove-bastion.cjs
```

Les traces dans [docs/simulations](../simulations/) contiennent la révision ou l'empreinte de la source, les achats, les revenus entre début et fin de vague, les fuites, les vies et les bonus. Le pas principal est de 1/30 s. À 1/60 s, les quatre stratégies maximales terminent également les 70 vagues. Les deux essais Hardcore s'arrêtent à 38 et 39 vagues terminées. Les résultats mesurent les politiques testées. Une partie humaine, une autre stratégie d'achat ou une cadence différente peuvent donner un autre résultat. Les essais au profil zéro ne valident pas la fin de la Plaine sans évolution.

Les trois essais mono-héros au profil maximum s’arrêtent à 9 vagues pour Tom, 14 pour Raphaël et 1 pour Ylvine, indisponible au départ de la Plaine. Ces essais bornés ne constituent pas une recherche exhaustive d’une stratégie dominante.
