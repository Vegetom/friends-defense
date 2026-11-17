# Mission 01 — synthèse et feuille de route proposée

## Décision proposée

**Sécuriser la progression et les reprises avant de recalibrer la difficulté ; rendre les parcours mobiles utilisables ; construire les mesures qui permettront ensuite de régler les sept terrains.** Les cinq héros et leur style actuel sont à préserver. Une refonte graphique ou technique générale n'est pas justifiée par cette première mission.

Cette PR contient une analyse, pas une implémentation. Les vingt recommandations et les arbitrages ci-dessous sont soumis à validation de l'utilisateur. Aucune mécanique, ressource ou sauvegarde du joueur n'a été modifiée ; `index.html` reste identique à la référence de départ.

## Référence et collaboration effectuée

- **Code analysé :** dernière version de `main` récupérée au démarrage, commit [`0e14138bc42eefbfcb7dcef06be3f955d328292d`](https://github.com/Vegetom/friends-defense/tree/0e14138bc42eefbfcb7dcef06be3f955d328292d).
- **Consignes :** `AGENTS.md` et `docs/COLLABORATION.md` lus au commit `e882b2278c9dfc99a06be89ef025743de988d81b` de la [PR nº 1](https://github.com/Vegetom/friends-defense/pull/1), encore distincte de `main` au début de la mission. Cette PR d'audit part directement de `main` et ne fusionne pas cette PR d'organisation.
- **Organisation réelle :** quatre agents spécialisés ont travaillé en parallèle, avec des fichiers réservés. Le chef de projet a cadré la mission, transmis les constats partagés, relu les quatre analyses et consolidé les priorités. Il est seul à effectuer les opérations Git.
- **Traçabilité :** [fiche de mission, périmètre et réservations](../tasks/mission-01.md).

| Expertise | Rapport détaillé | Résultat |
| --- | --- | --- |
| Game Designer | [Difficulté, économies et simulation](../design/mission-01.md) | Cinq recommandations GD-01 à GD-05 ; tableaux des sept terrains ; trois simulations de faisabilité |
| UX/UI Designer | [Parcours, tactile et accessibilité](../ux/mission-01.md) | Cinq recommandations UX-01 à UX-05 ; mesures de trois formats en Chromium |
| Pixel Artist | [Identités, ressources et animations](../art/mission-01.md) | Cinq recommandations ART-01 à ART-05 ; inspection visuelle des sources et inventaire des ressources |
| Développeur / QA | [Progression, sauvegardes et vérifications](../qa/mission-01.md) | Cinq recommandations QA-01 à QA-05 ; reproductions ciblées sur profils synthétiques isolés |

## Ce qui est établi et ce qui reste à mesurer

| Constat | Preuve disponible | Conséquence et limite |
| --- | --- | --- |
| Abandonner la vague 1 juste lancée peut donner 6 étoiles, puis 5 aux répétitions | Fonctions réelles extraites par GD ; abandon confirmé en navigateur par QA sur un état actif synthétique | Le compteur crédite une vague non terminée. Les 205 étoiles de tous les paliers sont atteignables en 41 abandons, soit 206 étoiles. Aucun temps réel de répétition n'a été mesuré. |
| Le bouton « Mode dev » est accessible dans le parcours normal et déclare le terrain gagné | Clic réel de QA depuis un profil neuf ; bouton également observé par UX | Les victoires et récompenses normales peuvent être obtenues par un raccourci de test. Il faut isoler le parcours distribué, sans prétendre empêcher toute modification locale par un joueur. |
| Deux cœurs reportés peuvent ne pas permettre de reprendre la première vague du terrain suivant | Fin de terrain synthétique, clic réel vers le terrain suivant, puis défaite synthétique ; checkpoint observé à zéro malgré deux cœurs actifs | Défaut de transition établi, pas une défaite obtenue en jouant une campagne. Le checkpoint est créé avant restauration des cœurs. |
| Un combat sauvegardé en pause à ×3 reprend sans pause à ×1 | Parcours réel de QA, sans injection d'état | Le retour de session ne respecte pas les choix du joueur. Les autres états de sauvegarde restent à couvrir. |
| Un état de sauvegarde incomplet peut activer Continuer puis produire des erreurs ; un stockage refusé n'est pas signalé | JSON structurellement invalide et `QuotaExceededError` injectés dans des profils séparés | Fragilité de récupération et de feedback ; aucune corruption spontanée ni saturation réelle de téléphone n'est démontrée. |
| Le paysage 844 × 390 dépasse en hauteur et certaines commandes sont petites | Mesures DOM de UX, recoupement QA : document de 540 px, autoscroll de 150 px ; fermeture de fiche 24 × 24 px | Défauts de disposition et dimensions établis. La précision d'un doigt humain et Safari restent à tester. |
| La transition vers le Bastion cumule plusieurs hausses de pression | Calcul des vraies fonctions : PV normal V1 ×2,23 ; route nue 14 → 10 cases ; boucliers ; enveloppe Z théorique +10,1 % | Risque fort de rupture, pas preuve d'impossibilité. L'enveloppe inclut la prime finale, qui ne finance pas le combat final ; les tours et Z ne sont pas reportés entre terrains. |
| Les images dominent le fichier et plusieurs signaux graphiques peuvent se concurrencer | Inspection réelle et mesures ART : 52 data URI d'images, 98,3 % du HTML ; ordre des couches étudié | La surface RGBA théorique de `GRAPHICS` est de 22,8 Mio ; ce n'est ni la mémoire navigateur mesurée ni un benchmark de fluidité. La gêne en combat dense est à observer. |

Les preuves détaillées, fonctions et liens vers les lignes du commit se trouvent dans les rapports spécialisés. Les défauts reproduits ne prouvent pas une panne générale du jeu ; les hypothèses de plaisir, de compréhension et de performance restent des hypothèses.

### La simulation automatique est faisable, sa couverture reste initiale

Le Game Designer a exécuté trois simulations déterministes de la **première vague de la plaine** avec le noyau réel, un pas de `1/60 s` et le même achat légal : Tom aux cases 31 et 33, Raphaël à la case 35, pour 135 Z sur 150.

| Profil de paliers permanents | Temps de jeu simulé | Résultat |
| --- | --- | --- |
| Aucun palier | 13,933 s | 14 éliminations, aucune fuite, 15 vies, 97 Z |
| Tom I et Raphaël I | 9,867 s | Identique sur éliminations, vies et Z |
| Tous les héros au maximum | 9,150 s | Identique sur éliminations, vies et Z |

Le script reproductible figure dans le rapport GD. Ces trois scénarios ne sont pas un taux de victoire, ne couvrent pas les 70 vagues et ne démontrent pas l'équilibre des cinq héros. Ils permettent de démarrer un banc de mesure sans réécrire les règles.

## Traçabilité des vingt recommandations

Chaque spécialiste a classé ses cinq propositions selon son angle. La consolidation les regroupe par dépendance ; elle ne prétend pas que les rangs de métiers différents constituent un score comparable. Les lots L1 à L7 sont détaillés ensuite.

| ID | Recommandation du spécialiste | Lot proposé |
| --- | --- | --- |
| GD-01 | Récompenser la progression réellement accomplie et isoler les outils de développement | L1 |
| GD-02 | Mesurer la courbe des sept terrains, avec priorité au Bastion | L5, après L1 et L4 |
| GD-03 | Construire un banc de simulation utilisant la logique réelle | L4 |
| GD-04 | Aligner calendrier, promesses et effets des bonus | L3 |
| GD-05 | Mesurer le rythme permanent et les spécialisations à coût comparable | L5 |
| UX-01 | Adapter les faibles hauteurs et le paysage | L2 |
| UX-02 | Fiabiliser commandes et placement au doigt | L2 |
| UX-03 | Distinguer tentative et effacement du profil | L1 |
| UX-04 | Faire correspondre textes et annonces aux règles | L3 |
| UX-05 | Rendre dialogues et plateau accessibles autrement qu'au pointeur | L2, en étapes |
| ART-01 | Réduire le coût des ressources après établissement d'une référence | L7 ; mesures possibles en parallèle |
| ART-02 | Préserver ennemis, santé et états face aux effets | L6 ; scènes de lisibilité préparées avec L2 |
| ART-03 | Distinguer niveaux de combat et paliers permanents | L3 |
| ART-04 | Stabiliser cadrage, échelle et marges des animations | L6 |
| ART-05 | Raccorder pose, direction et feedback au tir réel | L6 |
| QA-01 | Synchroniser cœurs, checkpoint et reprise | L1 |
| QA-02 | Protéger la validité de la progression | L1 |
| QA-03 | Restaurer pause et vitesse sans surprise | L1 |
| QA-04 | Valider les sauvegardes et annoncer les échecs de stockage | L1 |
| QA-05 | Installer une régression ciblée et une parité noyau/navigateur | L4 ; contrôles associés à chaque lot |

## Contradictions, tensions et arbitrages proposés

Aucune contradiction factuelle n'a été démontrée entre les quatre rapports. Ils convergent sur la référence du code et sur les défauts recoupés. Les tensions portent sur les priorités, le périmètre ou les moyens ; les arbitrages suivants restent des propositions.

| Tension | Origine | Arbitrage proposé et décision restante |
| --- | --- | --- |
| Récompenser l'échec pour soutenir la boucle roguelite, tout en évitant que l'abandon immédiat remplace le jeu | GD-01, GD-05, QA-02 | Compter uniquement les vagues réellement terminées pour le record. Valider séparément une éventuelle compensation sans vague terminée, son effort requis et ses limites. Ne pas supprimer par défaut toute récompense de défaite. |
| Corriger un texte trompeur ou modifier la mécanique pour tenir sa promesse | GD-04, UX-04 | Commencer par présenter les règles réelles : bonus après 3/6/9, revenus temporaires sur 4–6 et 7–9, boosts limités au terrain. Le cas de la cible voisine de Jordan doit être tranché explicitement : corriger la promesse ou modifier l'effet dans une autre PR d'équilibrage. |
| Rendre une évolution spectaculaire sans cacher le plateau ni confondre les deux progressions | ART-02 à ART-05, UX-02/04 | Préserver les cinq portraits et identités ; distinguer niveau de tour et palier permanent par des indicateurs réutilisables. Ne pas agrandir encore les sprites ou multiplier les portraits avant essai de lisibilité et budget. |
| Donner plus d'espace tactile alors que le plateau et les informations manquent déjà de place | UX-01/02/05, ART-04 | Concevoir une disposition de faible hauteur avant de grossir indistinctement les contrôles. Viser 44 px minimum pour les commandes ; prototyper précision et annulation du plateau plutôt qu'imposer 44 px à chaque case. Valider loupe ou confirmation optionnelle par essai humain. |
| Extraire un noyau testable sans retarder les corrections par une refonte du monofichier | GD-03, QA-05 | Utiliser d'abord des sondes lisant la logique existante, puis une interface de test incrémentale avec traces comparées au navigateur. La séparation de fichiers, un framework ou un backend ne sont pas des prérequis. |
| La priorité ART met le poids des images en premier, alors que UX et QA ont des défauts reproduits de parcours | ART-01, UX-01, QA-01 à QA-04 | Mesurer le démarrage et les ressources tôt en parallèle ; prioriser l'implémentation des défauts établis. Optimiser ensuite avec une comparaison visuelle et un budget mesuré, sans gain de performance inventé. |
| Respecter une sauvegarde tout en évitant une reprise de combat surprenante | QA-03, UX-03 | Garantir une reprise contrôlée. Choisir entre conservation exacte de la pause et écran de reprise explicite ; conserver les sauvegardes 38 et un défaut documenté pour les anciennes données sans vitesse. |

Les critères de Game Designer sur la difficulté ne peuvent pas être remplacés par les seules mesures de DPS ; les simulations ne peuvent pas remplacer les essais de compréhension ou de plaisir. Réciproquement, un retour de ressenti ne suffit pas à diagnostiquer une rupture mathématique.

## Feuille de route priorisée

**P0** désigne une précondition à une évaluation fiable de la progression, pas une déclaration d'incident de production. **P1** désigne le prochain ensemble d'améliorations fonctionnelles ou de mesure. **P2** désigne les interventions qui gagnent à attendre ces contrats et références. Effort : S local, M plusieurs parcours, L conception et campagne de validation ; aucun délai calendaire n'est engagé.

| Lot | Priorité / effort | Responsable et contributeurs | Contenu et dépendances | Critère de sortie |
| --- | --- | --- | --- | --- |
| **L1 — Progression fiable** | P0 / M | Développeur/QA ; GD et UX | Récompenses et raccourcis de test, cœurs/checkpoints, reprise pause/vitesse, validation/feedback des sauvegardes, distinction nouveau profil/nouvelle tentative. Définir d'abord les contrats de récompense et de reprise. | Reproductions QA transformées en régressions utiles ; records sur vagues terminées ; cœurs cohérents sur transitions ; sauvegardes 38 conservées ; aucune perte silencieuse ni reprise surprise selon le contrat retenu. |
| **L2 — Mobile et accès aux actions** | P1 / M–L | UX ; Développeur/QA et Art | Faibles hauteurs/paysage, commandes tactiles, précision du placement et dialogues. Conception indépendante de L1 ; intégration séquentielle dans le monofichier. Traiter le focus des dialogues, puis le prototype d'accès alternatif au plateau. | Parcours essentiels complets aux trois formats ; pas d'autoscroll involontaire ; commandes mesurées, annulations sans dépense ; focus contenu/restauré ; prototype plateau validé au clavier et au lecteur d'écran selon le plan UX. |
| **L3 — Contrat des règles et signaux** | P1 / S–M | GD et UX ; Art, Développeur/QA | Bonus affichés depuis les mêmes données que leur application ; portée d'un boost de terrain ; distinction tour I–III/palier permanent 0–3. Dépend des décisions de L1 sur les récompenses ; les autres textes peuvent avancer en parallèle. | Aucune promesse de vague inexistante ; trois versements réels pour chaque bonus économique ; grille des cinq héros et de leurs deux axes de progression compréhensible ; pas de buff implicite dans une correction rédactionnelle. |
| **L4 — Mesures et régression** | P1 / M, incrémental | GD et Développeur/QA | Scénarios déterministes, achats légaux, invariants, traces noyau/navigateur, variations du pas de temps et profils de progression. Peut commencer dès validation ; les mesures destinées au réglage utilisent les contrats corrigés de L1/L3. | Une commande reproductible, un test négatif qui détecte une divergence, quelques traces comparées au navigateur ; extension explicitement suivie vers les 70 vagues, hardcore et interruptions de session. |
| **L5 — Calibration de campagne et du rythme permanent** | P1 / L, après L1 et L4 | GD ; UX et Développeur/QA | Mesurer Bastion puis toutes les transitions, comparer compositions et portefeuilles d'étoiles à coût égal, séparer carte/PV/cadence/budget. Fixer avec l'utilisateur tension et rythme cible avant de modifier des valeurs. | Résultats avant/après sur sept terrains, plusieurs profils et stratégies ; causes de défaite tracées ; tests humains distincts ; valeurs candidates présentées et validées avant leur intégration. |
| **L6 — Lecture graphique et feedback** | P2 / M | Pixel Artist ; UX, GD et Développeur/QA | Santé/états au-dessus des effets décoratifs, cadrages/ancrages, direction et moment du tir. Préparer les scènes de contrôle avec L2 ; appliquer les contrats de signaux de L3 et un budget de ressources partagé avec L7. | Comparaison des scènes denses, cinq héros et quinze formes ; marges vérifiées sur les trente feuilles ; lecture sans son/couleur seule ; dégâts, cadence, portée et ciblage inchangés. |
| **L7 — Ressources adaptées au mobile** | P2 / M | Pixel Artist et Développeur/QA ; UX | Établir une référence de démarrage, de tailles d'affichage et de mémoire dès que possible, puis comparer exports et chargement. Pas de CDN ni nouvelle chaîne de compilation par défaut. Éviter une production de variantes avant ce budget. | Inventaire avant/après, rendu aux densités visées, démarrage comparé dans le même environnement, toutes les formes disponibles et repli sans image manquante ; absence de régression visuelle ou de sauvegarde. |

L5 dépend de **contrats fiables et d'un banc validé**, pas nécessairement de la fin de toute l'accessibilité ou de toutes les retouches artistiques. Les identifiants de lots n'imposent pas un ordre strict entre travaux indépendants. Une revue par domaine précède chaque intégration ; les modifications de `index.html` restent successives sous la responsabilité du Développeur/QA, même si analyses, prototypes et ressources sont préparés en parallèle.

### Parallélisme proposé pour la suite, après validation

1. **En parallèle :** GD/QA écrivent les contrats et cas de L1/L4 ; UX conçoit les vues et gestes de L2 ; Art prépare les scènes de lisibilité et le manifeste/budget de L6/L7.
2. **Intégration successive :** petites PR cohérentes pour les reprises/sauvegardes, l'intégrité des récompenses, les textes et les parcours mobiles, chacune avec sa régression. Aucune de ces PR n'est créée ni appliquée par cette mission d'analyse.
3. **Après comparaison des traces :** GD étend les scénarios de L4 et propose des réglages de L5 ; UX mesure leur compréhension ; Art ajuste les signaux selon les contrats établis.
4. **Avant une déclaration de compatibilité :** QA complète WebKit/Safari, appareil tactile réel, interruptions, scènes chargées et lecteurs d'écran avec UX. Les outils actuellement disponibles ont permis Chromium et des calculs, pas ces validations finales.

## Choix à valider avant implémentation

- Adopter l'ordre de dépendance proposé, en commençant par la fiabilité de progression et des reprises.
- Définir le devenir d'une tentative sans vague terminée, les cœurs gagnés dans une vague perdue et le contrat de reprise après interruption. La mission ne décide pas de supprimer une compensation de défaite ni de changer le format 38.
- Privilégier d'abord la cohérence des textes avec les effets actuels ; traiter tout changement de pouvoir ou de calendrier comme une décision d'équilibrage séparée.
- Fixer les objectifs de difficulté et de rythme permanent à partir du banc de mesure et de retours humains ; aucun prix, PV ou taux de victoire cible n'est approuvé dans ce rapport.
- Conserver les cinq identités et le style chibi anime ; améliorer d'abord la lisibilité et les ressources plutôt que lancer une refonte graphique.

## Vérification et limites de cette livraison

Les spécialistes ont réellement effectué les lectures, calculs, inspections et essais décrits dans leurs rapports. Le coordinateur vérifie les liens, le périmètre du diff, l'identité de `index.html`, les cinq recommandations par rôle et la reproductibilité du script GD. Les résultats de ces contrôles sont consignés dans la fiche de mission et la description de PR.

Non réalisés : campagne complète simulée ou jouée, étude de taux de victoire, panel de joueurs, Safari/WebKit, appareil mobile réel, lecteur d'écran et benchmark de performance/mémoire. Ces absences sont des éléments du plan futur ; elles ne sont pas présentées comme des validations acquises. Aucune recommandation n'est implémentée par cette PR, qui reste ouverte pour revue sans fusion automatique.
