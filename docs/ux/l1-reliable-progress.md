# L1 — états de sauvegarde et reprise compréhensible

## Périmètre et responsabilités

Référence de départ : `main` au commit `14361f3`, branche `fix/l1-reliable-progress`. Les consignes `AGENTS.md`, `docs/COLLABORATION.md` et la feuille de route de la mission 01 ont été lues. Le Développeur / QA est seul à modifier `index.html` et les helpers existants ; l'UX réserve ce document et le nouveau fichier `tests/test_l1_browser.py`.

L'objectif est de protéger la progression et d'expliquer les états de sauvegarde. Les clés et le format 38, les étoiles, pouvoirs, records et complétions déjà acquis sont préservés. La mission ne refait pas les menus, le plateau, les héros ou l'ergonomie paysage de L2.

## Contrat des états et textes français

| État détecté | Message destiné au joueur | Commandes et protection |
| --- | --- | --- |
| Aucune sauvegarde | `Aucune sauvegarde sur cet appareil.` | Continuer indisponible ; Nouveau profil permet de commencer. |
| Sauvegarde valide | `Une sauvegarde est disponible.` | Continuer reprend la session ; une nouvelle tentative conserve la progression permanente. |
| Enregistrement réussi pendant le jeu | `Progression enregistrée.` | Retour discret, sans annonce répétée à chaque image. |
| Données illisibles ou incohérentes, mais contenu brut accessible | `Cette sauvegarde ne peut pas être reprise. Elle a été conservée.` | Continuer indisponible ; proposer la récupération de la copie brute, sans remplacer automatiquement les données. |
| Seule la tentative est invalide, profil permanent 38 valide | `Cette tentative ne peut pas être reprise. Tes étoiles, pouvoirs et record peuvent être conservés.` | Après sauvegarde de la copie brute et consentement, proposer une nouvelle tentative en préservant les acquis vérifiés. |
| Version non prise en charge | `Cette sauvegarde vient d’une autre version du jeu. Elle a été conservée.` | Même protection ; ne pas présenter ce cas comme une absence de sauvegarde. |
| Accès à la sauvegarde refusé | `Impossible de lire la sauvegarde sur cet appareil. Aucune donnée n’a été remplacée.` | Continuer indisponible ; pas de réinitialisation aveugle ni de promesse d'export d'un contenu inaccessible. |
| Échec d'écriture, dont manque de place ou stockage refusé | `Progression non enregistrée. Garde cette page ouverte.` | Le jeu peut garder sa session en mémoire, mais ne prétend pas que les changements sont persistés ; conserver la dernière sauvegarde disponible. |

Le contenu visible ne doit pas exposer les noms d'exceptions JavaScript, une trace technique ou du JSON. Les détails techniques restent dans les tests ou le diagnostic. Un message « conservée » décrit le maintien du contenu existant ; il ne promet pas une synchronisation externe.

## Contrat des composants

IDs convenus avec le Développeur / QA :

- `#saveStatus` : message textuel, `role="status"` et `aria-live="polite"`. Le même composant rejoint le menu ou le dock selon le parcours ; il reste dans leur flux, avec fond lisible, sans recouvrir le plateau ni les commandes.
- `#manageSave` ouvre les actions de récupération ; `#exportProgress` permet d'exporter la progression actuelle en mémoire quand une écriture a échoué. Ce dernier fichier est distinct de la copie brute de la dernière sauvegarde et ne doit pas la remplacer silencieusement.
- `#saveRecovery` et `#saveRecoveryMessage` : explication et actions de récupération, avec contenu pouvant défiler sur une faible hauteur. Le texte indique que l'ancienne sauvegarde est encore protégée.
- `#exportSave` : télécharger le contenu brut exact dans un fichier texte, sans tenter de l'interpréter ou le reformater.
- `#backupConfirmed` : case `J’ai conservé une copie de cette sauvegarde`.
- `#recoverSave` : action de création d'un nouveau profil, indisponible avant les préconditions de récupération. Son effet est soumis à une confirmation finale explicite.
- `#recoveryCancel` : quitter la récupération sans remplacer la sauvegarde principale.

Le texte et les états suffisent à distinguer succès et erreur ; la couleur seule ne porte pas l'information. Le Pixel Artist vérifie le contraste et les rectangles sur petit écran sans créer de ressources graphiques.

## Récupération sans perte silencieuse

Une valeur absente, une valeur invalide et un stockage inaccessible sont trois états différents. En particulier, un échec de lecture ou de validation ne doit pas entraîner un nouveau profil automatique suivi d'une sauvegarde qui écraserait l'ancienne valeur.

Pour une valeur brute accessible, la réinitialisation exige un export déclenché, la confirmation par la case, puis une confirmation finale des conséquences. L'export seul n'est pas une preuve que le joueur a effectivement reçu le fichier. Une **copie locale distincte**, sous la clé de sauvegarde suffixée par `-backup`, doit donc être écrite et relue avec égalité exacte avant de remplacer la valeur principale. Si cette copie ou sa relecture échoue, l'ancienne valeur principale reste intacte et la récupération explique l'échec. La case ne permet pas de contourner cette protection.

L'annulation avant ou lors de la confirmation conserve le contenu principal verbatim. Quand l'accès lui-même est refusé, désactiver export et réinitialisation plutôt que prétendre sauvegarder un contenu qui n'a pas pu être lu. Une version inconnue suit les mêmes garanties que les données invalides ; elle n'est pas convertie implicitement en format 38.

Quand l'enveloppe de profil 38 est valide et que seule la tentative est inutilisable, la récupération privilégiée ne doit pas effacer les acquis récupérables. Expliquer **Nouvelle tentative — progression conservée**, avec la même copie brute et le même consentement. Après récupération, étoiles, paliers, record et complétion restent identiques, tandis que la tentative repart au terrain 1, vague 0. Si la version ou ces acquis sont eux-mêmes invalides, ne pas deviner leurs valeurs : conserver l'original et limiter l'action à un profil neuf explicitement accepté.

## Nouveau profil, fin et nouvelle tentative

Le bouton du menu nommé **Nouveau profil** se distingue des commandes **Nouvelle tentative** déjà présentes après une fin de tentative ou dans l'atelier. Le profil neuf efface volontairement les étoiles, les pouvoirs permanents, le record et la tentative : ces quatre conséquences sont nommées dans sa confirmation lorsqu'une sauvegarde existe. Annuler ne change rien aux données.

Le bouton précédemment nommé « Recommencer » dans le jeu doit annoncer **Terminer la tentative**, afin de ne pas confondre cette fin avec un effacement de profil. La récompense légitime est alors calculée une seule fois ; Nouvelle tentative conserve ensuite les acquis permanents. Aucun nouvel écran de navigation n'est nécessaire pour cette distinction.

## Reprise de session

Un combat sauvegardé en pause reste en pause après Continuer et après un rechargement. Les vitesses ×1, ×2 et ×3 restent celles de la sauvegarde ; une ancienne sauvegarde 38 sans vitesse utilise ×1 sans modifier les acquis. La pause conserve son indicateur et son nom d'action de reprise.

Un reçu ancien déjà payé peut être affiché, puis rechargé ou suivi de l'atelier, sans second versement ni retrait de gains historiques. Le choix d'un pouvoir ou d'une reprise ne justifie pas un remplacement silencieux de l'état sauvegardé.

## Vérifications navigateur durables

`tests/test_l1_browser.py` ajoute des parcours sur la page réelle, avec serveur lié à `127.0.0.1` sur un port libre et contextes Chromium jetables. Les états sont dérivés de la fixture synthétique commune `tests/fixtures/save-v38.json`. Aucun helper ou fixture existant n'est modifié par l'UX.

La suite vérifie : absence de sauvegarde ; JSON et structure invalides ; version inconnue ; conservation exacte du contenu ; export texte exact ; annulations ; copie locale avant remplacement ; récupération d'une tentative invalide avec acquis 38 valides ; absence d'acquis devinés depuis une version inconnue ; refus de remplacement si la copie échoue ; refus de lecture initial ou survenant après reprise ; écritures refusées et quota simulé avec export de l'état en mémoire ; pause avec les trois vitesses ; sauvegarde ancienne sans vitesse ; reçu ancien et atelier après rechargement ; distinction Nouveau profil/Nouvelle tentative et conservation des acquis.

Les défaillances de stockage sont injectées dans le seul profil de test. Elles ne démontrent ni saturation réelle d'un téléphone, ni corruption spontanée, ni compatibilité Safari. La suite échoue sur une erreur JavaScript de page ou sur un refus de lancer le navigateur ; ces cas ne sont pas déclarés validés.

## Résultats exécutés le 18 novembre 2026

Commande :

```sh
python -B -m unittest discover -s tests -p 'test_l1_browser.py' -v
```

**13 tests réussis en 35,955 s**, avec Chromium `156.0.8078.79` headless, aux dimensions 390 × 844 pixels CSS et avec tactile émulé. Aucune erreur JavaScript de page n'a été relevée. Les contextes, le serveur local sur port libre et les téléchargements de test sont isolés des données d'un joueur.

| Parcours vérifié | Résultat observé |
| --- | --- |
| Absence de sauvegarde | Message d'absence, Continuer désactivé, création d'un profil 38 possible. Aucun faux message de sauvegarde déjà enregistrée. |
| JSON invalide, structure invalide, version 99 | Continuer désactivé, message visible, ouverture puis annulation de récupération et rechargement sans remplacement de la valeur brute. |
| Réinitialisation explicite après données invalides | Export UTF-8 exactement identique au contenu brut ; confirmation, copie locale vérifiée et création d'un nouveau profil. |
| Annulation de la confirmation finale | Valeur principale inchangée verbatim. |
| Tentative invalide avec profil 38 valide | Copie brute conservée ; nouvelle tentative terrain 1, vague 0 ; 73 étoiles, paliers, record 48 et complétion de la fixture conservés, y compris après rechargement. |
| Version inconnue après consentement à un profil neuf | Original sauvegardé séparément ; aucun acquis deviné depuis la version 99 ; profil neuf 38. |
| Copie locale refusée par quota simulé | Réinitialisation refusée, données principales intactes et récupération toujours visible. |
| Lecture du stockage refusée | Message visible, Continuer désactivé, aucun remplacement ; export/récupération inopérants sur un contenu inaccessible. |
| Lecture devenue impossible après reprise | Nouveau contrôle ciblé : message visible, dernière valeur principale inchangée et export de la progression en mémoire avec les acquis et la vitesse actuelle. |
| Écriture refusée ou quota simulé en jeu | Avertissement visible sans nom d'exception technique ; dernière sauvegarde conservée ; export JSON de l'état en mémoire avec les acquis et la vitesse actuelle. |
| Combat en pause à ×1, ×2, ×3 | Pause et vitesse conservées après Continuer puis rechargement ; acquis permanents inchangés. |
| Ancienne sauvegarde sans vitesse | Pause conservée, valeur de repli ×1 et acquis conservés après rechargement. |
| Reçu historique et atelier | Affichage puis rechargements sans deuxième versement, ni retrait des étoiles historiquement acquises. |
| Nouveau profil et nouvelle tentative | Confirmation nommant les pertes, annulation sans changement ; Terminer la tentative puis Nouvelle tentative conserve les acquis et le gain légitime. |

Après extension du fichier à **14 tests**, le nouveau cas de refus de lecture après reprise a été exécuté séparément :

```sh
python -B tests/test_l1_browser.py ReliableProgressBrowserTests.test_read_failure_after_loading_allows_export_without_replacing_the_last_save -v
```

**Un test ciblé réussi en 2,678 s.** Les 13 tests initiaux et ce nouveau cas ne sont pas présentés comme une exécution unique de 14 tests ; l'intégration relance l'ensemble après les derniers changements de code.

Une exécution intégrée ultérieure a révélé une incohérence dans le scénario synthétique du reçu historique : la tentative était placée en vague 1, mais son checkpoint avait conservé la vague 2 de la fixture de base. La validation plus stricte a correctement refusé ce checkpoint situé dans le futur. Le test a été corrigé pour utiliser un checkpoint de préparation à la vague 0, conforme à une première vague commencée. Étoiles, reçu historique, record, paliers et assertions de conservation restent inchangés ; aucune garde de validation du jeu n'a été assouplie. La suite complète doit être relancée après les dernières gardes d'intégration.

Ces résultats sont ceux des contrôles UX ciblés. La validation des autres suites, des invariants du noyau et du SHA final relève de l'intégration du Développeur / QA et du coordinateur. La lisibilité à 300/320 px est examinée séparément par le Pixel Artist ; cette suite ne prétend pas couvrir un appareil réel, Safari/WebKit, un lecteur d'écran ou le paysage.
