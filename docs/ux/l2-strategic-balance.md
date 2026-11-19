# L2 — compréhension des règles et de l'équilibrage stratégique

## Périmètre

Référence initiale : `34dc9a8cbd6d010ea125c460ee77624deaf6c4d6`, branche `feat/l2-strategic-balance`. `AGENTS.md` et `docs/COLLABORATION.md` ont été lus. La numérotation de cette mission suit la demande actuelle : L2 concerne le gameplay et les simulations ; la refonte d'interface et du paysage relève désormais de L5.

Le Game Designer définit les règles et leurs valeurs ; le Développeur / QA est seul à modifier le jeu et les tests. L'UX réserve ce document et des outils temporaires de lecture sous `/tmp`. Les cinq héros, les ressources graphiques, les sauvegardes et les parcours fiables issus de L1 restent à préserver.

Le rôle UX consiste ici à faire correspondre les promesses aux effets réels, à rendre les nouveaux traits compréhensibles avec peu de texte et à vérifier leur affichage. Ce rapport ne remplace ni une simulation de campagne ni une étude de compréhension auprès de joueurs.

## Promesses à corriger dans la référence de départ

| Source | Écart établi | Conséquence pour le contrat de contenu |
| --- | --- | --- |
| `B`, `bonusOptions`, `wavePay` | Les groupes définis avec les anciennes valeurs 5/10/15 sont effectivement proposés après 3/6/9 ; l'économie annoncée sur 6–10 ou 11–15 s'applique en réalité sur 4–6 ou 7–9. | Annoncer les vagues effectives, calculées depuis les mêmes données que l'application du bonus. Aucune promesse de vague 11–15 dans un terrain de dix vagues. |
| `B`, `initial`, `startLevel` | Des boosts portent la mention « Permanent », alors que les bonus du terrain sont effacés au changement de terrain. | Réserver « permanent » aux pouvoirs achetés avec les étoiles ; nommer les autres « bonus de terrain ». |
| `B`, `stats`, `attack` | Le bonus de Jordan annonce une cible voisine supplémentaire ; l'attaque de référence n'applique ce ciblage supplémentaire qu'à un palier permanent. | Le Game Designer tranche l'effet voulu avant que le texte annonce un nouveau pouvoir. Ne pas corriger la promesse sans contrôler le mécanisme. |
| `META`, `attack` | Ylvine II présente « ×2 » ; l'onde supplémentaire de référence inflige 34 % des dégâts, ce qui ne double pas le DPS. | Garder le nom Double explosion si souhaité, mais annoncer « +1 onde secondaire » plutôt qu'un doublement général des dégâts. |
| `META`, `attack` | Les tirs multiples de Tom visent des cibles distinctes ; les projectiles secondaires sont atténués dans la référence. | Ne pas faire lire « deux projectiles » comme « double dégâts sur un boss unique ». Le détail du pouvoir doit préciser la répartition. |
| `D`, `splash`, `hurt` | Les descriptions de Ylvine et POY annoncent un malus fixe de 20 % des dégâts indirects sur les élites ; la réduction réelle dépend des mécanismes d'armure et de zone. | Revalider le chiffre après les arbitrages GD et les tests ; aucun pourcentage ne reste dans le texte sans effet correspondant. |
| `wavePay` | Les montants économiques 35/60 sont ajoutés avant les multiplicateurs de terrain. | Afficher un montant réel calculé pour le terrain ou préciser « Z de base / vague » ; ne pas confondre coefficient de formule et revenu effectif. |

Ces écarts sont des constats de départ, pas une spécification qui impose de conserver les valeurs de la référence. Les valeurs finales seront celles du contrat GD vérifié dans le code intégré.

## Contrat court des bonus de terrain

Les choix sont proposés après les vagues **3, 6 et 9 terminées**. Une indication commune peut dire **« Un choix pour ce terrain. Les revenus ont leur propre durée. »** Les cartes de puissance portent **« Jusqu’à la fin du terrain »** ; une carte de revenu indique ses vagues et ses trois versements. Le dernier choix n'est pas présenté comme un pouvoir pour les six terrains suivants.

| Bonus existant | Formulation de durée à conserver, sous réserve des valeurs finales |
| --- | --- |
| Café serré — Tom | Cadence et portée indiquées ; jusqu'à la fin du terrain. |
| Double impact — Raphaël | Dégâts et largeur de rayon indiqués ; jusqu'à la fin du terrain. |
| Cagnotte des potes | Revenu par vague ; vagues 4 à 6, trois versements. |
| Colère du nain — Ylvine | Dégâts et rayon indiqués ; jusqu'à la fin du terrain. |
| Hiver nucléaire — Jordan | Ralentissement/durée et éventuelle cible secondaire selon la règle réellement retenue ; jusqu'à la fin du terrain. |
| La grosse prime | Revenu par vague ; vagues 7 à 9, trois versements. |
| Super série — POY | Cadence indiquée ; jusqu'à la fin du terrain. |
| Dernier rempart | Soin immédiat plafonné à 15 vies ; bonus contre les boss jusqu'à la fin du terrain. |
| L'appel de POY | Réduction du prix d'évolution indiquée ; jusqu'à la fin du terrain. |

Les identifiants persistés des bonus ne doivent pas être renommés pour une retouche de vocabulaire. La différence entre **évolution de tour achetée en Z pendant la préparation**, **bonus de terrain** et **pouvoir permanent acheté en étoiles** doit rester explicite.

## Traits, contre-mesures et arrivée au terrain 4

Privilégier une annonce courte dans les composants d'information existants, avec une explication détaillée dans les réglages. Les icônes et effets déjà présents complètent le texte : ils ne constituent pas seuls la description d'une règle. Aucun nouveau panneau, portrait ou système de couleurs n'est requis pour L2.

| Trait | Formulation courte de base | Condition de publication |
| --- | --- | --- |
| Armure / blindés | `Armure : réduit les dégâts reçus.` | Quantifier le pourcentage réel lorsque plusieurs catégories ont une résistance différente ; n'annoncer une pénétration d'armure que si elle est codée. |
| Volants | `Volants : trajet direct, portée réduite.` | Conserver le rappel du couloir aérien ; tous les héros ne sont pas implicitement privés de cible aérienne. |
| Régénération | `Régénération : récupèrent des PV.` | Préciser la valeur réelle et le contre retenu dans le détail ; un simple halo vert ne suffit pas à expliquer l'effet. |
| Bouclier | `Bouclier : absorbe les dégâts et peut se recharger.` | Ne pas écrire « seulement hors combat » si la recharge commence en réalité entre deux impacts. |

Une annonce quantitative de type **trait — valeur — contre-mesure** est préférable à une nouvelle liste d'icônes seules. Le contre doit être une action réelle : placement, concentration des tirs, contrôle, cadence, type d'attaque ou pouvoir défini dans le code. Il n'est pas nécessaire d'ajouter toutes les explications dans le nom du terrain ou de surcharger le HUD.

Le prérequis au Bastion fait partie de la demande actuelle : **une campagne sans pouvoir permanent ne doit pas franchir sa première vague**. Il doit résulter d'une mécanique annoncée, pas d'un test caché du profil qui déclarerait la défaite. Le candidat introduit donc un blindage d'impact à partir du terrain 4. À sa valeur intermédiaire de 90, les achats initiaux accessibles au profil sans pouvoir n'offrent pas d'impact suffisamment fort ; ce constat doit être vérifié par GD/QA sur les valeurs finales et les achats légaux, et non déduit d'un seul bot qui perd.

La formulation courte proposée est **« Blindage 90/impact : pouvoirs permanents adaptés nécessaires. Marquage, gel et feu offrent des contres. »** Le nombre doit être pris dans les données finales, sans recopier une constante de réglage dans plusieurs textes. Avant le terrain 4 et dans l'atelier, nommer des réponses accessibles : **Marquage de Raphaël I** et **Sol brûlant d'Ylvine I**. Le gel est une aide, pas une garantie suffisante à lui seul. « Adaptés » évite de promettre que tout premier achat de pouvoir débloquera ce terrain.

Pour le candidat examiné, distinguer le **blindage d'impact** d'une **réduction en pourcentage** et d'un **bouclier rechargeable** :

- Blindage : absorbe une quantité par impact avant les autres protections.
- Marquage : réduit ce blindage de 60 % ; gel : réduction supplémentaire de 20 %. À la valeur 90, cela donne respectivement 36, 72, ou 28,8 avec les deux effets. Ces valeurs sont des paramètres de candidat, à relire après les simulations finales.
- Feu continu : ignore le blindage d'impact, mais reste soumis aux boucliers et à la réduction en pourcentage. Ne pas le présenter comme une attaque ignorant toutes les protections.
- Un impact entièrement absorbé doit être expliqué par un feedback bref tel qu'**Absorbé**, réutilisant le système textuel existant et regroupé pour éviter une pluie de messages. Aucun nouveau sprite ou code de couleur n'est nécessaire.

Une ancienne sauvegarde dont les ennemis n'ont pas ce nouveau champ ne doit pas être durcie rétroactivement par le simple chargement. La description peut préciser que le blindage concerne les nouveaux ennemis du terrain. Les campagnes et vérifications doivent annoncer le profil de pouvoirs utilisé ; l'apport des pouvoirs permanents n'est pas masqué derrière un conseil vague de placement.

Les données de départ réelles doivent être identiques entre jeu et simulations : budget donné par `initial()`, pouvoirs effectivement acquis, déblocages et achats légaux. Une fixture destinée à lire une carte de bonus ou une description de trait reste explicitement un état synthétique de lecture ; elle ne compte pas comme une partie réussie, un départ équilibré ou une démonstration de viabilité.

## Vérification de lecture

Sur une copie stable du HTML intégré, utiliser Chromium isolé, sans sauvegarde réelle. Vérifier les cartes des trois choix de bonus, les traits et contre-mesures, les pouvoirs affichés, puis le retour après défaite vers l'atelier sans perte d'acquis. Contrôler que les montants, durées et conditions lus correspondent aux mécanismes retenus par GD/QA.

Pour la demande Samsung S22, documenter un viewport paysage **854 × 393 pixels CSS**, un facteur de pixels **3** et `is_mobile`/`has_touch` activés ; cela constitue une émulation de taille et de densité, pas un essai physique du téléphone ni de Safari. Relever les rectangles, retours à la ligne et éventuelles informations hors viewport. Les défauts de disposition existants seront distingués d'une régression du texte ; leur refonte reste L5.

Sur le HTML `9664436dc84afc68bda543f5016b351770f1ee73ff158fb4a3f8694b8125a32e`, Chromium 156 a chargé 24 contextes répartis entre les deux tailles. Les sept terrains, les trois choix de bonus, la transition vers le Bastion et le retour à l’atelier ont été vérifiés. Les six sélections de bonus ont fonctionné, le portefeuille synthétique est passé de 73 à 78 étoiles après récompense et est resté à 78 dans l’atelier. Aucune erreur de page.

L’avertissement avant le terrain 4, la mention 90/impact et les contres figurent dans les panneaux existants. Le paysage requiert toujours un défilement comme sur la référence L1. La revue vérifie l’affichage et les interactions, sans mesurer la compréhension auprès de joueurs.
