# GD-01 / QA-02 — contrat UX des récompenses de progression

## Périmètre

Référence initiale : `main` au commit `0e14138bc42eefbfcb7dcef06be3f955d328292d`. Consignes `AGENTS.md` et `docs/COLLABORATION.md` lues au commit `e882b2278c9dfc99a06be89ef025743de988d81b` de la PR d'organisation. Le Game Designer définit le calcul ; le Développeur / QA est seul à modifier `index.html`. Ce document réserve les textes et les vérifications UX à ce correctif.

Contrat demandé : seules les vagues réellement terminées comptent pour les nouvelles récompenses et le record. Zéro vague terminée donne zéro nouvelle étoile, y compris après une défaite pendant la première vague. Les étoiles légitimement obtenues restent acquises après une défaite. Le format 38, les soldes, pouvoirs et records déjà enregistrés ne font pas l'objet d'une correction rétroactive.

Pas de refonte des menus, des héros, du style, du tactile ou des faibles hauteurs. Les défauts précédemment audités de pause, de viewport et d'accessibilité générale ne font pas partie de cette livraison.

## Textes français minimaux proposés

| Emplacement | Texte / règle | Raison |
| --- | --- | --- |
| Sous-titre de fin de tentative | `Terrain {terrain} · {vaguesLocalesTerminées}/10 vagues terminées` | Distingue le compteur de progression de la vague commencée. |
| Bilan global lorsqu'il est affiché dans l'atelier | `Vagues terminées : {n}/70 · Record : {record}/70` | Rend explicite la même unité dans le reçu et le record. |
| Explication courte du reçu, si `n = 0` | `Aucune vague terminée : +0 étoile.` | Explique le zéro sans suggérer que le portefeuille a été effacé. |
| Explication courte du reçu, si `n > 0` | `Seules les vagues terminées rapportent des étoiles.` | Explique le périmètre du calcul sans promettre une étoile par vague. |
| Confirmation de sortie | `Quitter la tentative ? Les étoiles sont calculées sur les vagues terminées.` | Annonce le calcul avant la décision, sans laisser croire que la vague active sera créditée. |
| Explication de la boucle, si un texte existant est remplacé | `Les étoiles gagnées restent acquises, même après une défaite.` | Précise la persistance ; ne remplace pas le libellé de remise à zéro du profil. |

Ces textes sont un contrat de contenu ; conserver les composants et la hiérarchie existants. La défaite n'est pas présentée comme une pénalité sur le portefeuille permanent. Un reçu à `+0 ★` doit continuer d'afficher le solde antérieur inchangé. La phrase « seules les vagues terminées » ne signifie pas qu'un revenu est versé après chaque vague : la récompense de tentative reste calculée à sa fin selon la formule retenue par le Game Designer.

## Unité des compteurs et parcours sur la carte

Le compteur de combat `g.wave` indique une vague commencée ; il peut conserver ce sens dans le HUD et dans le contexte de défaite. Le reçu, la progression et le record doivent au contraire utiliser le nombre de vagues terminées de la tentative, noté `n` dans le reçu.

Pour le terrain courant d'index `level`, afficher `max(0, min(10, n - level × 10))` vagues locales terminées. Le sous-titre peut donc indiquer `0/10 vagues terminées` tandis que le joueur vient de perdre pendant la vague 1 : les libellés rendent cette différence compréhensible.

Le parcours visuel présentait un défaut lié au même contrat : `renderRewardJourney()` marquait le terrain courant terminé dès que `g.life > 0` (ligne 934 de la référence). Un abandon pendant la préparation ou une vague active pouvait donc afficher une coche de victoire. Une coche de terrain terminé doit provenir de dix vagues locales terminées : pour le terrain d'index `i`, `n >= (i + 1) × 10`. Le terrain courant reste identifiable comme point d'arrêt sans devenir gagné par le seul fait que des vies restent.

| Scénario d'un nouveau reçu | Compteur local attendu | Parcours attendu |
| --- | --- | --- |
| Abandon avant ou pendant la vague 1 de la plaine | 0/10 | Plaine courante, aucune coche de terrain gagné. |
| Défaite pendant la vague 1 de la plaine | 0/10 | Même progression ; gain nul et solde permanent conservé. |
| Vague 1 terminée, préparation ou abandon pendant la vague 2 | 1/10 | Plaine courante, non terminée ; le gain légitime n'est pas annulé. |
| Dix vagues de la plaine terminées | 10/10 | Plaine terminée. |
| Entrée sur le deuxième terrain, aucune vague locale terminée | 0/10, total 10/70 | Plaine terminée ; deuxième terrain courant, non terminé. |
| Victoire de campagne régulière | 10/10, total 70/70 | Sept terrains terminés. |

Ne pas recalculer les anciens reçus sauvegardés pour retirer des gains historiques : le correctif préserve les acquis et le format 38. Le calcul corrigé concerne les nouvelles attributions.

## Parcours de test explicitement séparé

Le raccourci de développement ne doit pas être accessible dans le parcours normal. Le masquer doit être accompagné d'une garde dans son gestionnaire ; une activation par le DOM ne doit pas contourner cette garde.

Pour l'activation explicite `?dev=1`, proposer un marquage textuel visible **`MODE TEST · progression séparée`**, y compris au menu puis dans le jeu, et un bouton nommé **`Passer le terrain (test)`**. Une simple différence de couleur ou un paramètre invisible dans l'adresse ne suffit pas à distinguer les profils. Le titre de l'onglet peut également rappeler le mode test, sans en faire le seul signal.

La sauvegarde de test utilise un espace séparé. Elle ne lit, n'importe ni n'écrase le profil normal ; le retour sans `?dev=1` retrouve ce dernier. Les libellés « Continuer » et « Nouvelle partie » restent cohérents dans chaque profil : ils concernent le mode visiblement annoncé, sans créer une refonte du menu ni ajouter une commande d'import. Les réglages qui pourraient affecter le profil normal doivent également être examinés par le Développeur / QA.

## Vérifications UX prévues

1. Profil neuf, abandon avant et immédiatement après lancement de la première vague : reçu à `+0 ★`, compteur à zéro vague terminée, aucun terrain coché à tort.
2. Profil synthétique avec solde permanent non nul, défaite en première vague : aucun débit d'étoiles antérieures ; le message explicatif parle du gain nul de cette tentative.
3. Au moins une vague réellement terminée, puis défaite ou abandon : reçu, record et parcours ne créditent pas la vague active ; la récompense légitime des vagues précédentes reste visible et conservée après rechargement.
4. Profil normal, puis mode test puis retour au profil normal : séparation visible et absence de contamination des données. Bouton de développement absent du parcours normal et sans effet si son gestionnaire est sollicité.
5. Lecture des textes aux formats 320 × 568 et 390 × 844 : sous-titre et explication compréhensibles, sans sortie du dialogue ou masquage des actions existantes. Contrôler le paysage sans inclure sa refonte dans ce correctif.

Les essais utilisent un navigateur et un stockage isolés, avec fixtures synthétiques lorsqu'un état précis est nécessaire. Ils ne valent pas essai sur téléphone réel, ni étude de compréhension auprès de joueurs.

## Résultats UX réellement obtenus

Les contrôles ci-dessous ont été exécutés avec Playwright Python et Chromium système `156.0.8078.79`, dans des contextes neufs (`is_mobile=True`, `has_touch=True`, facteur de pixels `1`). Le serveur HTTP local du port `8104` servait une copie temporaire exacte du HTML intégré, prise avant chaque série pour éviter une lecture pendant son écriture. Aucun stockage utilisateur réel n'a été utilisé ; le serveur et les contextes ont été fermés.

**Première série, 320 × 568 et 390 × 844 pixels CSS**, sur le snapshot SHA-256 `26692b518a97cd424502f4aeb6a68e04dd378bd5b1d1fa81e4591e29f8a53f21` :

| Contrôle exécuté | Résultat observé |
| --- | --- |
| Profil neuf → atelier → commencer → lancer la vague 1 → pause → Quitter | Confirmation explicite ; reçu `+0 ★`, solde `0`, sous-titre `Terrain 1 · 0/10 vagues terminées`, explication du gain nul. |
| Parcours de carte de ce reçu | Aucune coche de terrain terminé. Un écart subsistait : badge local `1/10` alors que le sous-titre annonçait `0/10` terminées. Écart signalé puis corrigé par le Développeur / QA. |
| Commande de développement en mode normal | Bouton invisible ; appel à son clic par le DOM sans changement du compteur `0/10`. |
| Même contexte, passage à `?dev=1` sans sauvegarde de test préalable | Menu `MODE TEST · progression séparée`, Continuer désactivé malgré la sauvegarde normale présente ; aucun import de cette sauvegarde. |
| Nouvelle partie de test puis raccourci autorisé | Route préfixée `TEST`, bouton `Passer le terrain (test)` visible, résultat de terrain de test affiché. La valeur de la clé normale est restée identique octet pour octet. |
| Retour sans paramètre de test | Menu normal, Continuer activé, bouton de développement invisible et valeur de sauvegarde normale toujours identique. Clés normale et de test distinctes. |
| Erreurs JavaScript de page pendant ces parcours | Aucune observée. |

**Contrôle ciblé après correction du badge**, à 320 × 568, sur le snapshot SHA-256 `414d498f6328a56c43d831432f8f978cf41fdeadac1780a8e3d00cc7d57d6edc` : le même abandon de vague 1 affiche désormais **`0/10` dans le badge et `0/10 vagues terminées` dans le sous-titre**, `+0 ★` et aucune coche de victoire. Le dialogue finit à `y = 564 px`, ses actions à `555 px`, dans un viewport haut de `568 px` ; le texte explicatif est visible et aucune erreur JavaScript de page n'a été observée. La relecture source confirme également les noms accessibles de boutons du menu test mis en accord avec leurs libellés visibles.

Ces contrôles UX portent sur les libellés, le reçu, le petit format et la séparation visible des profils. Ils ne démontrent pas à eux seuls toutes les règles économiques, la compatibilité de toutes les sauvegardes 38, une défaite jouée après plusieurs vagues ou l'impossibilité de toute modification locale. Ces garanties nécessitent les vérifications du Game Designer et du Développeur / QA. Safari/WebKit, appareil réel, lecteurs d'écran, paysage et étude de compréhension n'ont pas été testés pour ce correctif ; la correction des défauts antérieurs de ces domaines reste hors périmètre.
