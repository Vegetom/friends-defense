# L2 — représentation des traits et réemploi des ressources

## Périmètre

Référence de départ : `main`, commit `34dc9a8cbd6d010ea125c460ee77624deaf6c4d6`, branche `feat/l2-strategic-balance`. `AGENTS.md` et `docs/COLLABORATION.md` ont été lus.

Cette étape concerne le gameplay et l'équilibrage. La refonte artistique L4 et la disposition L5 ne sont pas anticipées ici : aucun nouveau dessin, réencodage global, changement de palette ou agrandissement supplémentaire de sprites n'est proposé à l'intégration de L2. Tom, Raphaël, Ylvine, Jordan et POY conservent leurs identités chibi anime, leurs formes et leurs ressources HD existantes.

Le Pixel Artist réserve ce rapport et ses fichiers temporaires. Le Développeur / QA reste seul intégrateur de `index.html` ; les propositions suivantes lui ont été transmises, ainsi qu'à l'UX/UI Designer.

## Inventaire utilisable sans nouvelle production artistique

L'inventaire de la référence contient **52 data URI d'images, 15 blocs SVG et deux blocs CSS**. Une empreinte SHA-256 individuelle et ordonnée de chaque image/SVG a été capturée avant les modifications, pour une comparaison ponctuelle à la fin de L2. Ces empreintes temporaires ne sont pas un test durable interdisant une future évolution artistique autorisée.

| Besoin de lecture | Ressource ou effet existant | Limite et règle de réemploi |
| --- | --- | --- |
| Tank / blindage | Plaques et silhouette `enemySprite(..., k=2, ...)` ; icône SVG `shield` de `perkIcons` | Les plaques désignent le tank, pas tous les ennemis ayant `armor>0`. Les élites ou boss blindés doivent donc être annoncés par un texte exact, sans leur donner arbitrairement une nouvelle silhouette. |
| Bouclier actif | Anneau conditionné par `e.maxShield>0 && e.shield>0` | Conserver le lien avec le bouclier réellement présent. Ne pas allumer en permanence un anneau qui ferait croire à une protection encore active après sa destruction. |
| Régénération | Lueur verte lorsque `e.regen && e.hp<e.max` | Une lueur seule ne communique ni la valeur ni une contre-mesure. La description doit préciser le taux et les conditions réelles ; ne pas promettre une interruption qui n'existe pas dans la logique. |
| Unités aériennes | Ailes `drawFlyer`, trajet aérien pointillé et flèches | Ces formes complètent la couleur ; conserver les indications de vagues mixtes/aériennes et de portée réduite. |
| Ralentissement / gel | Anneau et cristaux `frost` | Rendre le contrôle cohérent avec l'état `slow` et ses limites contre les boss, sans inventer un gel intégral si l'effet reste un ralentissement. |
| Marquage | Arcs dorés autour de la cible | Réutiliser seulement lorsqu'un marquage mécanique est réellement actif. |
| Feu et dégâts de zone | Zones `fire`, effets procéduraux et signatures existantes d'Ylvine / POY | Ne pas confondre une explosion décorative avec un effet persistant au sol ou un effet anti-régénération. |
| Annonce de trait et conseil | SVG existants `shield`, `target`, `snow`, `flame`, `bolt`, avec texte français | Les icônes ne remplacent pas la mention du trait, de sa valeur et du contre validé. Réemployer les mêmes formes, sans ajouter un nouveau fichier d'image. |

## Contrat de lisibilité transmis à UX et QA

1. Annoncer le trait avant la vague par un texte court fondé sur les données de combat : **trait — valeur — réponse tactique réellement implémentée**. Réserver les explications détaillées au panneau existant ; ne pas allonger sans limite la ligne de route.
2. Ne publier un conseil de contre-mesure qu'après sa validation par le Game Designer et son implémentation par QA. À la référence, le feu d'Ylvine ne suspend pas spécifiquement la régénération et Raphaël ne dispose pas d'un bonus propre aux boucliers : un effet visuel ne suffit pas à promettre ces propriétés.
3. Distinguer priorité de la cible et spectacle : les barres de vie, l'état du boss et les états mécaniques doivent rester lisibles face aux halos. Éviter d'empiler un nouveau badge, une nouvelle aura et une nouvelle ligne de texte sur chaque ennemi.
4. Employer d'abord les silhouettes, formes et libellés existants. Aucun changement de couleur de héros ou de faction n'est nécessaire pour cette mission. Toute nouvelle direction de palette ou de style doit être soumise avant application.
5. Vérifier les conditions exactes des formulations. Dans le code de départ, la recharge du bouclier dépend de la fin du flash d'impact, pas d'une véritable sortie du combat : le terme « hors combat » serait trompeur sans changement de mécanique correspondant.

Sur le HTML `9664436dc84afc68bda543f5016b351770f1ee73ff158fb4a3f8694b8125a32e`, les 52 images, 15 SVG et deux blocs CSS sont identiques à la référence, dans le même ordre. Quatorze états Chromium à 390 × 844 et 854 × 393 CSS (densité 3 pour le paysage) ont été capturés sans erreur JavaScript. Le texte « Absorbé » réemploie l’affichage des dégâts. Les anneaux de bouclier et effets de marquage, gel et feu conservent leur rôle. En paysage, le haut du plateau peut sortir de la vue après défilement, comme dans L1. Le contenu des réglages s’allonge d’environ 85 pixels CSS dans l’état Bastion mesuré, dans le panneau défilant existant.
