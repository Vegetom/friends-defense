# Mission 01 — analyse UX/UI

## Référence et portée

- Code étudié : `main`, commit [`0e14138bc42eefbfcb7dcef06be3f955d328292d`](https://github.com/Vegetom/friends-defense/tree/0e14138bc42eefbfcb7dcef06be3f955d328292d).
- Consignes lues : `AGENTS.md` et `docs/COLLABORATION.md` du commit `e882b2278c9dfc99a06be89ef025743de988d81b`, encore dans la PR d'organisation au début de la mission.
- Livrable : recommandations uniquement ; aucune modification du jeu, de ses ressources ou de ses sauvegardes réelles.
- Classement : priorité à l'accès aux actions essentielles et à la protection de la progression, puis à la compréhension et aux alternatives d'accès. Les efforts indiqués sont relatifs : S = local, M = plusieurs composants, L = interaction à concevoir et valider ; ce ne sont pas des engagements calendaires.

## Méthode et observations effectivement exécutées

Analyse des parcours et du code, puis mesures DOM dans **Chromium 156.0.8078.79 headless**, piloté par Playwright Python, avec un contexte neuf par viewport : `is_mobile=True`, `has_touch=True`, facteur de pixels `1`. La page exacte du dépôt a été servie en HTTP local sur le port `8101` ; aucun contenu du jeu n'a été réécrit ou instrumenté. Mesures après chargement puis parcours **Nouvelle partie → atelier → Commencer → achat/placement de Tom → ouverture de sa fiche**. Les coordonnées de placement ont été envoyées à la souris automatisée : elles vérifient ce parcours, pas la précision d'un doigt humain.

| Viewport CSS | Hauteur du document | Plateau mesuré | Taille d'une case de la plaine | Boutons secondaires du rail | Résultat de mise en page |
| --- | --- | --- | --- | --- | --- |
| 320 × 568 | 568 px | 260 × 208 px | 26 × 26 px | 32 × 37 px | HUD et commandes dans le viewport ; fiche de Tom 150 × 184 px |
| 390 × 844 | 844 px | 390 × 312 px | 39 × 39 px | 36 × 40 px | HUD et commandes dans le viewport ; fiche de Tom 176 × 184 px |
| 844 × 390 | 540 px | 222,5 × 178 px | 22,25 × 22,25 px | 36 × 37 px | Défilement automatique de 150 px après clic sur Commencer ; HUD hors écran |

Dans le dernier cas, le bord supérieur de `#fd15` se trouve à `y = −150`, `.status` occupe `−66…−1 px`, et les réglages `−143…−109 px`. Ces éléments restent dans le document mais ne sont plus dans le viewport. Ce n'est donc pas une disparition du DOM. À position de défilement nulle, c'est le bas du jeu qui dépasse.

Autres mesures : réglages `35 × 34 px`, fermeture de fiche `24 × 24 px`, actions Évoluer/Retirer de hauteur `34 px`, bouton Commencer de l'atelier `43 px`. Les cartes d'achat permanent, elles, atteignent au moins `67 × 52 px` dans les trois formats ; agrandir indistinctement tous les contrôles n'est pas nécessaire.

Un premier appui sur **Tab** depuis la page initiale cible `#mapsButton`, derrière le menu. Après ouverture de l'atelier, le premier Tab cible également ce bouton extérieur au dialogue. `#board` n'a ni `tabindex`, ni rôle, ni nom accessible, ni contenu alternatif. Aucune erreur JavaScript de page n'a été observée pendant ces trois parcours. Cela ne valide ni les sept terrains, ni le combat complet.

Les captures et mesures brutes ont été produites temporairement sous `/tmp/fd-ux-01/` et ne sont pas ajoutées au dépôt ; les constats chiffrés ci-dessus sont conservés ici. La commande de serveur reproductible est `python -m http.server 8101 --bind 127.0.0.1`. Avec Playwright et un Chromium disponibles, créer les trois contextes décrits, charger `/index.html`, suivre le parcours ci-dessus et relever `getBoundingClientRect()`, `document.documentElement.scrollHeight`, `window.scrollY`, `document.activeElement` et les styles calculés. Fermer chaque contexte pour isoler son `localStorage`.

**Limites :** aucun essai sur téléphone réel, Safari/WebKit, lecteur d'écran ou utilisateur recruté ; pas de mesure de taux d'erreur tactile, de compréhension, de contraste exhaustif ou de fluidité. Les hypothèses sur les conséquences humaines restent à vérifier par des essais ciblés. Les styles effectifs ont été contrôlés : le minimum de hauteur actif est **540 px**, et non l'ancien `650 px` encore présent plus haut dans le fichier.

## UX-01 — Adapter réellement les faibles hauteurs et le paysage

**Priorité : très haute. Impact : accès au jeu entier. Confiance : élevée, défaut mesuré. Effort : M.**

**Preuve.** Le style final de `#fd15` fixe `min-height:540px` ([ligne 238](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L238)). `fit()` calcule l'arène à partir du bandeau et du dock ([lignes 871–889](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L871)) sans disposition spécifique au paysage. Résultat observé à 844 × 390 : document de 540 px, atelier dépassant `y=519 px`, puis autoscroll qui cache vies, monnaie, vagues, sortie et réglages.

**Conséquence.** Le joueur doit choisir entre voir ses ressources ou ses commandes pendant une situation où le plateau lui-même est réduit à 178 px de haut. Le paysage ne profite pas de sa largeur disponible.

**Recommandation.** Prévoir une disposition dédiée aux faibles hauteurs : plateau dans une zone centrale et boutique/actions dans une colonne latérale, HUD compact mais complet, dialogues dimensionnés selon le viewport effectif et contenu interne défilable. Définir une politique explicite de hauteur minimale et de zones sûres ; conserver les actions essentielles visibles sans dépendre d'un autoscroll. Ne pas seulement supprimer le minimum de 540 px : cela pourrait écraser davantage le plateau.

**Dépendances et arbitrages.** UX-02 définit les dimensions et gestes minimums ; le Développeur / QA valide redimensionnement et barres du navigateur. Aucun changement de règles de combat n'est nécessaire.

**Acceptation proposée.** Aux trois formats de référence, puis lors d'une rotation portrait/paysage, voir simultanément vies, argent, vague, plateau, lancement/pause et sortie de dialogue. Aucun défilement de page involontaire causé par un bouton ; un dialogue long défile à l'intérieur sans cacher sa commande de sortie. Vérifier ensuite sur Safari iOS et Chrome Android réels, dont zones sûres et barres visibles.

## UX-02 — Fiabiliser les commandes et le placement au doigt

**Priorité : haute. Impact : erreurs d'action et confort fréquent. Confiance : élevée sur les dimensions ; moyenne sur le taux d'erreur humain non mesuré. Effort : M à L.**

**Preuve.** Les styles effectifs du rail imposent `36 × 40 px`, puis `32 × 37 px` sur le petit format ([lignes 269, 286–287](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L269)). La fermeture de fiche est mesurée à `24 × 24 px` et Évoluer/Retirer à `34 px` de haut. Le placement utilise déjà capture du pointeur, prévisualisation et annulation ([lignes 752–758](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L752), [866–871](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L866)). La plaine ne présente que 26 px par case à 320 × 568.

**Conséquence.** Les commandes fréquentes offrent peu de marge tactile, surtout près d'une action de redémarrage. Les petites cases peuvent rendre difficile la sélection d'un emplacement voisin ; cette difficulté est plausible, pas démontrée par un taux d'échec. Une case de plateau n'est pas un bouton ordinaire : le geste glissé et l'aperçu existants sont déjà des moyens de précision à préserver.

**Recommandation.** Porter les zones interactives des commandes à au moins 44 × 44 pixels CSS, idéalement 48, avec espacement et priorité aux actions principales ; une icône peut rester plus petite que sa zone. Pour le plateau, tester un aperçu décalé du doigt, un grossissement local ou un mode de confirmation optionnel, plutôt que forcer une grille de dix colonnes à 440 px de large. Garder l'annulation du geste sans dépense et l'aperçu du trajet.

**Dépendances et arbitrages.** UX-01 doit réserver l'espace. Éviter qu'une confirmation obligatoire par tour ralentisse toutes les préparations ; choisir le mécanisme après essais de précision. Les cibles tactiles ne doivent pas se recouvrir.

**Acceptation proposée.** Mesurer les rectangles réellement interactifs, y compris après rotation ; contrôler absence de chevauchement. Avec un protocole humain documenté, comparer le placement sur cases adjacentes et près des bords, l'annulation, la sélection d'une tour et les achats. Publier taux d'erreur et temps avant/après ; ne pas annoncer le bénéfice d'une loupe sans l'avoir mesuré. `pointercancel` et sortie du plateau ne dépensent jamais de Z.

## UX-03 — Distinguer nouvelle tentative et effacement de progression

**Priorité : haute. Impact : compréhension roguelite et risque de réinitialisation involontaire. Confiance : élevée sur le parcours du code ; compréhension humaine non mesurée. Effort : S à M.**

**Preuve.** Le menu expose « Nouvelle partie » et « Continuer » ([ligne 433](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L433)). `launchNewGame()` confirme l'écrasement d'une sauvegarde puis appelle `newProfileState()`, qui remet à zéro `metaLevels`, étoiles, record et complétion ([lignes 448–450](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L448)). `startNewRun()`, à l'inverse, lance une nouvelle tentative en conservant la progression permanente ([ligne 1004](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L1004)). Le tutoriel de boucle est présent dans l'atelier, mais ne distingue pas explicitement ces deux commandes du menu.

**Conséquence.** « Nouvelle partie » peut être compris comme rejouer une tentative alors qu'il s'agit d'un nouveau profil. « Écraser la sauvegarde » ne détaille pas les étoiles et pouvoirs permanents qui seront perdus. Aucune sauvegarde réelle n'a été effacée lors de l'audit.

**Recommandation.** Nommer et séparer **Reprendre**, **Nouvelle tentative — conserve étoiles et pouvoirs**, et **Réinitialiser toute la progression**. Placer la dernière action dans une zone secondaire avec conséquences explicites et annulation par défaut. Ajouter au premier atelier une explication courte : Z de la tentative, étoiles persistantes, vies de la base et cœurs de reprise ; distinguer évolution achetée en Z pendant la préparation et pouvoir permanent. Conserver le bon récapitulatif de fin de tentative plutôt que créer un second système.

**Dépendances et arbitrages.** Développeur / QA garantit que le nouveau parcours ne change pas la signification des sauvegardes ; le Game Designer confirme les termes et le devenir des monnaies. Il s'agit de clarifier les actions existantes, pas de décider sans validation de nouvelles règles de progression.

**Acceptation proposée.** Avec une fixture synthétique comportant étoiles, pouvoirs et record, une nouvelle tentative conserve ces données après rechargement ; une réinitialisation ne les supprime qu'après confirmation qui les nomme. Un essai de compréhension doit vérifier que les participants distinguent les quatre ressources et prédisent l'effet des trois actions avant de cliquer.

## UX-04 — Faire correspondre les textes et annonces aux règles réelles

**Priorité : haute. Impact : choix tactiques et confiance dans les récompenses. Confiance : élevée sur les divergences source ; effet sur les décisions à mesurer. Effort : M.**

**Preuve.** `bonusOptions()` présente les groupes de bonus après les vagues **3, 6 et 9** ([ligne 535](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L535)). Le texte de la Cagnotte annonce les vagues **6 à 10**, alors que `wavePay()` l'applique de **4 à 6** ; la Grosse prime annonce **11 à 15**, alors que l'effet est de **7 à 9** ([lignes 518–535](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L518)). Les dix vagues et les menaces sont rendues deux fois en timelines via `updateMeters()` ([759–766](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L759)). Les cartes de boutique sont lisibles mais leurs sous-titres sont mesurés à 8 px sur le petit format, 9 px sur le format courant.

**Conséquence.** Une option économique peut être choisie en anticipant des revenus qui n'arriveront pas aux vagues indiquées. Les nombreuses informations compactes ne compensent pas une règle incorrecte, et les petits sous-titres demandent un effort de lecture. La répartition exacte de l'attention n'a pas été testée auprès de joueurs.

**Recommandation.** Décrire chaque bonus depuis les mêmes données que son application : début, fin, durée, montant et caractère temporaire/permanent. Afficher explicitement le prochain événement utile, puis permettre de consulter le détail des dix vagues sans comprimer toutes les informations au même niveau. Harmoniser « portée aérienne », prochaine vague et description de déblocage ; conserver un nom de rôle français cohérent, par exemple « Gel » plutôt que « Slow », si ce choix éditorial est retenu. Vérifier les cinq héros et tous les bonus ensemble.

**Dépendances et arbitrages.** Le Game Designer doit confirmer le calendrier voulu avant de décider s'il faut corriger le texte ou la règle ; cet audit ne tranche pas une modification de mécanique. La place gagnée dans les timelines doit servir la lisibilité et les cibles de UX-01/02.

**Acceptation proposée.** Pour chaque bonus, un tableau de référence permet de vérifier que les vagues annoncées sont exactement celles où l'effet s'applique. Comparer toutes les descriptions à la logique sur les sept terrains. Un joueur peut identifier la prochaine vague aérienne et le prochain boss avant lancement sans ouvrir les réglages ; les libellés essentiels restent lisibles au petit format et à l'agrandissement de texte retenu.

## UX-05 — Rendre les dialogues et le plateau accessibles autrement qu'au pointeur

**Priorité : haute pour les publics concernés. Impact : accès complet et prévention des actions derrière un dialogue. Confiance : élevée sur le focus et le DOM ; pas de certification d'accessibilité. Effort : M pour les dialogues, L pour le plateau.**

**Preuve.** Les dialogues ont souvent `role="dialog"` et `aria-modal="true"`, mais le menu n'a pas de nom accessible et le focus n'est ni déplacé ni confiné. Premier Tab mesuré : `mapsButton`, derrière le menu puis derrière l'atelier. Le Canvas est vide de sémantique et n'a pas de point d'entrée clavier ([lignes 414, 417–433](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L414)). Les interactions du plateau écoutent uniquement `pointer*` ([866–871](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L866)). En positif, le CSS prévoit déjà `:focus-visible`, des boutons ont des libellés et le récapitulatif respecte la réduction de mouvement pour son animation ([241](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L241), [979](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L979)).

**Conséquence.** Le clavier peut atteindre une action masquée par une fenêtre et ne peut pas réaliser le placement. La présence d'attributs ARIA seule ne rend pas le parcours accessible. L'ampleur exacte des problèmes avec VoiceOver/TalkBack reste à établir.

**Recommandation.** Nommer les dialogues, placer le focus sur une action pertinente, rendre l'arrière-plan inerte pendant l'ouverture, confiner la navigation et restaurer le focus à la fermeture. Définir la fermeture adaptée à chaque dialogue ; ne pas laisser Échap abandonner implicitement un choix obligatoire. Pour le plateau, concevoir une grille logique ou un curseur clavier avec nom de case, statut, sélection, prévisualisation et validation ; annoncer les erreurs et résultats utiles sans annoncer chaque dégât. Étendre de façon cohérente la préférence de réduction des animations aux effets de combat.

**Dépendances et arbitrages.** Développeur / QA fournit une gestion centralisée des dialogues et teste le parcours ; UX et Pixel Artist garantissent que les indications essentielles ne reposent pas uniquement sur couleur ou effets. Le choix de la représentation accessible du plateau mérite un prototype ciblé après validation, pas une refonte graphique globale.

**Acceptation proposée.** Au clavier, parcourir menu, atelier et dialogues sans atteindre les commandes derrière, avec focus visible et restauré. Acheter et poser une tour, annuler, inspecter et lancer une vague sans souris ; le parcours de reprise doit rester possible. Vérifier noms/états avec un lecteur d'écran réel et l'absence de bruit d'annonce excessif. Tester `prefers-reduced-motion` sur le combat et les récompenses.

## Articulation avec les autres expertises

Le bouton « Mode dev » est effectivement visible dans les trois formats mesurés. Sa conséquence économique et la politique de distribution relèvent en premier lieu du Game Designer et du Développeur / QA ; son traitement doit être coordonné, sans masquer simplement le bouton en laissant un parcours de production incohérent. La réduction de densité visuelle ne doit pas supprimer le feedback tactique dont le Pixel Artist et le Game Designer ont besoin. Une amélioration d'interface ne justifie pas de modifier les cinq héros ou leurs statistiques avant validation.
