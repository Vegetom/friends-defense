# Collaboration entre les quatre rôles

Ce guide complète [AGENTS.md](../AGENTS.md). Il permet de faire avancer en parallèle les travaux indépendants, puis d'intégrer leurs résultats sans perdre de modifications dans le fichier unique du jeu.

## 1. Cadrer une tâche commune

Le Développeur / QA assure par défaut la coordination technique. Il enregistre le commit de départ, le besoin de l'utilisateur, les contraintes et les critères de réussite. Cette coordination ne donne pas l'autorisation d'élargir la tâche. La livraison des missions suit l'autorisation et les conditions de la section « Livraison automatisée autorisée » d'[AGENTS.md](../AGENTS.md).

Créer une fiche par tâche dans `docs/tasks/<identifiant>.md` lorsque le travail nécessite plusieurs livrables. Pour une petite correction, ces informations peuvent figurer directement dans la PR. Ne pas créer de dossiers vides ou de rapports sans utilité pour la tâche.

```markdown
# <Identifiant — objectif>

- Demande et périmètre autorisé :
- Commit de référence :
- Coordinateur / intégrateur :
- Critères d'acceptation observables :
- Contraintes de sauvegarde, mobile et ressources :
- Sous-tâches, responsables, fichiers réservés et dépendances :
- Contrats convenus : valeurs / textes / ressources / états :
- État : à cadrer | en cours | prêt à intégrer | intégré | vérifié
- Validations prévues puis résultats réellement obtenus :
- Décisions, limites et questions encore ouvertes :
```

Définir des critères adaptés au besoin. Par exemple : une récompense ne peut être encaissée qu'une fois après rechargement, ou le bouton de lancement reste atteignable sur un écran de 320 pixels CSS. Un objectif d'équilibrage doit préciser profil de progression et stratégie de référence.

## 2. Répartir le travail parallèle

| Rôle | Travail indépendant possible | Livrable et emplacement indicatif | Dépendances à résoudre |
| --- | --- | --- | --- |
| Game Designer | Audit des valeurs, stratégies et simulations | `docs/design/<identifiant>.md`, scripts utiles dans `tools/simulations/` | Règles réelles et commit de référence ; hypothèses du modèle |
| UX/UI Designer | Audit des parcours, textes, états et maquettes | `docs/ux/<identifiant>.md` et maquettes associées | Conséquences des actions ; place et fonction des icônes |
| Pixel Artist | Inventaire, études et préparation des ressources | `docs/art/<identifiant>.md`, sources/exports dans `art/<identifiant>/` | Références des héros et contrat de dimensions/animations |
| Développeur / QA | Cartographie du code, plan de test et fixtures synthétiques | `docs/qa/<identifiant>.md`, outils de vérification utiles | Critères et contrats ; résultats des autres rôles pour l'intégration finale |

Les emplacements sont des conventions à utiliser seulement si des fichiers sont nécessaires. Les propositions documentaires et ressources de travail ne deviennent pas automatiquement des ressources chargées par le jeu.

Les quatre audits peuvent démarrer en parallèle sur le même commit. Une maquette qui dépend de statistiques nouvelles, une animation qui dépend d'un nouveau timing d'attaque et les tests finaux attendent le contrat correspondant. Marquer explicitement les hypothèses en attendant sa résolution.

Chaque rôle écrit uniquement ses fichiers réservés. La fiche commune est mise à jour par le coordinateur à partir des comptes rendus ; les autres rôles ne l'écrivent pas simultanément. Les lectures de `index.html` sont partagées, son édition est réservée à l'intégrateur.

## 3. Choisir l'isolation adaptée

### Plusieurs agents dans le même dossier

- Attribuer des fichiers disjoints et annoncer les réservations avant les écritures.
- Réserver les opérations Git qui changent l'état du dépôt au coordinateur : changement de branche, ajout à l'index, commit, rebase et push. Les collaborateurs peuvent consulter le statut et le diff.
- Ne pas utiliser une branche différente par agent dans un même dossier : un changement de branche affecterait tous les agents.
- Ne pas écraser ou rétablir un fichier dont un autre agent est propriétaire. Transmettre une proposition ou demander la libération de sa réservation.

### Plusieurs dossiers ou worktrees

Créer une branche par rôle à partir du même commit de référence. Exemple à adapter ; ne pas réutiliser des branches ou dossiers contenant déjà du travail :

```sh
git fetch origin main
git switch -c feature/<identifiant> origin/main
git rev-parse HEAD
git worktree add ../fd-game-design -b design/<identifiant> <commit-de-reference>
git worktree add ../fd-ux -b ux/<identifiant> <commit-de-reference>
git worktree add ../fd-art -b art/<identifiant> <commit-de-reference>
git worktree add ../fd-qa -b qa/<identifiant> <commit-de-reference>
```

Remplacer les paramètres entre chevrons avant exécution. Un worktree isole les fichiers et l'index Git ; les configurations et références du dépôt restent partagées. Ne pas modifier les références d'une autre branche de rôle.

Les worktrees permettent des prototypes séparés si la tâche les autorise. Ils ne rendent pas sûre l'intégration automatique de plusieurs versions concurrentes de `index.html`. Les rôles livrent de préférence des spécifications ou des patchs ciblés ; le Développeur / QA les applique successivement dans la branche d'intégration.

Si aucun outil multi-agent n'est disponible, la même répartition s'applique séquentiellement. Ne pas prétendre que des agents ont été lancés si seuls des rôles documentaires ont été définis.

## 4. Fixer les contrats entre rôles

Avant l'implémentation des éléments dépendants, consigner les accords nécessaires :

- **Équilibrage → développement :** valeurs avant/après, unités, conditions d'activation, ordre d'application des multiplicateurs et scénarios de validation. Les dates ou numéros de vague du texte doivent correspondre au code.
- **UX → développement :** parcours, textes français, état de chaque contrôle, zones tactiles, comportement des dialogues, gestes et feedback d'erreur.
- **Art → UX et développement :** héros et forme représentés, fichiers, dimensions, transparence, grille, ordre et nombre d'images, ancrage, durée, bouclage et poids.
- **Développement → tous :** points d'entrée touchés, contraintes de sauvegarde et de performance, ordre d'intégration et limites de l'environnement de test.

Les rôles règlent ensemble les choix ordinaires déjà autorisés. Une décision qui dépasse la demande est signalée à l'utilisateur avec une proposition concrète ; le travail indépendant continue entre-temps.

## 5. Intégrer sans conflits de responsabilité

1. Chaque rôle remet son livrable avec commit de référence, hypothèses, fichiers, critères et résultats. Un brouillon n'est pas un accord sur ses valeurs ou son graphisme.
2. Le coordinateur vérifie les dépendances et définit l'ordre ; par exemple données de combat, puis interface correspondante, puis ressources, puis validation des interactions. Une tâche peut nécessiter un autre ordre.
3. Le Développeur / QA intègre un changement cohérent à la fois dans `index.html`, avec un commit ciblé et le contrôle adapté. Les documents et ressources indépendants peuvent être repris par commits séparés.
4. En cas de conflit, comparer les deux intentions à la référence commune. Ne pas accepter globalement « ours » ou « theirs » sur le fichier du jeu ou une ligne base64. Faire relire le résultat au rôle concerné lorsque le conflit affecte son contrat.
5. Après un changement de règles ou de timing, refaire les simulations ou prévisualisations qui en dépendent. Signaler comme périmés les résultats obtenus sur une ancienne version.
6. Chaque spécialiste relit les éléments relevant de son rôle selon le risque ; le Développeur / QA consigne la validation intégrée et les vérifications impossibles dans l'environnement disponible.

Ne pas confondre intégration dans la branche de travail et fusion dans `main`. La seconde suit la procédure automatisée autorisée : contrôles réussis, préservation des sauvegardes, PR à jour et vérification du SHA à fusionner. Une restriction explicite de la mission reste prioritaire.

## 6. Passer en revue et ouvrir la PR

Avant le push, inspecter `git diff --check`, le diff complet, les fichiers inclus et le statut du dépôt. Vérifier que seuls les changements de la tâche sont enregistrés. Contrôler les gros blocs de ressources si le jeu a changé ; pour une PR documentaire, confirmer que `index.html` est identique à la référence.

La description de PR doit présenter :

- Le problème et le résultat attendu, avec le périmètre final.
- Les rôles mobilisés et les décisions utiles à la revue.
- Les validations réellement exécutées, leur environnement et leurs résultats.
- L'effet éventuel sur les sauvegardes, la compatibilité mobile et les performances.
- Les limites restantes et les éléments hors périmètre qui nécessitent une décision.

Pousser uniquement la branche de travail et ouvrir ou actualiser sa PR vers `main`. Après succès de tous les contrôles, effectuer la fusion autorisée et suivre GitHub Pages jusqu'à la vérification du commit, du contenu publié et du chargement du jeu. Utiliser des profils de test isolés et conserver l'URL du jeu. Un test en échec ou un risque de perte de sauvegarde arrête la publication et doit être expliqué.

Si l'accès échoue, distinguer le droit de lecture du dépôt, le droit de pousser une branche, de créer ou fusionner une PR et de consulter le déploiement. Rapporter l'erreur utile et la permission ou connexion manquante sans exposer de jeton. Conserver les commits locaux et les fichiers prêts à examiner ; ne pas demander une intervention GitHub déjà couverte par l'autorisation lorsque les outils permettent d'agir.

## Historique — PR d'organisation

Cette première PR ajoute uniquement `AGENTS.md` et ce guide. Les quatre rôles sont définis, mais aucune modification des mécaniques ou des graphismes n'est incluse. La validation porte sur la cohérence des consignes, les liens relatifs, le diff et l'identité de `index.html` avec le commit de référence ; elle ne constitue pas un test de jouabilité.
