# Les Deux Forteresses — défense de passage

Ce lot suit le pilote de la Mare. Référence : `05cff30`. Les vagues 3, 6 et 9 regroupent respectivement 3, 3 et 4 blindés en un convoi précédé et suivi d'un rapide. Le briefing affiche le convoi et son effectif. Le passage entre les deux zones est le point naturel pour ralentir le groupe et concentrer les dégâts. Les vagues 4, 7, 8 et 10 conservent leur composante aérienne. Les vagues de boss, les héros, les coûts et les multiplicateurs de PV sont les mêmes.

La sauvegarde v38 d'une vague déjà commencée conserve les règles qui l'ont lancée. Les nouveaux départs enregistrent leur plan dans le champ facultatif déjà utilisé sur la Mare. Une reprise au milieu d'un convoi ne remplace donc pas les ennemis restants par des volants.

## Simulation et validation

Deux compositions aux mêmes profils, avec le moteur du jeu, les budgets réels et le même planificateur avant/après :

| Profil | Sniper, vagues de campagne achevées | Zone, vagues de campagne achevées |
| --- | ---: | ---: |
| Intermédiaire | 34 → 34 | 31 → 31 |
| Maximum | 70 → 70 | 70 → 70 |

Les deux compositions intermédiaires terminent les Deux Forteresses à 15 vies et arrêtent les trois convois. Le plan sniper termine le terrain avec huit Raphaël, trois Tom et un Jordan. Le plan zone utilise cinq Ylvine, sept Raphaël, trois Tom et un Jordan. Ces résultats vérifient la viabilité des deux plans automatiques testés. Ils ne mesurent pas la difficulté ressentie par des joueurs.

```sh
git show 05cff30:index.html >/tmp/forteresses-reference.html
node tools/simulations/run.cjs --profiles intermediate,max --compositions sniper,zone --source /tmp/forteresses-reference.html --out /tmp/forteresses-before.json
node tools/simulations/run.cjs --profiles intermediate,max --compositions sniper,zone --out /tmp/forteresses-after.json
node tests/fortress.test.cjs
python -B -m unittest discover -s tests -p 'test_fortress_browser.py' -v
```
