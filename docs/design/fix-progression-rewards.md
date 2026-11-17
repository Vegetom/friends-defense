# Contrat de progression — GD-01 / QA-02

## Périmètre et décisions

La correction porte sur le décompte des vagues réellement terminées et sur l'isolation du raccourci de développement. Elle ne change ni les prix, ni les statistiques des héros/ennemis, ni les coefficients de difficulté, ni les revenus en Z, ni les graphismes.

Référence fonctionnelle étudiée : `main` au commit `0e14138bc42eefbfcb7dcef06be3f955d328292d`. Consignes lues dans `AGENTS.md` et `docs/COLLABORATION.md` au commit `e882b2278c9dfc99a06be89ef025743de988d81b`, en attendant leur intégration dans `main` par l'utilisateur. Le présent document est le livrable de conception ; le code et les tests sont confiés au Développeur/QA, et la publication au coordinateur.

Décisions utilisateur appliquées :

1. Une vague lancée mais non terminée n'ajoute aucune vague acquise, aucune étoile liée à cette vague et aucun record.
2. Une défaite n'annule pas les vagues déjà terminées ; les gains légitimes de la tentative sont conservés.
3. Les étoiles déjà acquises, les paliers permanents, les records et l'achèvement existants ne sont pas retirés rétroactivement.
4. Les formules historiques restent inchangées lorsque la tentative comporte au moins une vague terminée.
5. Le parcours de développement, s'il est conservé, utilise un profil séparé et ne crédite pas le profil normal.

## Décompte attendu

Pour un état normal du format 38, `level` est l'indice du terrain de 0 à 6 et `g.wave` le numéro de la dernière vague lancée, de 0 à 10. Les dix vagues de chacun des terrains précédents sont déjà acquises.

```text
vagueNonTerminee = g.active OU (g.ended ET g.life == 0)
vaguesTermineesDuTerrain = max(0, g.wave - (vagueNonTerminee ? 1 : 0))
n = level × 10 + vaguesTermineesDuTerrain
```

Le combat actif est incomplet même si tous ses ennemis ne sont pas encore apparus. En cas de défaite, la dernière vague lancée est incomplète. En préparation après une victoire de vague ou pendant un choix de bonus, `g.wave` est déjà terminé : il ne faut pas le soustraire une deuxième fois. Une reprise de checkpoint ramène à une préparation dont le numéro correspond à la dernière vague terminée ; relancer la suivante ne crée pas de progression supplémentaire.

Cette dérivation utilise les champs déjà présents et n'exige pas un nouveau compteur dans le format 38. Elle ne prétend pas réparer les sauvegardes structurellement invalides ; leur validation générale relève d'une autre correction.

### Matrice sur les sept terrains

Les colonnes regroupent des états qui doivent avoir **exactement le même décompte**, avant attribution éventuelle de fin de tentative.

| Terrain | Préparation initiale V0 / V1 active / défaite V1 | Préparation après V1 / V2 active / défaite V2 | Préparation après V9 / V10 active / défaite V10 | V10 terminée avec des vies restantes |
| --- | --- | --- | --- | --- |
| 1 — La plaine | 0 | 1 | 9 | 10 |
| 2 — La mare | 10 | 11 | 19 | 20 |
| 3 — Les deux forteresses | 20 | 21 | 29 | 30 |
| 4 — Le bastion | 30 | 31 | 39 | 40 |
| 5 — Le Défilé | 40 | 41 | 49 | 50 |
| 6 — L'Archipel | 50 | 51 | 59 | 60 |
| 7 — La Couronne | 60 | 61 | 69 | 70 |

**Attention :** quitter la première vague du terrain 2 ne donne pas zéro pour la tentative : les dix vagues du terrain 1 sont légitimement acquises. L'interdiction concerne le crédit de la vague inachevée, pas la suppression des terrains déjà terminés.

## Étoiles, records et victoire

- Si `n == 0`, le gain est **0**, le nouveau record est **faux** et aucun achèvement de campagne n'est accordé, qu'il s'agisse d'un abandon ou d'une défaite.
- Si `n > 0`, `record = n > bestWaveAvant`, et la récompense de base reste `max(5, 4 + 2 × level + floor(n / 8) + (record ? 2 : 0))`.
- Le record conservé reste `max(bestWaveAvant, n)` ; une ancienne valeur n'est jamais abaissée.
- Le bonus historique de **10 étoiles** et l'achèvement sont réservés à une victoire réelle de campagne : dernier terrain, dixième vague terminée, combat inactif, état terminé et vies strictement positives. Le seul argument `win=true` ne doit pas transformer un état de préparation, de combat actif ou de défaite en victoire.
- Gagner un terrain intermédiaire n'encaisse pas automatiquement des étoiles ; l'attribution demeure à la fin de la tentative, comme dans le jeu de référence.
- Une tentative ne peut encaisser sa récompense qu'une fois. Recliquer, reprendre un écran de récompense sauvegardé ou recharger la page ne doit pas la réattribuer.

### Cas chiffrés d'attribution

Dans chaque cellule `A / B`, `A` suppose un nouveau record légitime et `B` un record existant supérieur ou égal à `n`. Pour `n=0`, le nouveau record reste faux dans tous les cas. Le passage au terrain suivant explique que la formule conserve son facteur `level` : ce paramètre historique n'est pas recalibré par cette correction.

| Terrain | Fin de tentative en préparation initiale / V1 active / défaite V1 | Fin après V1 terminée / V2 active / défaite V2 | Fin après V9 / V10 active / défaite V10 | V10 gagnée, puis fin de tentative sur ce terrain |
| --- | --- | --- | --- | --- |
| 1 | 0 / 0 | 6 / 5 | 7 / 5 | 7 / 5 |
| 2 | 9 / 7 | 9 / 7 | 10 / 8 | 10 / 8 |
| 3 | 12 / 10 | 12 / 10 | 13 / 11 | 13 / 11 |
| 4 | 15 / 13 | 15 / 13 | 16 / 14 | 17 / 15 |
| 5 | 19 / 17 | 19 / 17 | 20 / 18 | 20 / 18 |
| 6 | 22 / 20 | 22 / 20 | 23 / 21 | 23 / 21 |
| 7 | 25 / 23 | 25 / 23 | 26 / 24 | **36 / 34**, victoire de campagne comprise |

Le gain est un montant de fin de tentative, pas un gain versé à chaque entrée de la matrice. Après une vraie V1 terminée en plaine, échouer pendant V2 garde `n=1` et donne 6 étoiles si c'est un nouveau record, sinon 5. En revanche, lancer/abandonner V1 à répétition depuis une tentative neuve reste à zéro ; le précédent farm `6 + 40 × 5` disparaît.

Les valeurs de la matrice ont été calculées indépendamment de l'implémentation cible, avec la formule de référence. Elles servent d'exemples attendus ; elles ne constituent pas à elles seules une validation de navigateur.

## Préservation des sauvegardes et états hérités

- Le profil normal conserve sa clé `friends-defense-save-v38` et sa version `38`.
- Chargement, décompte et sauvegarde ne retirent ni étoiles, ni achats permanents, ni record, ni indicateur d'achèvement déjà acquis. Une récompense déjà versée ne doit pas être recalculée pour soustraire sa différence.
- Un combat ancien sauvegardé au milieu d'une vague reprend avec son état de combat ; au prochain abandon ou échec, son décompte exclut la vague encore inachevée. Le calcul ne repart pas de zéro pour la campagne.
- Un ancien écran de fin avec `runEnded=true` conserve son versement déjà réalisé et son historique ; il ne déclenche pas un deuxième versement au rechargement. Une donnée historique affichée peut garder l'ancien décompte sans que le solde soit réécrit.
- Un ancien record ou un ancien achèvement obtenu par le bouton de développement n'est pas distinguable d'une acquisition légitime dans le format actuel. La correction protège les nouvelles sessions et **ne prétend pas identifier ou retirer ces acquisitions passées**.
- Les scénarios utilisent des profils synthétiques isolés et une copie de données d'exemple ; aucune sauvegarde réelle n'est effacée pour les tester.

Le choix de ne pas introduire de nouveau champ repose sur les transitions normales de la version 38. Un état contradictoire importé manuellement n'est pas une preuve qu'une vague a été terminée ; ne pas étendre cette correction en migration générale sans besoin correspondant.

## Isolation du développement

Le bouton ne doit pas être accessible dans le parcours normal, et son gestionnaire doit vérifier le mode de développement avant de changer l'état. Le masquer sans empêcher l'appel de son gestionnaire ne suffit pas à séparer les parcours prévus.

Si une entrée explicite en mode de développement est conservée :

- Choisir la clé de profil séparée au démarrage de la session ; les lectures et écritures de progression, reprises et récompenses restent dans ce profil.
- Ne pas importer ni effacer automatiquement le profil normal pour créer un profil de développement.
- Les étoiles, records ou achèvements simulés en développement ne doivent pas apparaître après retour au parcours normal.
- Vérifier l'identité du stockage normal avant/après un raccourci de développement, la fin simulée de campagne et un rechargement ; tester séparément les deux modes.
- Une ancienne sauvegarde normale reste lisible et inchangée quand l'utilisateur a simplement visité le mode de développement.

Il s'agit de séparer les fonctionnalités distribuées, pas d'un mécanisme anti-triche contre un utilisateur qui modifie lui-même son code local ou son stockage.

## Critères de sortie et limites

Le Développeur/QA doit couvrir les états de la matrice, les records nouveaux/existants, l'abandon de combat actif, la défaite après une vague acquise, la victoire finale, la reprise de sauvegardes 38 et l'absence de crédits normaux par le raccourci de développement. Le contrôle du diff doit confirmer la conservation des prix, coefficients de combat, revenus en Z et ressources graphiques.

Les défauts de pause/vitesse, de cœur reporté entre terrains et de validation générale des sauvegardes signalés dans l'audit restent distincts. Cette correction ne constitue pas un nouvel équilibrage, un simulateur de campagne, un audit anti-triche ni une déclaration de compatibilité sur tous les appareils.
