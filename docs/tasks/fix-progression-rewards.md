# Correctif GD-01 / QA-02 — progression sur vagues terminées

## Demande et base de travail

Corriger l'attribution d'étoiles et de records, conserver les gains légitimes après défaite, isoler le mode développeur et préserver les sauvegardes acquises. Les graphismes, statistiques, prix et coefficients de difficulté restent inchangés. La livraison sur GitHub Pages est désormais autorisée après succès des contrôles.

La préparation commence sur `0e14138bc42eefbfcb7dcef06be3f955d328292d`. La PR nº 3 a été ouverte avec le correctif `1e598b6`, puis l'utilisateur a intégré les PR nº 1 et nº 2. La présente livraison est synchronisée avec `main` au commit `94e1a5c00c09129921e6f9a37682af294dffa60a`, qui contient ces deux PR documentaires. Le commit du correctif reste dans l'historique de `fix/completed-wave-rewards`.

Les consignes `AGENTS.md` et `docs/COLLABORATION.md` sont désormais disponibles et lues dans `main`. L'utilisateur a autorisé le 18 novembre la fusion après succès des contrôles et la vérification GitHub Pages, ainsi que cette gestion autonome pour les missions suivantes. Cette procédure est enregistrée dans les deux fichiers de consignes.

## Responsabilités et réservations

| Rôle | Fichiers réservés | Responsabilité |
| --- | --- | --- |
| Game Designer | `docs/design/fix-progression-rewards.md` | Contrat des vagues terminées, cas chiffrés, conservation des récompenses légitimes et des valeurs d'équilibrage |
| Développeur / QA | `index.html`, `tests/`, `docs/qa/fix-progression-rewards.md` | Intégration unique, tests automatisés, compatibilité des sauvegardes et résultats |
| UX Designer | `docs/ux/fix-progression-rewards.md` | Textes, compteurs de fin de tentative et compréhension du profil de test ; vérification ciblée |
| Coordinateur | Ce document, opérations Git et PR | Arbitrage, revue du périmètre, synchronisation, fusion autorisée après contrôles et vérification GitHub Pages |

Les trois spécialistes ont préparé le correctif en parallèle sur leurs fichiers réservés. Seul le Développeur / QA a écrit `index.html`. La présente étape de livraison ne change pas ce code. Les essais utilisent des profils synthétiques isolés et ne touchent pas aux sauvegardes du joueur.

## Contrat retenu

- Une vague active ou perdue n'est pas une vague terminée. Les vagues des terrains précédents restent acquises ; quitter la première vague d'un terrain avancé n'annule pas ces vagues.
- Une tentative sans aucune vague terminée donne zéro étoile et ne crée aucun nouveau record, y compris en cas de défaite.
- Pour une progression positive, la formule existante de récompense est conservée. Une défaite ou un abandon ne supprime pas les gains des vagues réellement terminées.
- La victoire de campagne et son bonus ne résultent que d'une fin légitime de campagne. Une même fin de tentative n'est pas créditée une deuxième fois au rechargement.
- Les étoiles, paliers permanents, records et complétion déjà sauvegardés restent acquis. Aucune correction rétroactive des anciens gains ni migration du format 38 n'est demandée.
- En mode normal, le raccourci développeur est caché et son gestionnaire ne peut pas accorder de victoire. Le mode de test explicite, s'il est activé, utilise un stockage séparé et ne lit ni ne modifie le profil normal.
- Les textes et l'indicateur de progression de fin de tentative utilisent les vagues terminées, sans promettre la récompense de la vague en cours. Aucun nouveau graphisme n'est produit.

## Vérifications prévues

Tests des abandons avant/après lancement et après des vagues terminées ; défaites en première vague et après progression ; fins de terrain et victoire de campagne ; rechargements et actions répétées ; lecture des sauvegardes 38 ; préservation de la progression acquise ; garde développeur en mode normal et isolation du profil de test.

La revue du périmètre comparera le noyau de combat, les données d'équilibrage, les styles et les images intégrées à la référence. Les tests portent sur les fonctions réelles et sur des parcours navigateur isolés ; aucune campagne humaine complète ni compatibilité sur appareil réel ne sera revendiquée sans exécution.

## État et résultats

Correctif implémenté, synchronisé avec `main` et vérifié de nouveau. La PR nº 3 existante est réutilisée ; sa fusion et le suivi du déploiement GitHub Pages sont autorisés après succès des contrôles. Le résultat final de livraison est consigné dans [la PR nº 3](https://github.com/Vegetom/friends-defense/pull/3).

`index.html` et les tests restent identiques au commit `1e598b67a5b3a0d868035fd0093caf90a96525b7`. Les deux suites ont été relancées après la synchronisation du 18 novembre : aucun changement fonctionnel n'a été ajouté, et aucun risque de perte des acquis n'a été détecté dans les cas couverts.

- [Contrat Game Designer et matrices des sept terrains](../design/fix-progression-rewards.md).
- [Contrat et vérifications UX](../ux/fix-progression-rewards.md).
- [Implémentation et résultats Développeur / QA](../qa/fix-progression-rewards.md).
- [Commandes des tests et limites](../../tests/README.md).

### Résultats de la revue finale

| Contrôle | Résultat |
| --- | --- |
| `node tests/rewards.test.cjs` | 21 cas réussis ; réexécutés par le coordinateur sur le code final |
| `python -B -m unittest discover -s tests -p 'test_*.py' -v` | 9 tests réussis après synchronisation, suite en 20,452 s, y compris mode test jusqu'à la fin des sept terrains et rechargement |
| Contrôle négatif sur l'ancien `index.html` | L'assertion « vague 1 active = zéro vague terminée » échoue bien avec valeur réelle 1 au lieu de 0 ; elle passe sur le correctif |
| Périmètre du code | Noyau `D` → `GRAPHICS`, styles, 52 images intégrées et SVG identiques à la référence ; aucune valeur d'équilibrage ni ressource modifiée |
| Sauvegardes | Fixture synthétique v38, acquis conservés, reçus anciens non repris à la baisse, fin non créditée réglée une seule fois, clés normales inchangées |
| Isolation du mode test | Bouton normal caché et gardé ; sept victoires de test donnent 36 étoiles uniquement au profil de test ; rechargement sans double crédit et profil normal retrouvé intact |
| Relectures | Game Designer favorable sur les fonctions finales ; UX favorable sur compteurs, coches, textes et distinction du profil de test ; Développeur / QA a exécuté et décrit les parcours automatisés |

Snapshot final de `index.html` vérifié : SHA-256 `414d498f6328a56c43d831432f8f978cf41fdeadac1780a8e3d00cc7d57d6edc`. Noyau de combat inchangé : SHA-256 `31c22e85fafd867bbe0cc886cfbd8b01d03a727c96e79c4f6617a2421e84f055`.

Le premier lancement navigateur pendant la préparation n'avait exécuté aucun test, car les sockets sont interdites dans le bac à sable. Les suites validées ont été exécutées dans l'environnement autorisant le serveur lié à `127.0.0.1`, puis serveur et navigateur ont été arrêtés. Ces tests locaux ne modifient aucun site public ; la publication réelle se fait ensuite par la fusion et GitHub Pages.

Limites : Chromium headless et profils synthétiques ; aucune campagne humaine complète, aucun essai Safari/WebKit ou appareil réel. Les défauts de checkpoint, de pause/vitesse et de validation générale du stockage restent hors du correctif. La séparation du mode test n'est pas un mécanisme anti-triche contre une modification manuelle du navigateur.
