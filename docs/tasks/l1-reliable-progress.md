# L1 — terminer la progression fiable

## Mission et référence

Terminer les problèmes restants de L1 de la mission 01 : cœurs et checkpoints entre terrains, pause/vitesse au rechargement, validation et récupération des sauvegardes endommagées, protection des acquis v38. Le correctif GD-01 / QA-02 déjà livré reste une régression à couvrir.

- Base : `main`, commit `14361f3301c4ceaa6f4d5d12e689da15b16936c5`.
- Branche : `fix/l1-reliable-progress`.
- Consignes : `AGENTS.md`, `docs/COLLABORATION.md`, `docs/reports/mission-01-roadmap.md`.
- Livraison autorisée : branche, PR, fusion et GitHub Pages après réussite des contrôles ; arrêt de la publication en cas de régression ou risque de perte de progression.
- Hors périmètre : équilibrage, nouveaux graphismes, refonte mobile L2 et calibration de campagne. Les cinq héros et les données de combat restent conservés.

## Collaboration et réservations

Les quatre spécialistes ont été lancés en parallèle. Le coordinateur réserve les opérations Git et ce document ; le Développeur / QA est seul à intégrer `index.html`.

| Rôle | Fichiers réservés | Travail |
| --- | --- | --- |
| Game Designer | `docs/design/l1-reliable-progress.md` | Règles des cœurs, checkpoints, reprises, pause et compatibilité des états hérités |
| Développeur / QA | `index.html`, tests Node/validation et helpers existants, `tests/README.md`, `docs/qa/l1-reliable-progress.md` | Implémentation, validation pure, compatibilité v38 et régressions |
| UX/UI Designer | `docs/ux/l1-reliable-progress.md`, `tests/test_l1_browser.py` | Messages, récupération et tests navigateur des nouveaux parcours |
| Pixel Artist | `docs/art/l1-reliable-progress.md` | Conservation des ressources et lecture du feedback sur petit écran, sans création graphique |
| Coordinateur | Ce document | Contrats, revue indépendante, contrôles intégrés et livraison automatisée |

## Contrats partagés

1. Les cœurs disponibles au checkpoint financent la reprise. Les gains d'une vague perdue sont annulés avec cette vague ; le commentaire historique contradictoire est corrigé sans modifier les valeurs d'équilibrage.
2. À l'entrée du terrain suivant, restaurer les cœurs avant de capturer le checkpoint. Réparer seulement les anciens états dont l'origine des cœurs reportés est déterminable, sans réouvrir une tentative déjà récompensée ni inventer un budget.
3. Sauvegarder la vitesse parmi ×1, ×2 et ×3 ; accepter les sauvegardes v38 sans ce champ avec un défaut ×1. Conserver une pause sauvegardée pendant un combat et les écrans qui imposent une pause.
4. Valider les données avant de remplacer l'état courant. Conserver les étoiles, paliers, record, complétion et données de tentative valides ; ne pas imposer rétroactivement une cohérence idéale qui rejetterait des acquis hérités.
5. Les données invalides, versions inconnues et données illisibles ne doivent pas être écrasées automatiquement. Récupération ou remplacement explicites, avec conservation/export de l'original ; un refus de stockage est annoncé sans prétendre avoir sauvegardé.
6. Distinguer les actions de reprise, nouvelle tentative et remise à zéro du profil. Les essais utilisent uniquement des fixtures et contextes isolés ; aucune sauvegarde réelle du joueur n'est effacée.
7. Conserver les clés normales v38, le format et l'URL du jeu ; maintenir l'isolation du profil développeur et les garanties de récompense de la PR nº 3.

## Critères de validation

- Matrice des transitions/reprises avec 0, 1 et 2 cœurs, sauvegarde puis rechargement ; consommation exacte, restauration du checkpoint et absence de duplication des gains.
- Pause et vitesse pour les états actifs, en préparation, dans les bonus, l'atelier et les récompenses ; défauts compatibles sur les anciens formats v38.
- Sauvegardes valides représentatives, données absentes, JSON endommagé, version inconnue, structure invalide, champs facultatifs anciens et stockage refusé ou inaccessible.
- Intégrité de l'original rejeté et de la copie de récupération ; aucun écrasement automatique en cas d'erreur ; messages visibles et action d'annulation effective.
- Réexécution des tests Node et Chromium existants, nouveaux tests ciblés et contrôle des ressources/valeurs de combat.
- Après validation : PR vers le dernier `main`, fusion du SHA testé, déploiement Pages du même code, chargement public et reprise de fixture v38 en profil isolé.

## État et résultats

Implémentation terminée et validation intégrée réussie sur le snapshot SHA-256 `54ce720068aa15466477df98fbe070329dd8257a4d1f2310def783c03df70edd`. La livraison automatique suit ces contrôles ; le résultat Pages est consigné dans la PR de livraison.

| Contrôle final | Résultat |
| --- | --- |
| `node tests/rewards.test.cjs` | 21 cas réussis, non-régression du correctif précédent |
| `node tests/save-validation.test.cjs` | 15 cas réussis, dont compteurs actifs obligatoires et protection des écritures |
| `python -B -m unittest discover -s tests -p 'test_*.py' -v` | 25 tests réussis en 62,504 s, dont transition avec deux cœurs, rechargement puis consommation 2 → 1 → 0 |
| Corpus indépendant de l'ancien noyau | 1252 états v38 acceptés, zéro rejet ; acquis et champs de tentative contrôlés inchangés ; 48 checkpoints hérités réparés |
| Périmètre | 52 images et 15 SVG inchangés ; données et fonctions de combat inchangées ; CSS ajouté uniquement pour sauvegarde/récupération |
| Revue graphique | Douze états à 320 et 390 px sans erreur de page ni débordement horizontal ; nouvelles commandes de 44 px minimum |

La première découverte intégrée avait révélé une fixture contradictoire : un reçu de vague 1 contenait encore un checkpoint de vague 2. Elle a été corrigée vers un checkpoint de vague 0, sans retirer les assertions sur les acquis ni relâcher le validateur. La publication est restée arrêtée durant cette vérification. La revue a aussi ajouté le rejet d'un combat actif privé de ses compteurs, pour empêcher une validation de vague artificielle. Les suites complètes ont ensuite été réexécutées avec succès.

Rapports : [Game Designer](../design/l1-reliable-progress.md), [UX](../ux/l1-reliable-progress.md), [Pixel Artist](../art/l1-reliable-progress.md), [Développeur / QA](../qa/l1-reliable-progress.md). Commandes et fixtures : [tests/README.md](../../tests/README.md).

Limites : profils synthétiques et Chromium headless, pas Safari/WebKit ni appareil physique. Le message d'erreur réduit la place du plateau sur petit écran mais ne recouvre pas les commandes ; l'ergonomie générale reste au lot L2. Le remplacement de données rejetées reste bloqué si leur copie locale ne peut pas être vérifiée. Aucun historique réel de joueur n'a été effacé.
