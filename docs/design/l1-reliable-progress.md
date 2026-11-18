# L1 — contrat de reprise et de continuité de la progression

## Périmètre

Référence de travail : `main` au commit `14361f3301c4ceaa6f4d5d12e689da15b16936c5`. Les consignes `AGENTS.md`, `docs/COLLABORATION.md` et la feuille de route de mission 01 ont été lues. Cette note précise le contrat Game Designer pour les cœurs, les checkpoints et la reprise pause/vitesse ; les validations techniques des sauvegardes et les autres parcours de L1 sont documentés par Développeur/QA et UX.

Les corrections de récompenses déjà intégrées sont à conserver : une vague active ou perdue n'est pas terminée ; zéro vague terminée donne zéro étoile ; les vagues réellement franchies sont acquises ; une tentative est récompensée une seule fois ; les acquis existants ne sont pas retirés. Le profil de développement reste séparé du profil normal.

Cette mission ne modifie ni les statistiques, ni les prix, ni les revenus, ni le calendrier des vagues, ni les graphismes. Elle ne nécessite pas de changement de clé normale ou de version de sauvegarde 38.

## 1. Règle des cœurs retenue

**Une reprise se paie avec les cœurs disponibles dans le checkpoint précédant la préparation de la vague échouée.** La reprise restaure cet état et consomme exactement un de ces cœurs. Cette règle correspond au comportement actuellement exécuté par `canRetryWave` et `retryWave` ; elle est conservée pour corriger L1 sans introduire une nouvelle capacité.

Le commentaire historique disant qu'un cœur gagné pendant la vague perdue peut payer sa reprise est contradictoire avec cette exécution. Il doit être aligné sur la règle conservée. Il ne justifie pas d'ajouter automatiquement les nouveaux cœurs de la vague perdue au checkpoint.

Un cœur obtenu sur un boss est disponible pour les vagues suivantes si la vague est effectivement franchie et son état acquis. S'il a été obtenu dans une vague ensuite perdue, la reprise annule ce gain en même temps que les autres gains de cette vague. Les cœurs déjà présents au checkpoint ne disparaissent pas à cause d'un changement de terrain ou d'un rechargement.

| Cœurs du checkpoint | Cœurs visibles en fin de vague perdue | Reprise possible | Après une reprise acceptée |
| --- | --- | --- | --- |
| 0 | 0 | Non | Aucun prélèvement ni restauration |
| 1 | 1 | Oui | 0 dans l'état actif, le checkpoint et le report de tentative |
| 2 | 2 | Oui | 1 dans les trois représentations ; une autre reprise peut ensuite consommer le dernier |
| 0 | 1, cœur gagné dans la vague perdue | Non | Le nouveau gain ne crée pas un droit à reprendre cette vague |
| 1 | 2, dont un cœur gagné dans la vague perdue | Oui | 0 après restauration : le cœur initial est consommé et le nouveau gain est annulé |

Les deux dernières lignes sont des cas de contrôle de la règle, pas des simulations de combat représentatives. Un `max(checkpoint.retries, g.retries)` appliqué généralement aux vagues de boss modifierait cette règle ; il est exclu.

## 2. Transition entre terrains et réparation v38 limitée

À l'entrée d'un terrain, `g.retries`, `runHearts` et `buildCheckpoint.retries` doivent refléter le même nombre de cœurs reportés, avant la sauvegarde finale de cette transition. Le checkpoint doit décrire le nouvel état de préparation du terrain, pas l'armée ou les Z du précédent.

| Cœurs reportés | État actif / report / checkpoint du terrain suivant | Première défaite, puis reprise | Deuxième défaite, puis reprise |
| --- | --- | --- | --- |
| 0 | 0 / 0 / 0 | Aucune reprise | Sans objet |
| 1 | 1 / 1 / 1 | Reprise vers 0 / 0 / 0 | Aucune reprise |
| 2 | 2 / 2 / 2 | Reprise vers 1 / 1 / 1 | Reprise vers 0 / 0 / 0 ; aucune troisième |

Le défaut de référence vient de la création du checkpoint dans `resetGame` avant restauration de `g.retries` dans `startLevel`. La correction doit synchroniser l'état final du nouveau terrain et son checkpoint ; le joueur ne doit pas voir des cœurs reportés que le checkpoint refuse d'utiliser dès la première vague.

### Sauvegardes anciennes déjà touchées

Une réparation ciblée est justifiée lorsqu'une ancienne sauvegarde réunit les conditions suivantes :

- terrain d'indice strictement supérieur à zéro ;
- tentative non finalisée (`runEnded` faux) ;
- checkpoint de début de terrain, vague zéro et zéro reprise, structurellement cohérent ;
- état actuel en préparation initiale ou première vague (`g.wave` zéro ou un) ;
- un ou deux cœurs actuellement présents, avec accord du report de tentative et de `g.retries`.

La première vague n'a pas de boss ; aucun cœur ne peut y avoir été gagné par la logique du jeu. Dans ce cas précisément, copier le nombre de cœurs déjà présent vers le checkpoint ne crée pas de nouvelle ressource : cela rétablit le report perdu dans le checkpoint. Les Z, tours, vies et autres champs du checkpoint restent inchangés. La réparation est idempotente au chargement suivant.

Ne pas étendre cette réparation aux vagues ultérieures, aux checkpoints contradictoires ou à un solde de cœurs incohérent. Une ancienne tentative déjà finalisée peut contenir `runEnded=true`, `runHearts=0` et encore des cœurs dans `g.retries` ; elle ne doit pas être rouverte après versement d'étoiles. Son solde permanent et son reçu restent acquis, sans deuxième versement. Un état dont l'origine ne peut être établie ne justifie pas d'inventer un cœur ou d'annuler une récompense passée.

## 3. Budget et état restaurés lors d'une reprise

Le checkpoint est pris après la précédente vague acquise, ou à la préparation initiale du terrain. Les achats, évolutions et gains postérieurs ne sont pas incorporés rétroactivement au checkpoint. La reprise doit :

- rétablir les Z, tours, niveaux et vies présents dans le checkpoint ;
- annuler les achats et évolutions faits après celui-ci, en restaurant l'état, sans ajouter de remboursements séparés ;
- annuler les Z et cœurs gagnés dans la vague échouée ;
- repartir en préparation, avec le même numéro de dernière vague terminée ;
- supprimer les ennemis et effets de combat temporaires, comme prévu par `snapshotBuild` ;
- consommer exactement un cœur dans l'état restauré, le checkpoint et `runHearts` ;
- ne pas attribuer d'étoiles, modifier les paliers permanents ou ajouter un record pour la vague perdue.

**Exemple de contrôle.** Checkpoint avec 410 Z, 12 vies, un Raphaël forme I et deux cœurs. Après ce checkpoint, une évolution coûte 90 Z et un Tom 35 Z ; la vague apporte ensuite 53 Z avant la défaite. L'état échoué contient donc 338 Z et des achats supplémentaires. La reprise doit rendre **410 Z, 12 vies, le seul Raphaël forme I et un cœur**. Elle ne doit pas donner 535 Z en restaurant le budget puis en remboursant une deuxième fois les achats. Si la même préparation est modifiée puis échoue à nouveau, le deuxième retour donne toujours 410 Z et la même tour, avec zéro cœur. Les chiffres sont une fixture de budget légal, pas une modification de prix ou un résultat de partie jouée.

Un rechargement après consommation doit garder le cœur consommé. Il ne recrée ni la reprise ni les Z de la vague échouée. Les pertes de vies des vagues précédemment acquises restent présentes dans le checkpoint : la reprise n'est pas une remise arbitraire à quinze vies.

## 4. Reprendre fidèlement pause et vitesse

La vitesse choisie est sauvegardée, et le format 38 continue d'être accepté. Une ancienne sauvegarde sans vitesse explicite reprend à **×1**, valeur historique de repli. Les vitesses légales restent **×1, ×2, ×3** : il ne s'agit pas d'ajouter une nouvelle accélération.

| Situation sauvegardée | Résultat après Continuer |
| --- | --- |
| Combat en pause, ×1 / ×2 / ×3 | Combat toujours en pause, même vitesse, aucune progression avant action de reprise |
| Combat non pausé, ×1 / ×2 / ×3 | Combat reprenant selon cet état, même vitesse |
| Préparation de vague | Même préparation, Z/tours/vies inchangés par le seul chargement |
| Atelier ou récompenses ouverts | Dialogue restauré et simulation arrêtée ; fermer/rejouer suit le parcours prévu |
| Ancien format 38 sans champ de vitesse | ×1, sans perte des autres champs valides |

La restauration d'un combat sauvegardé en pause ne doit pas être annulée par un appel de nettoyage d'interface qui remettrait `paused=false`. Les sauvegardes effectuées après le chargement doivent garder le bon état, y compris lors d'un second rechargement. En pause, les compteurs de simulation, positions, apparitions et budgets ne doivent pas avancer ; les animations d'interface sans effet de jeu ne constituent pas une reprise du combat.

Ce contrat conserve le choix du joueur ; il ne remplace pas ce choix par une nouvelle politique générale de pause à chaque interruption. Il n'impose pas non plus une modification du fonctionnement de ×1/×2/×3 pendant une partie neuve.

## 5. Préservation de la progression et critères de revue

- Clé normale `friends-defense-save-v38`, version 38 et origine du site conservées ; profil de développement toujours isolé.
- Étoiles, achats permanents, meilleur record et achèvement acquis préservés au chargement et après reprise.
- Compteur de vagues terminées et formule de récompense de la PR précédente inchangés ; aucune étoile en plus pour la seule consommation d'une reprise.
- Régressions couvrant les reports 0/1/2, les six transitions de terrain, la première défaite, les consommations successives et le rechargement après consommation.
- Cas négatifs pour ne pas attribuer un cœur d'une vague de boss perdue au checkpoint et ne pas rouvrir une tentative déjà récompensée.
- Tests des états pause/vitesse, du repli ×1 des anciennes sauvegardes et de la conservation sur deux chargements.
- Revue des différences confirmant l'absence de retouche des statistiques, des prix, des revenus, des sprites et des mécanismes de récompense déjà corrigés.

Les calculs de contrat et les relectures de source sont distincts des essais du jeu. Les résultats réellement exécutés seront consignés par QA et par le coordinateur ; ce document ne prétend pas qu'une matrice de scénarios constitue une campagne jouée ou une validation sur téléphone réel. La livraison suit la procédure automatisée du dépôt après réussite des contrôles requis ; un test en échec arrête cette livraison.

## Corpus indépendant de compatibilité v38

Un corpus structurel de **1 252 sauvegardes** a été produit dans `/tmp/fd-gd-l1/legacy-corpus.json`, à partir d'une copie de `index.html` du commit déployé `14361f3301c4ceaa6f4d5d12e689da15b16936c5`. Il utilise son noyau réel, `buildSaveData`, `damageFeedback` et `tickFeedback` ; les hooks sonores et certains retours décoratifs sans effet sur le combat sont neutralisés. Le générateur ne lit pas le fichier de jeu en cours de modification. Les cas portent le commit source, leur identifiant et leurs hypothèses.

Couverture : sept cartes, profils permanents entièrement à zéro ou à trois, formes de combat I/II/III achetées avec les API du noyau, première vague et vagues 4/5/7/10, puis captures à pas fixe `1/60 s`. Pour les vagues avancées, la préparation, un budget de 5 000 Z et les compteurs historiques sont **injectés et déclarés** afin d'obtenir les formes et états à couvrir. Les cœurs reportés des cas de transition sont également injectés avant exécution de l'ordre historique de création du checkpoint. Il ne s'agit ni d'une campagne jouée, ni d'une validation de l'économie, ni d'une recherche de stratégie optimale.

Le corpus contient 924 états actifs, 291 captures avec volants, 44 avec boss, 779 avec effets `g.fx`, 318 avec zones, 180 avec impacts retardés, 455 avec `damageTag`, 246 avec flash et 67 avec marquage. Les compteurs se recoupent. Il comprend aussi **569 cas avec cooldown de tour négatif**, **110 avec horloge d'apparition négative** et **48 cas de checkpoint initial décalé malgré des cœurs reportés**, tous produits selon les appels décrits. Les nombres négatifs de cooldown/horloge peuvent être légitimes : ils ne doivent pas être confondus avec une corruption par un validateur trop strict.

Le corpus est temporaire et n'est pas ajouté au dépôt. Son acceptation par le validateur final et les tests de chargement doivent être consignés séparément après exécution ; sa seule génération ne prouve pas que la nouvelle validation conserve toutes les sauvegardes.
