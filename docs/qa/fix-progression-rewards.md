# Correction GD-01 / QA-02 — vérification Développeur / QA

## Périmètre intégré

Le décompte retire la vague en cours ou perdue, mais conserve toutes les vagues des terrains précédemment terminés. Zéro vague terminée donne zéro étoile, y compris après une défaite. Pour une progression positive, la formule historique et le bonus de victoire de campagne sont conservés. Un appel incohérent de victoire ne débloque pas la campagne ni son bonus : le dernier terrain doit être terminé, avec des vies restantes, sans vague active et avec 70 vagues terminées.

Les étoiles, paliers permanents, records et complétions déjà enregistrés ne sont pas corrigés rétroactivement. Les clés normales `friends-defense-save-v38` et `friends-defense-settings-v15`, ainsi que le format de version 38, sont conservés.

Le raccourci développeur est caché et son gestionnaire refuse les appels en mode normal. Son activation explicite par `?dev=1` utilise `friends-defense-dev-save-v38` et `friends-defense-dev-settings-v15`, sans lecture, copie ou écriture des profils normaux. Menu, titres et route identifient ce profil de test. Les indicateurs de récompense et les coches de terrain utilisent les vagues terminées.

## Vérifications exécutées

Environnement : Node 24.22.1 ; Python 3 avec Playwright disponible ; Chromium 156.0.8078.79 headless, profils temporaires neufs, fenêtre principale 390 × 844 pixels CSS. Aucune donnée réelle de joueur n'a été utilisée.

| Commande | Résultat |
| --- | --- |
| `node tests/rewards.test.cjs` | 21 cas réussis, dont la syntaxe du script complet et un vrai achèvement de vague 1 par le noyau existant |
| `python -B -m unittest discover -s tests -p 'test_*.py' -v` | 9 tests navigateur réussis ; exécution initiale en 19,958 s |
| `python -B -m unittest discover -s tests -p 'test_*.py' -k explicit_test_profile -v` | Cas étendu du profil test réussi en 4,676 s : sept terrains passés, 36 étoiles/record 70/complétion dans la clé de test, rechargement sans second paiement et retour normal |

Les cas couvrent abandons, défaites, entrées des sept terrains, victoire intermédiaire sans paiement prématuré, victoire finale avec bonus, double fin de tentative, rechargement avant fin/sur récompenses/dans l'atelier, reçus historiques déjà payés et fin historique encore à clôturer. Une fixture synthétique fixe au format 38 vérifie la préservation des acquis. La protection du raccourci est exercée par un clic programmatique en mode normal ; le profil test est contrôlé par une trace des lectures de stockage, puis par un retour au profil normal.

Le modèle extrait les fonctions et le noyau réels du HTML, avec des limites de source uniques et des échecs explicites si ces points d'entrée changent. La suite navigateur sert la page réelle sur un serveur local temporaire. Les attentes chiffrées ne réimplémentent pas la formule. Voir [commandes, fixtures et limites](../../tests/README.md).

## Limites et éléments laissés inchangés

Les états de fin de terrain et certaines défaites sont préparés synthétiquement pour tester la transition concernée ; ce ne sont pas des campagnes jouées. La seule vague simulée intégralement dans cette suite est la première vague de la plaine, avec achats légaux. Il n'y a pas de mesure de taux de victoire, de performance ou de mémoire, ni de validation Safari/WebKit ou appareil tactile réel.

Le checkpoint des cœurs (QA-01), la restauration de pause/vitesse (QA-03), la validation des données corrompues et les refus de stockage (QA-04), le paysage et les ressources graphiques sont hors périmètre. Aucune réécriture du noyau, aucun rééquilibrage, aucun framework et aucune migration de sauvegarde ne sont introduits.
