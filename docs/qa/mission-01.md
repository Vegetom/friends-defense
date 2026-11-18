# Mission 01 — analyse Développeur / QA

## Référence, méthode et limites

Analyse du commit `0e14138bc42eefbfcb7dcef06be3f955d328292d` de `main`, effectuée le 17 novembre 2026. Les consignes de `AGENTS.md` et `docs/COLLABORATION.md` ont été lues depuis le commit documentaire `e882b2278c9dfc99a06be89ef025743de988d81b`, encore distinct de `main` au démarrage. Aucun fichier du jeu ni aucune ressource n'a été modifié.

La lecture du code a été complétée par des essais automatisés sur le HTML réel, servi par un serveur HTTP local temporaire. Environnement : Node 24.22.1, Playwright disponible dans l'environnement, Chromium 156.0.8078.79 headless, profils de navigateur neufs et isolés, avec émulation tactile. Aucun navigateur utilisateur, téléphone réel ou sauvegarde réelle n'a été utilisé. Les profils et scripts de mesure sont temporaires et ne font pas partie du jeu livré.

Les états synthétiques ci-dessous sont explicitement distingués des actions exécutées dans l'interface. Ils permettent de vérifier une transition précise, sans prétendre avoir joué ou gagné toute une campagne. Les références de lignes sont celles du commit analysé : [index.html](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html).

## Les cinq améliorations prioritaires

| Rang / ID | Amélioration | Impact | Confiance | Effort indicatif | Dépendances |
| --- | --- | --- | --- | --- | --- |
| 1 — QA-01 | Rendre cohérents les cœurs et le checkpoint à chaque changement de terrain | Très élevé : une reprise disponible peut être refusée | Élevée, transition reproduite | Petit à moyen | Décision Game Designer sur les cœurs gagnés pendant une vague perdue |
| 2 — QA-02 | Garantir l'intégrité de la progression et isoler les raccourcis de développement | Très élevé : progression permanente sans victoire effective | Élevée, deux parcours reproduits | Moyen | Contrat de récompense du Game Designer ; explications UX |
| 3 — QA-03 | Restaurer fidèlement pause et vitesse, sans reprise surprise | Élevé : risque de pertes pendant une reprise de session | Élevée, parcours normal reproduit | Petit à moyen | Choix UX : reprise explicite ou état de pause conservé |
| 4 — QA-04 | Valider les sauvegardes et rendre visibles les échecs de stockage | Élevé : chargement bloqué ou progression non conservée | Élevée pour les défauts reproduits | Moyen | Contrat de format et messages UX ; conservation de la version 38 |
| 5 — QA-05 | Installer un socle de régression ciblé, avec parité noyau/navigateur et vérification mobile | Élevé et transversal : sécurise les futurs réglages | Élevée sur le besoin ; couverture à construire | Moyen, incrémental | Scénarios GD, parcours UX et contrats de ressources Art |

Ces efforts sont relatifs, sans estimation calendaire. Les priorités portent sur des recommandations à valider ; aucune correction n'est incluse dans cette mission.

### QA-01 — synchroniser cœurs, checkpoint et reprise

**Preuve.** `startLevel()` ligne 1003 appelle `resetGame()` avant de restaurer `g.retries=runHearts`. Or `resetGame()` ligne 745 appelle `saveBuildCheckpoint(g)` à partir de `initial()`, dont `retries` vaut zéro (ligne 552). `canRetryWave()` ligne 557 décide ensuite à partir de `buildCheckpoint.retries`, et non des cœurs affichés de `g.retries`.

**Essai exécuté.** Une sauvegarde réelle de début de jeu a été copiée dans un profil de test, puis préparée synthétiquement comme fin gagnée du premier terrain : `level=0`, `wave=10`, `life=15`, `ended=true`, `active=false`, `g.retries=2`, `runHearts=2`, sans écran atelier/récompense. Après chargement par « Continuer » et clic réel sur le bouton de terrain suivant, la sauvegarde produite par le jeu contient :

```text
level=1 ; g.retries=2 ; runHearts=2
buildCheckpoint.wave=0 ; buildCheckpoint.retries=0
```

Une copie de cet état a ensuite été préparée comme défaite de la première vague (`wave=1`, `life=0`, `ended=true`, `active=false`), sans changer le checkpoint. Au chargement réel : aucun bouton `#retryWave`, écran de récompense ouvert, `runEnded=true`, alors que `g.retries=2` figure encore dans la sauvegarde. Cette seconde étape est une injection d'état de défaite, pas une défaite obtenue en jouant la vague.

**Conséquence.** Deux cœurs reportés au terrain suivant ne protègent pas sa première vague. Le commentaire des lignes 559–560 annonce aussi l'usage possible d'un cœur gagné pendant la vague perdue, alors que l'éligibilité dépend du checkpoint antérieur : cette intention doit être clarifiée, plutôt que déduite du seul commentaire.

**Recommandation.** Construire le checkpoint seulement après restauration complète du nouvel état de terrain. Définir une seule règle pour la disponibilité et la consommation des cœurs ; le HUD, `canRetryWave()` et `retryWave()` doivent la partager. Conserver l'annulation des achats et gains de la vague échouée, sans création de cœurs par répétition.

**Acceptation proposée.** Tester les transitions des sept terrains avec 0, 1 et 2 cœurs. Une défaite en première vague permet exactement le nombre de reprises annoncé ; chaque reprise consomme un cœur et restaure le budget/checkpoint prévu. Tester séparément un cœur gagné dans la vague perdue selon la règle retenue. Sauvegarder puis recharger chaque cas doit préserver le résultat.

### QA-02 — protéger la validité de la progression

**Preuves et essais exécutés.**

1. `globalWaveCleared()` ligne 896 compte la vague active comme franchie tant qu'il ne s'agit pas d'une défaite avec zéro vie. `mapsButton` ligne 1013 mène à `finishRun(false,true)`, puis à `rewardStars()` ligne 897. Dans une sauvegarde de test dérivée du jeu, préparée avec `wave=1`, `active=true`, 15 vies, zéro élimination, zéro étoile et aucun record, les clics réels « Continuer » puis « Quitter » ont donné **6 étoiles**, `bestWave=1` et `totalKills=0`. La présence d'un état de vague active était synthétique ; le calcul de récompense et le parcours d'abandon étaient ceux du jeu réel.
2. Le bouton « Mode dev » est présent dans le HTML ligne 433 et son gestionnaire lignes 1014–1023 n'exige pas un mode de développement dédié. Dans un profil neuf, parcours réel « Nouvelle partie » → « Commencer » → « Mode dev » : `wave=10`, `ended=true` et bouton « Niveau 2 » visible, sans combat gagné.

**Conséquence.** Les mesures de progression et de difficulté peuvent être contournées. Modifier seulement les PV ou prix avant de régler ces entrées fausserait l'évaluation de l'économie roguelite. Ce constat rejoint l'analyse Game Designer ; il ne justifie pas de supprimer arbitrairement toute récompense de défaite.

**Recommandation.** Définir explicitement les vagues réellement terminées et le contrat de récompense pour victoire, défaite et abandon. Tester le versement unique lors des rechargements et des doubles actions. Séparer le raccourci développeur du parcours distribué ; le conserver dans un outil de test isolé est utile pour reproduire les fins de terrain.

**Acceptation proposée.** Le Game Designer fixe l'attribution attendue lorsqu'aucune vague n'est franchie. Le compteur de vagues terminées, le record et le versement suivent ce contrat, même après rechargement. Un raccourci de test n'accorde aucune progression dans le mode normal. Les états de fin de tentative et de récompense sont idempotents : les invoquer à nouveau ne crédite pas une seconde fois la même tentative.

### QA-03 — restaurer la pause et la vitesse sans surprise

**Preuve.** `buildSaveData()` ligne 440 conserve `paused` mais omet `speed`. `applyLoadedSave()` ligne 449 lit pourtant `data.speed`, puis finit par `paused=!!data.paused&&g.active!==true` dans le parcours de combat ordinaire : une vague active sauvée en pause est donc réactivée.

**Essai exécuté sans injection d'état.** Profil neuf → Nouvelle partie → Commencer → lancer vague 1 → Pause → deux clics sur vitesse pour afficher `×3`. Avant rechargement : sauvegarde `paused=true`, `g.active=true`, absence de propriété `speed`. Recharger la page puis cliquer sur « Continuer » donne un bouton pause avec `aria-pressed="false"` et une vitesse `×1`, sans exception JavaScript.

**Conséquence.** Le joueur retrouve un combat en mouvement alors qu'il l'avait volontairement arrêté, et la vitesse ne correspond plus à son dernier choix. Sur mobile, une reprise après interruption est précisément un moment où il peut ne pas être prêt à agir.

**Recommandation.** Rendre explicite le contrat de reprise : conserver la pause sauvée ou afficher une reprise de combat nécessitant une action. Sauvegarder les paramètres nécessaires, avec défauts compatibles pour les sauvegardes 38 qui n'ont pas `speed`. Examiner aussi le passage en arrière-plan ; aucune règle de pause automatique n'est imposée sans décision UX.

**Acceptation proposée.** Un aller-retour sauvegarde/rechargement à `×1`, `×2` et `×3`, en pause et en combat, reproduit le contrat retenu. Aucun ennemi n'avance pendant un état annoncé en pause. Les sauvegardes actuelles dépourvues de `speed` restent chargeables et reçoivent un défaut documenté. Inclure l'interruption puis le retour d'onglet dans la validation mobile.

### QA-04 — valider avant chargement et annoncer un stockage impossible

**Preuve.** `readSaveData()` ligne 441 ne vérifie que la version, la présence d'un tableau `metaLevels` et un `g` non vide au sens booléen. `applyLoadedSave()` ligne 449 suppose ensuite un état exploitable par le chemin, le rendu et l'interface. `saveProgress()` ligne 443 absorbe toute exception de `localStorage.setItem()` sans retour joueur.

**Essais exécutés.**

- Dans un profil synthétique, le JSON `{ "version":38, "metaLevels":[0,0,0,0,0], "g":{} }` rend « Continuer » actif. Le clic produit les exceptions `Cannot read properties of undefined (reading '41')` puis `Cannot convert undefined or null to object` ; le menu reste visible. Il s'agit d'une corruption structurelle volontaire, pas d'une preuve que les sauvegardes normales sont systématiquement corrompues.
- Une exception `QuotaExceededError` a été injectée uniquement pour l'écriture de la clé `friends-defense-save-v38`, via un remplacement de `Storage.prototype.setItem()` dans un autre profil de test. Nouvelle partie, lancement et pause continuent sans exception non gérée, mais la clé n'est pas stockée et aucun avertissement n'est affiché. Ce test simule un refus de stockage, sans prétendre mesurer le quota réel d'un téléphone.

**Recommandation.** Valider les champs indispensables et leurs bornes avant de modifier l'état courant. Garder une copie récupérable des données rejetées ; proposer un message clair et une issue de récupération. Faire remonter un statut de sauvegarde, notamment en cas de stockage indisponible. Préserver la clé `friends-defense-save-v38`, le format 38 et les réglages `friends-defense-settings-v15` dans les tâches qui ne demandent pas de migration.

**Acceptation proposée.** Tester données absentes, JSON invalide, version inconnue, structure incomplète, indices hors limites et sauvegarde normale. Une donnée invalide ne lance pas un chargement partiel, ne bloque pas l'interface et n'est pas écrasée silencieusement. Un refus d'écriture est annoncé au joueur sans arrêter le combat. Toute migration future dispose de fixtures anciennes et d'un résultat idempotent ; aucune migration n'est proposée dans cette PR d'analyse.

### QA-05 — construire une régression ciblée avant les changements de fond

**Constats vérifiés.** La référence `main` ne contient que `index.html`. La vérification `node --check` du JavaScript extrait en mémoire réussit ; les défauts comportementaux ci-dessus existent donc malgré une syntaxe valide. Trois démarrages réels ont été exécutés sans exception JavaScript à 320 × 568, 390 × 844 et 844 × 390 pixels CSS. Cela valide uniquement le démarrage observé, pas la compatibilité mobile complète. En paysage, après les clics, `#fd15` mesure 720 × 540 dans une fenêtre 844 × 390 : l'adaptation et le défilement doivent être vérifiés avec l'UX Designer, qui mène son audit propre.

**Recommandation.** Ajouter progressivement un harnais de tests autour des fonctions existantes, sans conditionner les premières mesures à une réécriture du jeu. Les extractions doivent lire la logique réelle et échouer clairement si leurs points d'entrée changent. Comparer quelques traces d'états noyau/navigateur avant d'utiliser un simulateur pour décider l'équilibrage. La séparation ultérieure des responsabilités peut faciliter la maintenance, à condition de préserver l'artefact autonome et les sauvegardes ; un changement de framework n'est pas nécessaire à ce stade.

**Premiers invariants utiles.** Chemin toujours accessible après achat légal ; argent conservé par achat/remboursement ; non-cumul indu des effets ; compteur de vagues terminé cohérent ; versement unique des étoiles ; cœurs/checkpoints cohérents ; pause et état conservés au rechargement. Reproduire les cinq défauts ci-dessus comme cas de régression, puis ajouter les situations touchées par chaque future PR.

**Acceptation proposée.** Une commande documentée exécute les invariants et quelques scénarios déterministes, en affichant commit et paramètres. Un test négatif prouve que le harnais détecte une divergence. Les scénarios GD utilisent la même logique et leurs limites sont déclarées ; une simulation de vague 1 ne vaut pas validation des 70 vagues. Les parcours mobiles essentiels sont vérifiés dans Chromium et WebKit/Safari selon disponibilité, puis sur un appareil tactile réel avant une déclaration de compatibilité complète. Couvrir le paysage, les annulations de pointeur, l'audio après interaction, les images, les dialogues et les interruptions. Mesurer fluidité et mémoire sur une référence commune avant d'annoncer une amélioration de performance.

## Bilan des vérifications réellement exécutées

| Vérification | Résultat observé | Portée |
| --- | --- | --- |
| Syntaxe JavaScript extrait du HTML, Node 24.22.1 | Réussite, code de sortie 0 | Syntaxe seulement |
| Rechargement d'un combat en pause et vitesse ×3 | Reprise sans pause, vitesse ×1 | Parcours réel, 390 × 844 |
| Passage de terrain avec deux cœurs | Checkpoint à zéro malgré deux cœurs actifs | Fin de terrain synthétique, transition réelle |
| Chargement de défaite vague 1 du terrain suivant | Pas de reprise proposée, tentative terminée | Défaite synthétique dérivée de la transition précédente |
| Chargement d'une sauvegarde structurellement invalide | Continuer actif puis deux exceptions JavaScript | Corruption synthétique volontaire |
| Abandon pendant première vague, zéro élimination | 6 étoiles, record vague 1 | État actif synthétique, abandon réel |
| Bouton développeur depuis début normal | Terrain déclaré gagné sans combat | Parcours réel |
| Refus d'écriture de sauvegarde | Jeu actif, aucune sauvegarde ni alerte visible | `QuotaExceededError` injectée |
| Trois tailles de fenêtre en Chromium | Démarrage sans exception ; paysage à examiner | Émulation, pas appareils réels |

Non exécutés : campagne complète jouée, matrice des 70 vagues, WebKit/Safari, appareils réels, coupure brutale du processus pendant une écriture, benchmark de fluidité ou mémoire, contrôle exhaustif des animations. Ces éléments restent dans le plan de validation et ne sont pas des résultats de cette mission.
