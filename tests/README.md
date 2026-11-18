# Régression — vagues terminées et progression

Ces tests vérifient le JavaScript et la page réels de `index.html`. Ils n'ajoutent aucune dépendance au jeu distribué et ne demandent ni framework de build ni serveur de production.

## Commandes

Depuis la racine du dépôt, avec Node.js récent :

```sh
node tests/rewards.test.cjs
node tests/save-validation.test.cjs
```

Ces commandes utilisent le module standard `node:test` : 21 cas d'attribution et 15 cas de validation/stockage/reprises. `node --test tests/rewards.test.cjs tests/save-validation.test.cjs` est également possible.

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
- Checkpoint capturé avec les cœurs reportés dès le premier combat d'un terrain ; reprise du budget et de la défense antérieurs avec consommation exacte d'un cœur, sans financer la reprise par un cœur gagné pendant la vague perdue.
- Rechargement en pause aux trois vitesses ; vitesse ancienne absente normalisée à ×1 ; écrans de fin hérités rouverts sans second versement.
- Validation avant chargement et avant écriture ; rejet des corps dangereux, conservation exacte des données rejetées et verrou d'écriture en cas de lecture impossible.
- Export brut, confirmation et copie locale vérifiée avant remplacement ; récupération explicite des acquis permanents valides au format 38 quand seule la tentative est endommagée ; refus de remplacement si la copie de sécurité échoue.
- Feedback visible et export de la progression en mémoire en cas de quota ou de lecture devenue impossible ; sauvegarde primaire précédente conservée.

`model.cjs` extrait les fonctions d'attribution et le noyau du jeu depuis le HTML. Les marqueurs doivent être uniques et les fonctions ciblées complètes ; sinon l'extraction échoue explicitement. Les tests contiennent des attentes chiffrées, pas une seconde implémentation de la formule. Les fonctions de feedback et de persistance sont neutralisées dans ce seul modèle de test. La suite navigateur utilise la page complète et les vrais gestionnaires d'interface.

`fixtures/save-v38.json` est une donnée **synthétique**, sans information de joueur. Certains parcours navigateur préparent des fins de terrain ou des états de défaite à partir de cette fixture pour tester des transitions précises ; cela ne constitue pas une campagne jouée. Chaque contexte possède son propre stockage temporaire. Le serveur est lié à `127.0.0.1` sur un port libre et s'arrête à la fin de la suite.

Les fixtures compactes `save-v38-active-effects.json` et `save-v38-air-boss.json` proviennent du noyau et du sérialiseur de `main` au commit `14361f3301c4ceaa6f4d5d12e689da15b16936c5`. Cas source : `n1-p3-v5-form1-f90` et `n1-p0-v10-form2-f1200`. Les préparations des vagues 5 et 10, 5000 Z et compteurs d'éliminations historiques ont été injectés pour couvrir les structures ; les placements, évolutions, attaques et pas de temps sont exécutés par les fonctions réelles. Elles ne représentent pas des campagnes gagnées ni un budget cible. Un corpus temporaire indépendant de 1252 états a aussi été vérifié durant L1 ; les deux exemples durables permettent d'exercer effets, zones, impacts différés, volants et boss sans committer ce corpus de 9,5 Mo.

## Limites

La suite navigateur vérifie des parcours de progression en Chromium headless à 390 × 844 pixels CSS. Ce n'est ni une validation Safari/WebKit, ni un essai sur téléphone réel, ni une campagne complète. Le mode test sépare les sauvegardes ; il ne prétend pas empêcher un joueur de modifier son navigateur ou son stockage local.

L'ergonomie générale du paysage, le coût graphique, les essais sur appareil réel et les autres lots de la feuille de route restent hors du périmètre de L1. Les copies exportées dépendent du navigateur et de l'action du joueur ; le jeu exige aussi une copie locale relue à l'identique avant de remplacer une sauvegarde rejetée. Un refus de stockage peut bloquer cette récupération jusqu'à ce qu'une copie locale puisse être vérifiée ; le jeu garde alors le texte brut primaire intact.
