# L1 — préservation graphique et lisibilité du feedback de sauvegarde

## Référence et périmètre

Référence de départ : `main` au commit `14361f3301c4ceaa6f4d5d12e689da15b16936c5`, branche de travail `fix/l1-reliable-progress`. `AGENTS.md`, `docs/COLLABORATION.md` et la feuille de route de la mission 01 ont été lus.

Le Pixel Artist contrôle la préservation des cinq héros et des ressources, puis la lisibilité des nouveaux messages de sauvegarde. Il n'a modifié ni `index.html`, ni les images, ni les tests, ni l'état Git. Le présent document est son seul fichier livré ; les inventaires, scripts et captures restent temporaires.

Le contrôle navigateur final porte sur une copie locale stable de `index.html`, SHA-256 `c9bac111c434e6acb81f125bc36bad606ef80ac7b79c43eb750160ed943b536c`. Son identité avec le fichier de travail a été vérifiée après les observations. La publication et la validation fonctionnelle intégrée relèvent du coordinateur et du Développeur / QA.

## Ressources préservées avant, pendant et après le correctif

Un SHA-256 a été calculé pour chaque data URI d'image et chaque bloc SVG du source, dans leur ordre d'apparition. Le contrôle a été répété au démarrage, pendant l'implémentation et sur la version figée ; les listes sont strictement identiques à la référence.

| Élément | Avant | Pendant | Après |
| --- | ---: | ---: | ---: |
| Data URI d'images, avec comparaison individuelle | 52 | 52 identiques | 52 identiques |
| Blocs SVG, avec comparaison individuelle | 15 | 15 identiques | 15 identiques |
| Lignes CSS existantes | Référence | Toutes conservées | Toutes conservées |

Empreintes des séquences, obtenues en concaténant les SHA-256 individuels avec un saut de ligne :

- Images : `813c4db1bf112fbd03e83448426d6b09d365adc8c3a67cd92154c47156d034ae`.
- SVG : `c7b03e0ffc6df0c005babe8324dffedcc924dc004174586fcd0b6fb3f21fb58b`.

Ces mesures sont un contrôle ponctuel de ce correctif, pas une interdiction permanente d'améliorer les ressources dans une future mission artistique autorisée. Aucun test durable figeant les images ou leurs empreintes n'a été ajouté.

Tom, Raphaël, Ylvine, Jordan et POY conservent leurs portraits, icônes, atlas, feuilles de repos et d'attaque, couleurs et identités. Aucune nouvelle illustration, conversion de format ou réinterprétation stylistique n'est incluse.

Les deux blocs `<style>` existants sont conservés. Le changement CSS ajoute uniquement des règles locales à `#saveStatus`, ses boutons, `#saveRecovery` et ses descendants. Aucune règle de héros, sprite, animation, palette ou plateau n'est remplacée. Les boutons nouvellement ajoutés au statut ont été portés de 32 à 44 pixels de hauteur minimale avant le contrôle final ; ce réglage reste limité aux nouvelles actions de sauvegarde.

## Méthode navigateur et observations visuelles

Chromium système headless (`/usr/bin/chromium`), contextes jetables avec tactile émulé, serveur local sur port libre servant uniquement la copie temporaire. Huit contextes ont couvert quatre scénarios à deux formats : **320 × 568** et **390 × 844 pixels CSS**. L'ouverture du dialogue dans les deux scénarios d'erreur au menu porte le total à **douze états observés**.

Les erreurs de stockage sont injectées uniquement dans ces profils : JSON volontairement invalide, refus de lecture par `SecurityError`, refus d'écriture par `QuotaExceededError`. L'état de pause dérive de la fixture synthétique `tests/fixtures/save-v38.json`, avec combat actif en pause et vitesse ×3. Il ne s'agit ni de données réelles, ni d'une corruption ou saturation spontanée d'un téléphone.

Des captures du menu, de l'écriture refusée, de la reprise en pause et du dialogue de récupération ont été prises. Ont notamment été inspectées visuellement la capture de quota à 320 px, celle du dialogue de récupération à 320 px et celle de la pause à 390 px. Les rectangles et couleurs calculées ont été relevés pour tous les états.

| État | Résultat à 320 × 568 | Résultat à 390 × 844 |
| --- | --- | --- |
| JSON invalide au menu | Statut de 320 × 74,84 px, entièrement visible ; message de conservation et action Gérer la sauvegarde | Statut de 390 × 74,84 px, entièrement visible |
| Lecture refusée au menu | Message explicite, retour à la ligne ; aucun nom d'exception technique exposé | Message entièrement visible, sans dépassement horizontal |
| Dialogue de récupération | Panneau de 300 × 415,33 px, de y=76,34 à y=491,66 ; texte et commandes dans la vue | Panneau de 370 × 405,33 px, de y=219,34 à y=624,66 ; texte et commandes dans la vue |
| Écriture refusée en jeu | Statut dans le flux du dock, 304 × 74,84 px ; export de la progression en mémoire visible | Statut de 366 × 74,84 px ; commandes de jeu visibles |
| Combat repris en pause à ×3 | Indicateur de pause `aria-pressed=true`, bouton de reprise visible, vitesse ×3 | Même état et vitesse ; plateau et dock entièrement dans la vue |

Les nouvelles actions Gérer la sauvegarde, Exporter la progression en mémoire, Exporter la sauvegarde conservée et Annuler ont une hauteur mesurée de **44 px** aux deux formats. Le bouton long de création de profil occupe **54 px à 320 px** et **44 px à 390 px**, sans texte tronqué. Son état initial désactivé est visible ; ce contrôle graphique ne remplace pas les tests fonctionnels de consentement et d'export.

Le statut utilise le texte `rgb(227,242,248)` sur un fond plein `rgb(16,45,67)`, soit un contraste sRGB calculé de **12,39:1**. Le message et le libellé d'action portent l'information sans dépendre de la couleur. Le statut possède `role="status"` et `aria-live="polite"` ; cela constate le balisage, sans revendiquer un essai au lecteur d'écran.

Dans les douze états, aucune erreur JavaScript de page n'a été observée. La largeur du document reste celle du viewport, sans débordement horizontal ; le message, ses nouvelles actions et les commandes essentielles restent visibles. Le dialogue de récupération est volontairement modal et masque le parcours sous-jacent lorsqu'il est ouvert.

## Compromis identifié et limites

**Aucun problème graphique bloquant relevé sur les deux formats contrôlés.** Les avertissements restent persistants et utilisables sans changer l'apparence des héros ou masquer les commandes derrière un bandeau.

À 320 × 568, l'avertissement d'écriture refusée et son bouton occupent environ 75 px dans le dock. Le mécanisme existant de disposition réduit alors le plateau mesuré à **177,5 × 142 px** ; dans l'état de pause sans erreur, le plateau mesure **240 × 192 px**. Le statut ne recouvre pas le plateau, mais ce coût d'espace réduit encore la précision de placement sur petit écran. C'est un compromis explicite pour rendre l'échec de sauvegarde visible ; son ergonomie au doigt et une disposition de faible hauteur doivent être traitées dans L2, plutôt qu'élargir cette correction en refonte du plateau.

Non réalisés dans ce contrôle : essai tactile humain, paysage, zoom utilisateur, lecteur d'écran, Safari/WebKit, appareil mobile réel, scène de combat dense ou benchmark de mémoire. Les contrôles d'intégrité des sauvegardes, des récompenses et des reprises restent ceux des suites de régression et de la validation finale du coordinateur. Aucun accès à GitHub Pages ou changement d'origine du jeu n'a été effectué par le Pixel Artist.
