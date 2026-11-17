# Mission 01 — analyse du Pixel Artist

## Périmètre et méthode

Référence analysée : `main`, commit `0e14138bc42eefbfcb7dcef06be3f955d328292d`. Consignes lues dans la PR d'organisation, commit `e882b2278c9dfc99a06be89ef025743de988d81b`, qui n'était pas encore intégré dans `main` au début de cette mission.

Cette analyse ne crée ni ne remplace aucune ressource du jeu. Les données de `GRAPHICS` ont été décodées dans un dossier temporaire, sans réencodage ni modification de `index.html`. Inspection visuelle réelle : atlas complet, cinq portraits, icônes de Tom et Raphaël, feuilles `idle[0][0]`, `attack[0][0]`, `attack[1][2]`, `idle[2][2]`, `attack[3][2]`, `attack[4][2]` et cinq effets. Les dimensions et poids ont été mesurés sur les 46 images de `GRAPHICS`. Des bornes alpha ont été calculées sur sept feuilles, avec un seuil de 16/255.

Il s'agit d'une inspection des images sources et du code de rendu, sans partie jouée ni mesure de fluidité dans un navigateur. Les risques de recouvrement sur petit écran restent à confirmer en situation réelle avec UX et QA. Les coûts mémoire ci-dessous sont des calculs de surfaces RGBA, pas une mesure de consommation du navigateur.

## Ce qu'il faut préserver

Les cinq héros disposent déjà d'identités visuelles cohérentes entre portraits et atlas :

| Héros | Repères observés à conserver | Signature d'action |
| --- | --- | --- |
| Tom | Cheveux bruns/orange dressés, tenue orange, bandages, poings | Énergie dorée et tirs rapides |
| Raphaël | Cheveux sombres, tenue bleu nuit, cape, fusil à lunette | Rayon cyan précis |
| Ylvine | Silhouette trapue, barbe et cheveux roux, gantelets massifs | Feu orange, roche et explosion |
| Jordan | Bonnet rouge, barbe brune, manteau bleu à fourrure, poings | Glace bleue, cristaux et flocons |
| POY | Lunettes, cheveux sombres à accents verts, tenue noire et verte | Énergie verte et grande zone |

L'atlas contient cinq colonnes et trois lignes de formes. Son style est un chibi anime illustré avec contours, volumes et effets lumineux, plutôt qu'un pixel art rétro. Une conversion stylistique générale n'est pas recommandée dans cette première feuille de route. Les noms et les trois formes de combat restent ceux de `D` ([source](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L453)).

## Données utiles à la décision

| Groupe | Nombre | Dimensions des sources | Poids compressé décodé des data URI | Surface RGBA théorique |
| --- | ---: | --- | ---: | ---: |
| Atlas | 1 | 640 × 384 | 407 949 octets | 983 040 octets |
| Portraits | 5 | 512 × 512 | 1 880 874 octets | 5 242 880 octets |
| Icônes | 5 | 128 × 128 | 165 257 octets | 327 680 octets |
| Effets | 5 | 384 × 256 | 583 238 octets | 1 966 080 octets |
| Repos | 15 | 640 × 160, quatre cases de 160 × 160 | 849 866 octets | 6 144 000 octets |
| Attaques | 15 | 960 × 160, six cases de 160 × 160 | 2 090 706 octets | 9 216 000 octets |
| Total `GRAPHICS` | 46 | — | 5 977 890 octets | 23 879 680 octets, soit environ 22,8 Mio |

Le fichier HTML pèse 9 821 126 octets. Ses 52 data URI d'images, incluant les ressources hors `GRAPHICS`, représentent 9 655 233 caractères ASCII, soit environ 98,3 % de sa taille ; leur contenu décodé totalise 7 240 519 octets. La taille transférée avec compression HTTP et la mémoire effectivement allouée n'ont pas été mesurées.

## Cinq améliorations prioritaires

Ordre proposé selon portée joueur et preuves disponibles. P1 : premier lot après validation ; P2 : lot suivant. Effort relatif : S = intervention locale, M = contrat et plusieurs ressources/consommateurs, L = travail de production étendu. Ces catégories ne constituent pas un chiffrage calendaire.

### ART-01 — Réduire le coût des ressources sans changer le style ni les héros

- **Preuve.** Les mesures ci-dessus montrent la prédominance des images dans le HTML. Les cinq portraits 512 × 512 représentent 1,88 Mo compressés, alors que `portraitDraw` les redimensionne pour des vignettes et que l'atelier les dessine dans un canvas de 96 × 96. `loadGraphic` instancie immédiatement les images de tous les groupes, y compris les 30 feuilles d'animation ; `decoding='async'` ne constitue pas un chargement conditionnel ([sources : chargement](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L706), [portraits](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L715), [atelier](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L908)).
- **Effet joueur.** Risque de démarrage coûteux sur mobile et de pression mémoire avant même que les formes avancées soient utiles. L'ampleur du ralentissement est une hypothèse à mesurer, pas un défaut de performance déjà reproduit.
- **Recommandation.** Définir avec le développeur les dimensions d'affichage réelles et les densités d'écran visées ; comparer des exports adaptés des portraits et des optimisations sans perte des feuilles. Conserver les sources originales hors du chemin de chargement du jeu. Évaluer séparément un chargement des formes à leur première utilisation, en gardant une solution de repli déjà prête. Préserver le fonctionnement autonome du HTML ; ne pas ajouter de CDN par défaut.
- **Priorité / impact / confiance / effort.** P1 ; portée élevée sur tous les nouveaux lancements ; confiance forte sur les poids, moyenne sur le gain utilisateur ; M.
- **Dépendances.** QA pour une référence de démarrage sur le même appareil/profil réseau ; UX pour tailles de vignettes ; développeur pour le décodage et les états de repli.
- **Acceptation.** Inventaire avant/après des octets et surfaces ; comparaison visuelle des cinq héros aux tailles réelles et à forte densité ; démarrage et mémoire comparés dans le même environnement ; toutes les 15 formes et 30 feuilles restent disponibles ; aucun appel réseau externe ajouté, aucune modification de sauvegarde. Le budget final doit être fixé après la mesure de référence, sans annoncer à l'avance un pourcentage de gain garanti.

### ART-02 — Faire passer les ennemis, la santé et les états avant les effets décoratifs

- **Preuve.** Les effets sources ont de larges masses lumineuses, particulièrement le vert de POY et les cristaux de Jordan. `drawSignatureEffect` ajoute une image semi-transparente aux effets procéduraux ; `draw` dessine ensuite les effets de combat après les ennemis, leurs barres de vie et leurs noms de boss. Les tailles de signature atteignent 112 unités pour POY, face à des ennemis terrestres de 32 à 58 unités. Ce constat décrit l'ordre des couches, pas une durée d'occultation mesurée ([signature](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L783), [ordre de rendu](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L861)).
- **Effet joueur.** En cas de tirs multiples ou d'explosions superposées, le joueur risque de perdre l'information essentielle : quelle cible survit, laquelle est gelée ou protégée, et si le boss approche de la sortie. Une sensation de puissance ne doit pas cacher la conséquence de l'action.
- **Recommandation.** Définir une hiérarchie commune : décor et zones au sol, unités, attaques transitoires, puis santé/états critiques et indicateurs de sortie. Réduire les parties opaques centrales des signatures avant de diminuer la reconnaissance du héros. Différencier les fonctions par forme : laser linéaire pour Raphaël, cristaux/ruptures pour Jordan, éclats radiaux pour Ylvine, grand choc vert pour POY ; ne pas s'appuyer uniquement sur la couleur.
- **Priorité / impact / confiance / effort.** P1 ; impact tactique élevé ; confiance forte sur les couches et dimensions, moyenne sur la gêne en partie ; M.
- **Dépendances.** UX définit la priorité des informations ; Game Designer confirme ce qui doit rester visible lors des effets de zone ; QA prépare des scènes chargées reproductibles.
- **Acceptation.** Captures de scènes identiques, avec et sans effets renforcés, aux trois vues mobiles de référence ; barres de vie et état du boss jamais masqués par une signature décorative ; gel, marquage et bouclier distinguables sans lire les chiffres de dégâts ; dommages, portée et cadence strictement inchangés. Ne pas ajouter une sixième famille d'effets avant d'avoir vérifié cette hiérarchie.

### ART-03 — Rendre distincts les trois niveaux de combat et les paliers permanents

- **Preuve.** Le rendu du plateau choisit les feuilles par `t.lvl`, mais `portraitDraw` et `iconDraw` utilisent toujours la même image par héros. `refreshShopSkins` ne transmet aucun palier à `iconDraw`. Les paliers permanents 1 et 2 ont exactement la même expression visuelle dans l'anneau ajouté par `renderHeroBoard` : seuls le palier 3 et l'absence de palier sont distingués. L'atelier possède déjà des points et des noms de pouvoirs ; la recommandation vise la cohérence entre ces écrans et le plateau, pas l'absence totale d'indication ([dessin des images](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L714), [anneau](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L737), [boutique](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L739)).
- **Effet joueur.** L'image énergique d'un héros ne permet pas à elle seule de reconnaître l'achat permanent actif. Ajouter simplement de plus grosses auras entretiendrait la confusion entre niveau acheté en Z et progression en étoiles.
- **Recommandation.** Fixer une grammaire à deux axes avec UX : forme corporelle et marque I–III pour le niveau de combat ; symbole de pouvoir et compteur 0–3 pour l'évolution permanente. Employer les cinq portraits actuels comme identité stable, accompagnés d'un indicateur explicite, plutôt que produire immédiatement 20 nouveaux portraits. Les effets propres aux pouvoirs restent une confirmation en action, pas l'unique indication du palier.
- **Priorité / impact / confiance / effort.** P1 ; impact élevé sur compréhension et valeur perçue de la progression ; confiance forte ; M.
- **Dépendances.** UX pour les libellés et la place des indicateurs ; Game Designer pour l'association pouvoir/palier ; développeur pour les consommateurs d'images. Les étoiles de niveau affichées sur le plateau doivent être prises en compte pour ne pas ajouter un troisième vocabulaire concurrent.
- **Acceptation.** Matrice revue des 5 héros × 3 niveaux de combat × 4 états permanents ; niveau et palier correctement identifiables dans atelier, inspecteur et plateau sans supposer qu'ils sont le même axe ; contrôle sans distinction des couleurs ; aucun changement des cinq identités ni des valeurs de progression.

### ART-04 — Stabiliser cadrage, échelle et marges des animations

- **Preuve.** Les dimensions de feuilles respectent le découpage 160 × 160 prévu. En revanche, les proportions varient fortement : à alpha ≥ 16/255, Tom au repos I occupe environ 88 × 145 pixels dans une case, contre 154 × 103 pour Raphaël III. Les auras participent à ces bornes : cela ne mesure pas la seule taille du corps. Sur les attaques inspectées, des pixels opaques atteignent la limite droite et/ou basse de la case, notamment Raphaël III aux images d'attaque 3 à 5. Cela établit une absence de marge et un risque de coupe, pas la preuve que le dessin original contenait une partie perdue. Le rendu applique en outre une largeur nominale `84 × 1,18 = 99,12` au niveau III, pour une case de plateau de 60 unités ([contrat de rendu](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L727), [appel plateau](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L854)).
- **Effet joueur.** Les silhouettes trapues et les grandes auras peuvent devenir proportionnellement plus importantes que le héros lui-même, se recouvrir entre cases ou sembler changer de taille lorsqu'une attaque commence. Les mesures seules ne suffisent pas à qualifier un mouvement volontaire de tremblement indésirable.
- **Recommandation.** Établir un manifeste par feuille : corps et effets séparés dans les critères de cadrage, ancrage des pieds, rectangle utile, marge d'export et échelle d'affichage. Vérifier les trois formes dans une grille dense avant toute retouche. Garder Ylvine trapu et les différences de stature ; harmoniser la lecture et les points d'appui plutôt que forcer toutes les silhouettes à une même hauteur.
- **Priorité / impact / confiance / effort.** P2 ; impact moyen à élevé sur placement et lecture de l'armée ; confiance forte sur les mesures, moyenne sur le problème perçu ; M.
- **Dépendances.** Développeur pour les ancrages et la composition du plateau ; UX pour les zones de sélection ; QA pour les changements repos/attaque et les bords du plateau.
- **Acceptation.** Les 30 feuilles passent un contrôle de dimensions, alpha et bornes ; les dépassements volontaires sont documentés ; aucun effet utile n'est coupé ; pied stable sur le socle au repos et lors du tir ; vérification des 15 formes côte à côte et aux bords des sept terrains ; pas de changement de case occupée, de portée ou de hitbox.

### ART-05 — Faire correspondre pose, direction et moment du feedback d'attaque

- **Preuve.** Les feuilles observées reposent sur une pose dominante tournée vers la droite, avec des variations de recul et d'énergie. Le code utilise `t.aim` pour le recul et des effets, mais `renderHeroBoard` sélectionne une image sans orientation de la feuille. Les six images d'attaque sont distribuées sur la fenêtre fixe de recul de 0,19 s, tandis que `attack` applique les dégâts dès le déclenchement. Ainsi la pose de fusil peut rester vers la droite pendant qu'un rayon vise une cible à gauche ; la conclusion vient du code et des sources, sans essai de cette scène dans le navigateur ([déclenchement](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L644), [sélection des images](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L727), [utilisation de la visée](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L852)).
- **Effet joueur.** Risque d'affaiblir le lien entre le héros qui tire, sa cible et la perte de vie. Raphaël est particulièrement sensible à cette discordance, son arme ayant une direction explicite.
- **Recommandation.** Commencer par une convention droite/gauche et une origine d'effet raccordée à la pose, sans produire immédiatement un grand nombre de directions. Évaluer les détails asymétriques avant d'utiliser un miroir. Placer le feedback de contact au moment réel du dégât ; réserver anticipation et charge aux moments déjà disponibles dans la logique. Ne pas introduire un délai de dégâts pour rendre l'animation plus spectaculaire.
- **Priorité / impact / confiance / effort.** P2 ; impact moyen sur compréhension et sensation d'impact ; confiance forte sur le mécanisme, moyenne sur l'importance ressentie ; M, potentiellement L si de nouvelles directions sont ensuite validées.
- **Dépendances.** Game Designer garantit le calendrier des attaques ; développeur fournit moment de tir et direction ; UX et QA vérifient la lecture sans son et à vitesse accélérée.
- **Acceptation.** Séquences revues avec cibles à droite, à gauche, au-dessus et en dessous, pour les cinq héros et leurs formes ; origine et contact visuels cohérents avec la cible ; tests aux vitesses proposées par le jeu ; journal de dégâts identique avant/après ; aucun changement de cadence, sélection de cible ou bonus.

## Contradictions à arbitrer avec les autres rôles

- **Spectacle contre lisibilité.** Une demande de puissance visuelle supplémentaire doit respecter ART-02 ; préserver les signatures propres aux héros, puis diminuer leur occupation de l'information tactique, plutôt que supprimer tous les effets.
- **Diversité graphique contre coût mobile.** ART-03 propose d'abord des indicateurs réutilisables. Une multiplication des portraits, directions et variantes doit passer par le budget de ressources d'ART-01.
- **Animation contre règles de combat.** ART-05 adapte la présentation au moment réel du dégât. Un changement du timing de combat relève d'une autre décision et d'une nouvelle validation d'équilibrage.
- **Uniformité contre identité.** ART-04 vise des ancrages et marges prévisibles, sans rendre Ylvine aussi élancé que Raphaël ni effacer lunettes, barbe, bonnet ou palettes distinctives.

## Reproduction des mesures et limites

Les groupes ont été récupérés en parsant l'objet JSON après `const GRAPHICS=` ; chaque data URI a été décodée avec `base64.b64decode`, puis ouverte avec Pillow pour lire dimensions et canal alpha. Le poids compressé est la somme de la longueur des binaires obtenus ; la surface théorique est `largeur × hauteur × 4`. Pour les feuilles citées, chaque tranche horizontale de 160 pixels a été évaluée avec `alpha >= 16` avant calcul du rectangle englobant. L'inventaire global des images utilise le motif `data:image/...;base64,...` sur le HTML complet.

Les fichiers extraits et calculs intermédiaires sont temporaires et ne font pas partie des ressources livrées dans la PR. Aucun nouvel art, aucune vidéo, aucun test utilisateur ni benchmark navigateur n'est revendiqué. Les recommandations restent à valider par l'utilisateur avant toute implémentation.
