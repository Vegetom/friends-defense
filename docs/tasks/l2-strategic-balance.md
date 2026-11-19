# L2 — gameplay et équilibrage stratégique

- Demande : améliorer le jeu réel, puis livrer un lot testé et déployé. La numérotation actuelle de l'utilisateur remplace celle de la mission 01 : L2 concerne le gameplay ; L3 les évolutions, L4 l'art et L5 l'interface mobile.
- Référence : `34dc9a8cbd6d010ea125c460ee77624deaf6c4d6`, dernier `main` après L1. Branche : `feat/l2-strategic-balance`.
- Coordinateur : agent principal, seul responsable des opérations Git et de la livraison. Intégrateur unique de `index.html` : Développeur/QA.
- État : implémenté et vérifié.

## Critères et protection des acquis

Conserver les sept terrains de dix vagues, les cinq héros et les pouvoirs V3.8 déjà fonctionnels. Rendre le début accessible, mesurer une progression entre profils zéro, quelques achats, intermédiaire et maximum, et vérifier plusieurs compositions avec achats, revenus, bonus, reprises et transitions réels. Le profil sans aucun pouvoir permanent doit être incapable de terminer la première vague du quatrième terrain, y compris avec des achats intelligents ; une simple défaite de bot ne démontre pas ce critère universel.

Les simulations doivent utiliser le combat du jeu, aller jusqu'à la victoire ou la défaite réelle, et publier leurs limites. Aucun ajout de Z, de vies ou de victoire n'est autorisé dans les campagnes de référence. Une fixture synthétique de test ciblé est explicitement distincte d'une campagne.

Conserver clés et version v38, étoiles, pouvoirs, records, complétion, checkpoints, cœurs, pause/vitesse et séparation développeur. Les nouvelles caractéristiques ennemies restent facultatives pour les sauvegardes antérieures ; ne pas recalculer rétroactivement leurs PV, investissements ou boucliers. Aucun effacement de sauvegarde joueur.

## Réservations parallèles

| Responsable | Fichiers réservés | Dépendances |
| --- | --- | --- |
| Game Designer | `tools/simulations/`, `docs/design/l2-strategic-balance.md`, `docs/simulations/` | Référence figée avant ; code intégré après ; recommandations au QA |
| UX/UI Designer | `docs/ux/l2-strategic-balance.md` | Règles réelles pour les libellés et contre-mesures ; émulation mobile |
| Pixel Artist | `docs/art/l2-strategic-balance.md` | Réemploi des effets existants et vérification des ressources, sans refonte L4 |
| Développeur/QA | `index.html`, `tests/`, `docs/qa/l2-strategic-balance.md` | Intégration séquentielle des règles et contenus retenus |
| Coordinateur | Cette fiche, Git/PR/fusion/Pages | Contrôles, revue indépendante et SHA exact avant fusion |

## Contrats intégrés

Les premières vagues gardent leur courbe. Les dernières vagues de la Plaine sont allégées. Les terrains avancés donnent plus de Z et les boss y ont moins de PV. Le blindage par impact à partir du Bastion introduit des contres par marquage, gel et feu. Le joueur en est averti dans l’atelier, avant le changement de terrain et à l’entrée du Bastion. Les bonus conservent leurs identifiants et leurs effets, et indiquent leurs durées réelles.

## Validation

HTML testé `9664436dc84afc68bda543f5016b351770f1ee73ff158fb4a3f8694b8125a32e`.

- Node : 21 cas de récompense, 15 de sauvegarde, 8 de gameplay. Chromium : 28 cas, dont blocage réel et retour « Absorbé », sauvegarde en pause, reprise et avertissement avant le Bastion.
- Comparaison indépendante de 1 252 états historiques : résultats du validateur identiques à L1 sur l’intégralité des états.
- Inventaire : 52 images, 15 SVG et deux blocs CSS identiques à la référence.
- UX : 24 contextes mobiles, six choix de bonus acceptés et aucune erreur JavaScript. Voir la [revue UX](../ux/l2-strategic-balance.md) et la [revue des ressources](../art/l2-strategic-balance.md).
- Équilibrage : voir le [comparatif reproductible](../design/l2-strategic-balance.md). Les quatre compositions de référence terminent la campagne avec tous les pouvoirs. Les simulations au profil zéro s’arrêtent avant la fin du premier terrain.

La vérification de GitHub Pages et du chargement public est consignée dans la PR. Les essais mobiles utilisent Chromium et des tailles émulées. Les limites de défilement en paysage relèvent de L5. Aucun essai sous Safari ni sur téléphone physique n’a été exécuté.
