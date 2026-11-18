# L1 — vérification de la progression et des reprises

## Référence et périmètre

Implémentation préparée depuis `main` au commit `14361f3301c4ceaa6f4d5d12e689da15b16936c5`. Le Développeur / QA est l'unique intégrateur de `index.html` ; les spécialistes ont travaillé dans les fichiers réservés. Les décisions suivent [le contrat Game Designer](../design/l1-reliable-progress.md) et [le contrat UX](../ux/l1-reliable-progress.md).

L1 complète la correction des récompenses déjà livrée : checkpoints et cœurs, reprise pause/vitesse, validation et conservation des sauvegardes, feedback de stockage et distinction entre nouvelle tentative et nouveau profil. Aucun changement d'équilibrage, de héros, d'image, de son ou de format de sauvegarde n'est prévu.

Les clés normales restent `friends-defense-save-v38` et `friends-defense-settings-v15`, avec une version de sauvegarde `38`. Le profil activé explicitement par `?dev=1` conserve ses clés distinctes ; les copies de récupération utilisent aussi la clé du profil courant, suffixée par `-backup`.

## Comportements intégrés

### Checkpoint et cœurs

`resetGame()` affecte les cœurs reportés avant de capturer le checkpoint. Au premier combat d'un nouveau terrain, `g.retries`, `runHearts` et `buildCheckpoint.retries` partagent donc le même solde.

La reprise conserve la règle du checkpoint : elle restaure son budget, ses tours et ses vies, annule achats et gains de la vague perdue, et consomme exactement un cœur déjà présent avant cette vague. Un cœur gagné pendant le combat perdu ne peut pas financer sa propre reprise. Le commentaire historique contradictoire a été corrigé.

La réparation des anciennes données reste étroite : terrain supérieur au premier, checkpoint de vague zéro sans cœur, préparation de vague zéro ou première vague active/perdue, tentative non finalisée et accord entre les cœurs de `g` et `runHearts`. Les fins déjà récompensées et les vagues de boss ne sont pas rouvertes par un maximum global des soldes.

### Reprise de session

La vitesse est sauvegardée et restaurée à ×1, ×2 ou ×3. Une sauvegarde ancienne sans cette propriété reçoit ×1. La pause d'un combat actif est respectée ; le chargement ne passe plus par une fermeture d'atelier qui annule cette pause.

Une fin héritée encore à finaliser conserve la pause de son nouvel écran de récompense. Une tentative déjà finalisée dont l'écran avait été fermé entre deux écritures rouvre le reçu existant, ou l'atelier si aucun reçu n'est disponible, sans nouveau versement et sans demander d'effacer le profil.

### Validation et conservation

`validateSaveData(input)` est une fonction pure : elle retourne `{ok:true,data}` ou `{ok:false,error}` sans modifier la partie, le stockage ou son argument. Elle contrôle notamment les champs permanents, le terrain, le corps de partie, les tours, les entités, les listes et le checkpoint. Les chemins dérivés sont recalculés sur les données validées ; les clés dangereuses et positions de tours non canoniques sont refusées.

Les champs anciens optionnels reçoivent des valeurs de repli lorsque cela ne fabrique pas de progression. Les horloges et délais de tir négatifs produits naturellement par le noyau sont acceptés. Un état de récompense avec `g.active` et `runEnded` n'est pas rejeté. La complétion acquise n'est pas subordonnée à un record idéal : la fixture historique `completed=true`, `bestWave=48` reste valide.

Le validateur est appelé avant toute restauration et avant toute écriture. Une vague active exige ses compteurs présents et entiers, avec un total positif et un nombre d’ennemis apparus inférieur ou égal au total ; un champ manquant ne peut pas terminer automatiquement la vague. Une donnée rejetée, une version inconnue ou une lecture impossible bloque le remplacement automatique de la clé primaire. Le texte brut rejeté reste identique. Une erreur d'écriture n'arrête pas le combat et ne remplace pas la dernière sauvegarde valide ; le statut visible annonce que la progression n'est pas enregistrée.

La récupération est explicite : export brut, confirmation que le joueur a conservé une copie, confirmation de l'action, puis copie locale relue à l'identique avant remplacement. Si seule la tentative est endommagée et que les acquis permanents du format 38 sont valides, l'action proposée recommence une tentative en conservant étoiles, pouvoirs, record et complétion. Sinon, elle annonce clairement la création d'un nouveau profil. Aucune progression n'est devinée pour une version inconnue.

Une copie locale impossible, notamment par quota, empêche le remplacement. Si la copie a réussi mais que l'écriture du nouveau profil échoue, la donnée primaire reste conservée et le statut avertit que la partie courante n'est pas enregistrée. L'export de la progression en mémoire reste accessible après une erreur d'écriture ou une lecture devenue impossible pendant le jeu. Une absence de sauvegarde n'est pas présentée comme une sauvegarde réussie.

## Vérifications exécutées avant la revue intégrée

Environnement : Node 24.22.1 ; Python 3 avec Playwright disponible ; Chromium 156.0.8078.79 headless. Les serveurs HTTP locaux et contextes de navigateur sont temporaires et isolés. Aucune sauvegarde réelle de joueur n'a été utilisée.

| Vérification | Résultat constaté |
| --- | --- |
| `node tests/rewards.test.cjs` | 21 cas d'attribution existants réussis, dont syntaxe du script entier et véritable achèvement de la vague 1 |
| `node tests/save-validation.test.cjs` | 15 cas réussis : validation, phases héritées, données rejetées, checkpoint, budgets, réparation étroite et écriture réelle protégée |
| Corpus indépendant produit par le Game Designer depuis le noyau et le sérialiseur de `14361f3` | 1252 états acceptés, zéro faux rejet observé, y compris après le renforcement des checkpoints |
| `python -B -m unittest discover -s tests -p 'test_browser.py' -v` | Les 9 parcours historiques ont réussi dans une exécution intermédiaire de 27,784 s |
| `python -B -m unittest discover -s tests -p 'test_browser.py' -k legacy -v` | 3 tests ciblés réussis en 8,801 s après correction des écrans de fin hérités |
| `python -B -m unittest discover -s tests -p 'test_browser.py' -k carried_hearts -v` | Cas navigateur de report et deux reprises réussi en 7,123 s, sans argent ni étoile supplémentaire |
| Suite UX réservée `test_l1_browser.py` | 13 tests réussis en 35,955 s, puis le cas supplémentaire de lecture devenue impossible a réussi séparément ; 14 méthodes au total à intégrer à la découverte finale |

La découverte globale finale comporte onze méthodes dans `test_browser.py` et quatorze dans `test_l1_browser.py`. Le coordinateur exécute cette revue sur le code gelé, avec les deux commandes Node ; les résultats définitifs et le SHA livré sont consignés dans la fiche de mission et la PR. Les exécutions intermédiaires du tableau ne remplacent pas cette vérification finale.

Le test de reprise budgétaire utilise un checkpoint synthétique à 410 Z, 12 vies, Raphaël niveau 1 et deux cœurs. Après une défense modifiée et une perte, les reprises redonnent exactement 410 Z, 12 vies et la tour initiale, puis un et zéro cœur ; elles n'ajoutent ni remboursement supplémentaire ni étoile.

Les tests de stockage exécutent les fonctions réelles extraites du HTML. Ils vérifient qu'une structure mémoire invalide n'écrase pas une clé valide, que les textes invalides/inconnus restent inchangés, que le refus de lecture empêche l'écriture et qu'un quota laisse la clé précédente intacte. Les tests navigateur couvrent export, copie locale, confirmations, annulation, récupération des acquis et absence de double attribution.

Deux exemples compacts du corpus ancien sont conservés dans `tests/fixtures/` : effets/zones/impacts différés et volants/boss. Les budgets et préparations de vague ont été injectés pour couvrir les structures, tandis que les placements et combats utilisent les fonctions réelles. Ces fixtures et le corpus ne sont pas des campagnes gagnées. Voir [les commandes et précisions de test](../../tests/README.md).

## Limites

- Si un ancien état actif n'a plus de checkpoint, le jeu ne peut pas reconstruire son budget antérieur : il n'en fabrique pas un à partir de la vague courante. Les données permanentes restent conservées.
- Le téléchargement dépend du navigateur et du joueur ; l'interface ne prétend pas savoir si le fichier a été effectivement conservé. La copie locale vérifiée est une protection supplémentaire avant remplacement.
- Un stockage inaccessible peut empêcher la récupération jusqu'au rétablissement de son accès. Un quota qui empêche la copie de sécurité bloque le remplacement, en gardant le texte primaire intact.
- Il n'y a pas de validation Safari/WebKit, de téléphone réel, de lecteur d'écran, de campagne complète ou de benchmark de performance/mémoire dans cette vérification. Le lot L2, la calibration et les ressources graphiques restent distincts.

Les opérations Git, la fusion et le déploiement sont effectués par le coordinateur selon les contrôles du dépôt, pas par ce spécialiste.
