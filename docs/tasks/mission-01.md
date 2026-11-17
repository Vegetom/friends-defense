# Mission 01 — audit collaboratif de Friends Defense

## Cadrage

- **Demande :** faire analyser le jeu par quatre spécialistes, retenir cinq améliorations par rôle et consolider une feuille de route avant validation de l'utilisateur.
- **Référence du jeu :** dernière version de `origin/main` récupérée au début de la mission, commit `0e14138bc42eefbfcb7dcef06be3f955d328292d`.
- **Branche de livraison :** `docs/mission-01-collaborative-audit`, créée directement depuis cette référence de `main`.
- **Consignes lues :** `AGENTS.md` et `docs/COLLABORATION.md` au commit `e882b2278c9dfc99a06be89ef025743de988d81b`, dans la [PR d'organisation nº 1](https://github.com/Vegetom/friends-defense/pull/1). Ces fichiers ne sont pas encore présents dans `main` à la référence analysée. La mission les applique sans fusionner ni recopier cette PR dans la nouvelle branche.
- **Coordination :** agent principal, responsable du cadrage, de la consolidation, de la vérification du périmètre et des opérations Git.
- **Périmètre autorisé :** rapports et recommandations ; lectures du code et des ressources, calculs et vérifications dans des fichiers temporaires ou profils de test isolés.
- **Contraintes :** aucune modification de `index.html`, des ressources, des mécaniques ou des sauvegardes du joueur ; aucune fusion automatique de PR.

## Répartition et réservations

Quatre agents distincts ont été lancés en parallèle sur le même dossier et la même référence. Les opérations Git et les documents communs sont réservés au coordinateur.

| Responsable | Fichier réservé | Travail demandé |
| --- | --- | --- |
| Game Designer (`game_designer`) | [Analyse game design](../design/mission-01.md) | Difficulté des sept terrains, économie roguelite, possibilités de simulation et cinq recommandations |
| UX/UI Designer (`ux_designer`) | [Analyse UX/UI](../ux/mission-01.md) | Parcours, tactile, petits écrans, lisibilité, feedback et cinq recommandations |
| Pixel Artist (`pixel_artist`) | [Analyse graphique](../art/mission-01.md) | Ressources existantes, cohérence des cinq héros, animations, effets et cinq recommandations |
| Développeur / QA (`developer_qa`) | [Analyse technique et QA](../qa/mission-01.md) | Sauvegardes, progression, compatibilité, architecture, tests et cinq recommandations |
| Chef de projet / coordinateur | Ce document et [la feuille de route](../reports/mission-01-roadmap.md) | Contradictions, arbitrages proposés, ordre, dépendances et critères de validation |

Les expériences temporaires restent hors du dépôt. Les observations du navigateur, s'il y en a, utilisent des profils synthétiques séparés. Les résultats de chaque rôle précisent leur protocole et leurs limites.

## Contrat de restitution

Chaque recommandation porte un identifiant stable (`GD`, `UX`, `ART` ou `QA` suivi d'un numéro), une preuve reliée au code ou à une observation, l'effet attendu pour le joueur, une proposition, son niveau de confiance et des critères d'acceptation. Les constats vérifiés, hypothèses et choix de produit doivent rester distingués.

Le coordinateur regroupe les doublons sans supprimer les désaccords, présente les compromis et propose les priorités. Une proposition dans le rapport n'autorise pas son implémentation.

## Critères d'acceptation de cette mission

1. Les quatre rapports contiennent chacun cinq recommandations hiérarchisées et sourcées.
2. L'analyse game design couvre les sept terrains, les deux économies et un protocole réaliste de simulation automatique, avec une distinction entre calculs et parties simulées.
3. La synthèse établit les recoupements, contradictions, dépendances et critères de passage de la feuille de route.
4. Les méthodes exécutées et les vérifications manquantes sont explicites ; aucun test sur appareil réel ou taux de victoire n'est revendiqué sans mesure.
5. La PR n'ajoute que les documents de cette mission ; `index.html` reste identique octet pour octet à la référence de départ.
6. Une PR distincte est ouverte vers `main` et reste non fusionnée pour validation des recommandations.

## État

Analyses et consolidation vérifiées, prêtes pour livraison dans une PR distincte. Les recommandations attendent la validation de l'utilisateur ; aucune implémentation n'est engagée.

## Résultats et contrôles

- Les quatre spécialistes ont remis chacun cinq recommandations, avec preuves, limites et critères d'acceptation. Les vingt identifiants sont cartographiés vers sept lots dans la synthèse.
- Les quatre spécialistes ont relu la synthèse sur leur domaine et confirmé l'absence d'erreur matérielle ou de contradiction factuelle. Les tensions de conception et décisions restantes sont explicites.
- Les essais navigateur, calculs et inspections exécutés sont décrits dans les rapports. Les états synthétiques sont distingués des actions réelles ; les vérifications sur appareils réels, WebKit/Safari et une campagne complète restent à faire.
- Le coordinateur a réexécuté le script Node embarqué dans le rapport GD : calculs des sept terrains, récompenses et trois simulations de vague 1 reproduits avec succès.
- Contrôles documentaires : cinq recommandations ordonnées par rôle, vingt identifiants uniques dans la synthèse et dix liens relatifs valides. Le contrôle des espaces du diff est effectué avant commit.
- Seuls les six documents de mission sont ajoutés. `index.html` est identique octet pour octet à la référence analysée ; SHA-256 : `d0551939e91594ed838b658fb4e9ebfdfe4d57bedae0758be8a29642737ba7aa`.
- Livraison prévue sur la branche dédiée, vers `main`, sans fusion automatique. La PR d'organisation précédente reste indépendante.
