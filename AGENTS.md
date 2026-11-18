# Friends Defense — consignes des agents

## Portée et contexte

Ces consignes s'appliquent à tout le dépôt et aux quatre rôles ci-dessous. Les instructions explicites de l'utilisateur définissent le périmètre de chaque tâche et priment sur ce guide. Un rôle est une responsabilité ; une même personne ou un même agent peut en assurer plusieurs si nécessaire.

Friends Defense est un tower defense roguelite en français, destiné notamment au mobile. Le code actuel est autonome : `index.html` contient l'interface, les styles, la logique JavaScript, le rendu Canvas 2D et les images intégrées. La campagne comporte sept terrains de dix vagues et cinq héros. Vérifier ces faits dans la révision étudiée avant de s'en servir comme référence.

Une mission d'audit ou de documentation ne modifie pas `index.html`, les mécaniques, les statistiques, les graphismes ou le format des sauvegardes. Une mission d'implémentation reste limitée à son objectif explicite.

## Règles communes

1. Lire ce fichier et [la méthode de collaboration](docs/COLLABORATION.md) avant de travailler. Identifier la branche, le commit de référence, les modifications locales et les consignes plus spécifiques éventuelles.
2. Préserver les modifications existantes. Travailler sur une branche dédiée, sans push direct sur `main`. Les branches, commits, PR, fusions et déploiements des missions Friends Defense sont autorisés selon la procédure de livraison automatisée ci-dessous, sauf restriction explicite de la mission.
3. Relier chaque changement au besoin demandé et à un critère d'acceptation observable. Avancer sur les choix courants ; demander une précision seulement si une décision importante reste indéterminée ou dépasse le périmètre autorisé.
4. Distinguer les faits vérifiés, les hypothèses, les propositions et les résultats mesurés. Citer le commit, les fonctions ou les données concernés. Ne jamais présenter une simulation ou une émulation comme une partie humaine ou un essai sur téléphone réel.
5. Garder les cinq héros et leurs identités. Ne pas les renommer, les remplacer, les fusionner ou changer leur rôle fondamental dans une tâche qui ne le demande pas.
6. Préserver la langue française, la lisibilité tactile, les parcours de progression et les sauvegardes. Éviter les dépendances réseau, frameworks ou étapes de compilation sans besoin établi.
7. Limiter les diffs à la tâche. Ne pas reformater tout `index.html`, réencoder ses images ou remplacer ses gros blocs de données pour une correction locale. Examiner les lignes minifiées avec des extractions ciblées qui masquent les données base64 dans les sorties.
8. Ne pas modifier simultanément un fichier partagé depuis plusieurs agents. Déclarer les fichiers et zones de travail ; appliquer les règles d'intégration du guide de collaboration.
9. Choisir une validation proportionnée au risque. Une modification documentaire demande une relecture et un contrôle du diff ; une modification de combat ou de sauvegarde demande des vérifications de comportement. Ne pas créer des tests qui ne font que recopier l'implémentation.
10. Livrer un résultat vérifiable : fichiers changés, comportement attendu, contrôles exécutés et leurs résultats, limites et points restant à traiter. Ne pas déclarer un test réussi s'il n'a pas été exécuté.

## Livraison automatisée autorisée

Le 18 novembre 2026, l'utilisateur a demandé de gérer les branches, commits, PR, fusions et déploiements de Friends Defense sans lui demander de manipuler GitHub. Cette autorisation s'applique aux missions demandées ; elle ne dispense ni des contrôles ni du respect de leur périmètre.

1. Récupérer le dernier `main`, examiner les modifications locales et synchroniser la branche dédiée sans écraser de travail. Réutiliser la PR existante du même correctif lorsqu'elle est ouverte.
2. Exécuter les contrôles adaptés. Pour une modification du jeu : `node tests/rewards.test.cjs` et `python -B -m unittest discover -s tests -p 'test_*.py' -v`, puis les tests ciblés nécessaires à la tâche. Un refus de lancement n'est pas un résultat réussi.
3. Vérifier les sauvegardes avec des fixtures et profils isolés : clés/version, étoiles, pouvoirs, records, complétion et rechargements. Ne pas effacer de données réelles, retirer rétroactivement des acquis ou changer l'origine du site pour livrer un correctif.
4. Si un contrôle échoue ou si un risque de perte de sauvegarde est détecté, arrêter la publication et la fusion, conserver le travail et expliquer précisément le problème. Ne pas contourner les protections de branche ou présenter un contrôle incomplet comme validé.
5. Lorsque tous les contrôles réussissent, pousser la branche, créer ou mettre à jour la PR avec les résultats et limites, puis la fusionner dans `main`. Vérifier le SHA exact de sa tête au moment de la fusion ; si la base ou le code a changé depuis les tests, réévaluer et relancer les contrôles concernés.
6. Suivre le déploiement GitHub Pages existant, vérifier le commit déployé et le contenu servi, puis charger le jeu dans un profil de navigateur isolé. Préserver l'URL et les données du joueur ; ne pas confondre une réponse HTTP 200 avec un chargement fonctionnel réussi.
7. Rapporter le résultat, les modifications, les tests et les problèmes éventuels. Une consigne spécifique telle que « ne pas fusionner » ou « ne pas publier le site » suspend les étapes correspondantes pour cette mission.

## Références du code actuel

Ces noms servent de points d'entrée, pas d'API immuable. Rechercher les fonctions dans le code plutôt que se fier à des numéros de ligne.

| Domaine | Points d'entrée |
| --- | --- |
| Héros, cartes, évolutions, bonus | `D`, `MAPS`, `META`, `B` |
| Difficulté, économie, vagues | `STAGE_SCALE`, `MAP_HP`, `ECON_STAGE`, `spawn`, `wavePay`, `rewardFor` |
| Placement et combat | `path`, `buy`, `upgrade`, `stats`, `attack`, `step` |
| Interface et tactile | `init`, `sync`, `fit`, événements `pointer*`, styles sous `#fd15` |
| Images et rendu | `GRAPHICS`, `skinSprite`, `renderHeroBoard`, `draw` |
| Sauvegarde et progression | `buildSaveData`, `readSaveData`, `applyLoadedSave`, `saveProgress`, `snapshotBuild`, `finishRun` |

## Rôle 1 — Game Designer

### Mission

Évaluer et concevoir l'équilibrage, la progression de difficulté, les statistiques, l'économie roguelite et les stratégies viables. Maintenir des choix tactiques compréhensibles et une utilité propre à chaque héros.

### Méthode

- Relever les valeurs réelles : prix d'achat et d'évolution, dégâts, cadence, portée terrestre et aérienne, zones, contrôle, armure, boucliers, régénération, revenus, vies et reprises.
- Séparer les évolutions achetées pendant une tentative des trois paliers permanents payés en étoiles. Suivre leurs interactions et éviter de compter un bonus deux fois.
- Étudier les sept terrains, leurs chemins, les vagues mixtes et aériennes, les boss des vagues 5 et 10 et les déblocages. Vérifier dans le code le calendrier des bonus ; certains libellés historiques peuvent être périmés.
- Comparer plusieurs profils de progression permanente, dont aucun achat, des achats intermédiaires et le maximum. Couvrir des stratégies mixtes et spécialisées, avec des budgets légaux.
- Calculer le DPS théorique puis expliquer ses limites : portée, trajet, sur-dégâts, acquisition de cibles, ralentissements, résistances et interactions de zones. Ne pas conclure sur le seul DPS affiché.
- Pour les simulations, documenter commit, paramètres, placement, politique d'achat, événements et nombre de parties. Fixer les graines si un aléa intervient ; sinon documenter les scénarios déterministes. Utiliser la logique réelle ou expliciter et vérifier les écarts du modèle.
- Mesurer au minimum la vague atteinte, les vies perdues, les dépenses, le revenu, les étoiles gagnées et le temps de progression. Définir les objectifs chiffrés avant de proposer un réglage ; ne pas inventer un taux de victoire sans protocole.
- Contrôler l'emballement économique, les stratégies dominantes, les blocages de progression et les possibilités de répéter des récompenses. Examiner séparément le mode hardcore.

### Livrables et limites

Fournir un diagnostic sourcé, un tableau avant/après des valeurs proposées, les scénarios reproductibles et leurs résultats, les effets attendus et les compromis. Remettre les propositions au Développeur / QA pour intégration ; ne pas modifier le combat, les sauvegardes ou les ressources graphiques dans le cadre d'une simple étude.

## Rôle 2 — UX/UI Designer

### Mission

Rendre les menus, la préparation, le combat et la progression compréhensibles sur un écran mobile, avec une ergonomie tactile et un feedback lisible.

### Méthode

- Examiner le parcours complet : nouvelle partie ou reprise, atelier, achat et placement, prévisualisation, évolution, lancement de vague, pause, bonus, défaite, reprise par cœur, récompenses et terrain suivant.
- Séparer visuellement et verbalement argent de la tentative, étoiles permanentes, vies de la base et cœurs de reprise. Expliquer le coût et la conséquence d'une action avant son déclenchement.
- Décrire pour chaque contrôle les états normal, sélectionné, indisponible, actif et erreur. Un achat impossible doit donner une raison utile ; un retour visuel ne doit pas masquer le plateau.
- Viser des cibles tactiles d'au moins 44 × 44 pixels CSS, idéalement 48 lorsque l'espace le permet. Vérifier les zones réellement cliquables, l'espacement et les gestes de placement avec annulation du pointeur.
- Étudier les petites largeurs, les faibles hauteurs, le paysage, les zones sûres et les barres du navigateur. Vérifier que les panneaux restent utilisables sans cacher les actions essentielles.
- Préserver le contraste, les tailles de texte lisibles, les libellés accessibles et les indicateurs qui ne reposent pas seulement sur une couleur ou un son. Prévoir focus clavier, gestion du focus des dialogues et réduction des animations selon le contexte.
- Vérifier le feedback des dégâts, du gel, des boss, des récompenses, de la sauvegarde et des erreurs sans multiplier les informations concurrentes. Aligner le texte affiché sur les règles réelles.

### Livrables et limites

Fournir les problèmes avec étapes de reproduction, tailles d'écran et conséquences ; proposer les parcours, textes, états et maquettes nécessaires, accompagnés de critères d'acceptation. Coordonner les besoins d'icônes avec le Pixel Artist. Une proposition d'interface ne change pas implicitement l'économie, la difficulté ou l'identité des héros.

## Rôle 3 — Pixel Artist

### Mission

Produire des sprites chibi anime, animations, personnages et icônes cohérents avec les ressources existantes. Le nom du rôle n'autorise pas à convertir tout le jeu dans un nouveau style pixel art.

### Héros à respecter

| Héros | Identité de jeu | Formes actuelles |
| --- | --- | --- |
| Tom | Rapide, tirs multiples | Tom → Tom énervé → Tom incontrôlable |
| Raphaël | Sniper, rayon laser | Raphaël → Raphaël concentré → Raphaël ultime |
| Ylvine | Explosion et zone | Ylvine → Ylvine survolté → Ylvine destructeur |
| Jordan | Ralentissement et gel | Jordan → Jordan glacial → Jordan polaire |
| POY | Puissance et grandes zones | POY → SUPER POY → POY APOCALYPSE |

### Méthode

- Inspecter les portraits, icônes, atlas et animations de la révision de départ avant de dessiner. Préserver silhouettes, visages, coiffures, signes distinctifs, couleurs et lisibilité des cinq héros à petite taille.
- Distinguer les trois formes de combat des effets des évolutions permanentes. Maintenir l'identification du héros entre portrait, boutique et plateau.
- Confirmer le contrat technique avant export : dimensions, nombre et ordre des images, transparence, marges, ancrage au sol, durée, bouclage et échelle à l'affichage.
- À la référence actuelle, le rendu des feuilles d'animation utilise des cases de 160 × 160 pixels, quatre images de repos et six d'attaque ; l'atlas utilise des cases de 128 × 128. Vérifier les consommateurs du code avant toute livraison.
- Garder un cadrage stable d'une image à l'autre, sans tremblement involontaire, débordement, fond opaque ou frange de transparence. Montrer une prévisualisation animée à la taille réelle d'utilisation.
- Rendre les effets identifiables sans masquer les ennemis, leurs barres de vie ou le chemin. Coordonner contraste et icônes avec l'UX/UI Designer et chronologie des attaques avec le Développeur / QA.
- Livrer les variantes et sources séparément, avec noms stables, poids et manifeste de ressources. Justifier l'augmentation de taille ou de mémoire ; ne pas réencoder toutes les images existantes pour remplacer une seule ressource.

### Livrables et limites

Fournir une planche de comparaison avec l'existant, les ressources exportées, les aperçus et le manifeste technique. Le Développeur / QA intègre les ressources dans `GRAPHICS` et vérifie leur rendu. Ne pas changer les statistiques, le rythme du combat ou les cinq identités sous couvert d'une retouche graphique.

## Rôle 4 — Développeur / QA

### Mission

Intégrer les propositions retenues dans le périmètre demandé, garantir le comportement du jeu, sa compatibilité mobile et la préservation des sauvegardes. Assurer la coordination technique lorsque plusieurs rôles travaillent en parallèle.

### Implémentation et intégration

- Définir le contrat entre conception et code : valeurs, textes, ressources, états et critères de réussite. Résoudre les divergences avec le rôle concerné avant de combiner des changements incompatibles.
- Maintenir un seul intégrateur à la fois sur `index.html`. Intégrer les livrables successivement avec des commits ciblés ; examiner les zones partagées et les gros blocs d'images après chaque intégration.
- Garder la page autonome et compatible avec le déploiement existant. Ne pas ajouter un backend, une migration d'architecture ou une chaîne de compilation sans demande correspondante.

### Sauvegardes

- La référence actuelle utilise `friends-defense-save-v38`, un objet de version `38` et les réglages `friends-defense-settings-v15`. Préserver clés, format, progression permanente, étoiles, terrain, tentative, état de combat et checkpoint de reprise dans les tâches qui ne demandent pas leur évolution.
- Pour un changement de schéma demandé, prévoir une migration explicite, idempotente et testée depuis des exemples de l'ancien format. Ne pas écraser silencieusement les données non reconnues ou illisibles.
- Tester, selon la zone touchée, sauvegarde/rechargement pendant la préparation, le combat, une pause, le choix de bonus, la défaite avec reprise, les récompenses et l'atelier. Vérifier étoiles et achats après rechargement, absence de double récompense et coût correct des reprises.
- Couvrir une sauvegarde absente ou corrompue et l'indisponibilité de `localStorage`. Utiliser un profil de navigateur de test et des données synthétiques ; ne pas effacer une sauvegarde réelle pour exécuter un test et ne pas la committer.

### Validation

- Vérifier d'abord le diff et la syntaxe du JavaScript extrait en mémoire. La validité syntaxique ne prouve pas le bon fonctionnement dans un navigateur.
- Pour un changement fonctionnel, exécuter les parcours concernés : route toujours accessible, achats/remboursements, évolutions, ciblage terrestre et aérien, bonus, boss, fin de terrain, progression et sauvegardes selon le risque.
- Vérifier au minimum des vues 320 × 568, 390 × 844 et 844 × 390 pixels CSS pour les changements d'interface. Couvrir Chromium et, lorsque l'environnement le permet, WebKit/Safari et un appareil tactile réel ; indiquer précisément ce qui a été émulé ou n'a pas pu être testé.
- Observer erreurs console, chargement des images, audio après interaction, gestes tactiles, redimensionnement et fluidité en situation chargée. Comparer les performances à une référence mesurée sur le même environnement.
- Reproduire un défaut avant de le corriger lorsque possible. Ajouter un test de régression utile pour les comportements fragiles, surtout combat et sauvegardes ; ne pas imposer une suite fonctionnelle à une PR uniquement documentaire.
- Rédiger la PR avec problème, résultat, portée, validations réellement exécutées et limites. Effectuer la fusion et le suivi GitHub Pages selon la procédure de livraison automatisée, sous réserve des restrictions spécifiques de la mission.
