# Correctif GD-01 / QA-02 — progression sur vagues terminées

## Demande et base de travail

Corriger l'attribution d'étoiles et de records, conserver les gains légitimes après défaite, isoler le mode développeur et préserver les sauvegardes acquises. Aucun changement de graphismes, de statistiques, de prix, de difficulté ou de site public n'est autorisé dans cette mission.

La préparation commence sur `0e14138bc42eefbfcb7dcef06be3f955d328292d`, dernier `main` disponible à son lancement. Les PR nº 1 et nº 2 étaient encore ouvertes ; l'utilisateur a confirmé qu'il les fusionnerait lui-même et que la PR du correctif serait publiée **après** leur intégration. Le coordinateur vérifiera cette base avant publication, sans fusionner de PR lui-même.

Les consignes `AGENTS.md` et `docs/COLLABORATION.md` ont été lues depuis leur commit `e882b2278c9dfc99a06be89ef025743de988d81b` pendant cette préparation. La base finale et les résultats seront consignés ci-dessous.

## Responsabilités et réservations

| Rôle | Fichiers réservés | Responsabilité |
| --- | --- | --- |
| Game Designer | `docs/design/fix-progression-rewards.md` | Contrat des vagues terminées, cas chiffrés, conservation des récompenses légitimes et des valeurs d'équilibrage |
| Développeur / QA | `index.html`, `tests/`, `docs/qa/fix-progression-rewards.md` | Intégration unique, tests automatisés, compatibilité des sauvegardes et résultats |
| UX Designer | `docs/ux/fix-progression-rewards.md` | Textes, compteurs de fin de tentative et compréhension du profil de test ; vérification ciblée |
| Coordinateur | Ce document, opérations Git et PR | Arbitrage, revue du code et du périmètre, validation de la base et livraison sans fusion ni déploiement |

Les trois spécialistes travaillent en parallèle sur leurs fichiers réservés. Seul le Développeur / QA écrit `index.html`. Les essais utilisent des profils synthétiques isolés et ne touchent pas aux sauvegardes du joueur.

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

Correctif implémenté et vérifié localement. Publication en attente de l'intégration par l'utilisateur des PR nº 1 et nº 2 ; aucun push du correctif, aucune fusion et aucun déploiement n'ont été effectués à ce stade.

- [Contrat Game Designer et matrices des sept terrains](../design/fix-progression-rewards.md).
- [Contrat et vérifications UX](../ux/fix-progression-rewards.md).
- [Implémentation et résultats Développeur / QA](../qa/fix-progression-rewards.md).
- [Commandes des tests et limites](../../tests/README.md).

### Résultats de la revue finale

| Contrôle | Résultat |
| --- | --- |
| `node tests/rewards.test.cjs` | 21 cas réussis ; réexécutés par le coordinateur sur le code final |
| `python -B -m unittest discover -s tests -p 'test_*.py' -v` | 9 tests réussis, suite finale en 20,157 s, y compris mode test jusqu'à la fin des sept terrains et rechargement |
| Contrôle négatif sur l'ancien `index.html` | L'assertion « vague 1 active = zéro vague terminée » échoue bien avec valeur réelle 1 au lieu de 0 ; elle passe sur le correctif |
| Périmètre du code | Noyau `D` → `GRAPHICS`, styles, 52 images intégrées et SVG identiques à la référence ; aucune valeur d'équilibrage ni ressource modifiée |
| Sauvegardes | Fixture synthétique v38, acquis conservés, reçus anciens non repris à la baisse, fin non créditée réglée une seule fois, clés normales inchangées |
| Isolation du mode test | Bouton normal caché et gardé ; sept victoires de test donnent 36 étoiles uniquement au profil de test ; rechargement sans double crédit et profil normal retrouvé intact |
| Relectures | Game Designer favorable sur les fonctions finales ; UX favorable sur compteurs, coches, textes et distinction du profil de test ; Développeur / QA a exécuté et décrit les parcours automatisés |

Snapshot final de `index.html` vérifié : SHA-256 `414d498f6328a56c43d831432f8f978cf41fdeadac1780a8e3d00cc7d57d6edc`. Noyau de combat inchangé : SHA-256 `31c22e85fafd867bbe0cc886cfbd8b01d03a727c96e79c4f6617a2421e84f055`.

Le premier lancement navigateur dans le bac à sable n'a exécuté aucun test, car les sockets y sont interdites. La suite finale a été exécutée dans l'environnement autorisant le serveur lié à `127.0.0.1`, puis serveur et navigateur ont été arrêtés. Cela n'a créé ni modifié aucun site public.

Limites : Chromium headless et profils synthétiques ; aucune campagne humaine complète, aucun essai Safari/WebKit ou appareil réel. Les défauts de checkpoint, de pause/vitesse et de validation générale du stockage restent hors du correctif. La séparation du mode test n'est pas un mécanisme anti-triche contre une modification manuelle du navigateur.
