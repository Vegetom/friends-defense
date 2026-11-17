# Régression — vagues terminées et progression

Ces tests vérifient le JavaScript et la page réels de `index.html`. Ils n'ajoutent aucune dépendance au jeu distribué et ne demandent ni framework de build ni serveur de production.

## Commandes

Depuis la racine du dépôt, avec Node.js récent :

```sh
node tests/rewards.test.cjs
```

Cette commande utilise le module standard `node:test` et affiche les 21 cas individuels. `node --test tests/rewards.test.cjs` est également possible.

Pour les parcours navigateur, il faut Python 3, le paquet **Playwright pour Python** et un Chromium disponible dans l'environnement de test :

```sh
python -B -m unittest discover -s tests -p 'test_*.py' -v
```

Le script choisit `chromium` dans le `PATH`, ou le navigateur Chromium géré par Playwright s'il n'est pas dans le `PATH`. On peut préciser un exécutable déjà installé avec `FRIENDS_DEFENSE_CHROMIUM`. Aucune installation ni aucun téléchargement n'est effectué par les tests. Le lancement du serveur local et du navigateur peut nécessiter un environnement qui autorise ces processus ; un refus de lancement est un échec de validation à résoudre, pas un test passé.

## Couverture

- Abandon avant la première vague, pendant une vague active et après des vagues réellement terminées ; défaite en vagues 1, 2 et finale.
- Vague 1 active des terrains 2 à 7 : les vagues des terrains précédents restent acquises.
- Choix de bonus, victoire intermédiaire sans versement prématuré et victoire finale avec bonus historique ; appels de victoire incohérents sans déblocage de campagne.
- Un vrai lancement, achat légal et achèvement de vague 1 par `step()`, avec 14 éliminations, zéro fuite et 15 vies.
- Double fin de tentative et rechargements avant la fin, sur les récompenses et après l'ouverture de l'atelier.
- Sauvegarde synthétique fixe au format 38 : étoiles, paliers, record et complétion acquis conservés. Les anciennes récompenses déjà créditées ne sont pas recalculées ni retirées.
- Bouton développeur caché et inopérant en mode normal, y compris un clic programmatique ; activation uniquement avec `?dev=1`, progression et réglages de test séparés. Les sept terrains sont passés dans ce profil pour vérifier les étoiles et la complétion de test, puis le rechargement sans second paiement et le retour au profil normal.
- Sous-titre, coche de terrain et compteur de la carte courante fondés sur les vagues terminées.

`model.cjs` extrait les fonctions d'attribution et le noyau du jeu depuis le HTML. Les marqueurs doivent être uniques et les fonctions ciblées complètes ; sinon l'extraction échoue explicitement. Les tests contiennent des attentes chiffrées, pas une seconde implémentation de la formule. Les fonctions de feedback et de persistance sont neutralisées dans ce seul modèle de test. La suite navigateur utilise la page complète et les vrais gestionnaires d'interface.

`fixtures/save-v38.json` est une donnée **synthétique**, sans information de joueur. Certains parcours navigateur préparent des fins de terrain ou des états de défaite à partir de cette fixture pour tester des transitions précises ; cela ne constitue pas une campagne jouée. Chaque contexte possède son propre stockage temporaire. Le serveur est lié à `127.0.0.1` sur un port libre et s'arrête à la fin de la suite.

## Limites

La suite navigateur vérifie des parcours de progression en Chromium headless à 390 × 844 pixels CSS. Ce n'est ni une validation Safari/WebKit, ni un essai sur téléphone réel, ni une campagne complète. Le mode test sépare les sauvegardes ; il ne prétend pas empêcher un joueur de modifier son navigateur ou son stockage local.

Les autres défauts d'audit — checkpoint des cœurs, restauration pause/vitesse, validation des données corrompues, ergonomie paysage et coût graphique — sont hors du périmètre de cette correction.
