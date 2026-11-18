# Mission 01 — analyse Game Designer

## Référence et méthode

- Jeu étudié : `main`, commit `0e14138bc42eefbfcb7dcef06be3f955d328292d`.
- Consignes lues : `AGENTS.md` et `docs/COLLABORATION.md` du commit `e882b2278c9dfc99a06be89ef025743de988d81b` de la PR d'organisation ; ces fichiers ne sont pas encore présents dans cette référence de `main`.
- Périmètre : diagnostic et recommandations seulement. `index.html` n'est pas modifié.
- Méthode exécutée : lecture du code, calcul des sept terrains avec les vraies fonctions extraites, reproduction logique de l'abandon anticipé et trois simulations déterministes de la **seule première vague** de la plaine. Aucun test humain, aucune campagne complète simulée, aucun taux de victoire représentatif.
- Les temps donnés ci-dessous sont des secondes de jeu simulées, pas une mesure de performance du navigateur.

## Les cinq améliorations prioritaires

| Ordre | ID | Amélioration | Impact | Confiance | Effort indicatif | Dépendances |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | GD-01 | Récompenser la progression réellement accomplie et isoler les outils de développement | Très élevé : protège toute l'économie permanente | Élevée, logique reproduite | S–M | Développeur/QA : récompenses et rechargement ; UX : explication de l'abandon |
| 2 | GD-02 | Établir une courbe de difficulté mesurée, en priorité au passage vers le Bastion | Très élevé : continuité des sept terrains | Élevée pour les écarts chiffrés ; moyenne pour leur effet humain | M–L | GD-01, fiabilité des reprises/sauvegardes, GD-03 |
| 3 | GD-03 | Construire un banc de simulation reproductible utilisant la logique réelle | Élevé : rend les réglages vérifiables | Élevée pour la faisabilité ; couverture encore réduite | M | Contrat de séparation du noyau avec Développeur/QA |
| 4 | GD-04 | Aligner les bonus annoncés, leurs calendriers et leurs effets réels | Élevé : décisions tactiques et budgets fiables | Élevée, lecture du code | S–M | UX/UI pour les textes ; QA pour les cas de contrôle |
| 5 | GD-05 | Rendre la progression permanente et les spécialisations des héros mesurables | Élevé : rejouabilité et variété des stratégies | Élevée pour les coûts ; moyenne pour le rythme souhaitable | M | GD-01, GD-03, UX/UI ; préserver les cinq identités |

S = changement local et contrôles ciblés ; M = plusieurs parcours et coordination ; L = campagne de mesure et itérations. Ce sont des tailles relatives, pas des délais garantis.

### GD-01 — Intégrité des récompenses avant tout équilibrage

**Preuve.** [`globalWaveCleared` et `rewardStars`, lignes 896–897](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L896-L897) comptent la vague en cours tant qu'il ne s'agit pas d'une défaite terminée avec zéro vie. [`mapsButton`, ligne 1013](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L1013) permet de quitter cette vague et d'appeler `finishRun(false, true)`.

Reproduction par les fonctions extraites : profil neuf, `begin(g)` sur la plaine puis `rewardStars(false, true)` sans exécuter `step` donnent `n=1`, un nouveau record et **6 étoiles**. Refaire le même début donne **5 étoiles**, sans finir une seule vague. Tous les paliers permanents coûtent `5 × (5 + 12 + 24) = 205` étoiles : **41 abandons au départ suffisent**, car `6 + 40 × 5 = 206`. Il s'agit du rendement en nombre de tentatives ; aucun temps réel de farm n'est mesuré ici. Le Développeur/QA a également confirmé l'abandon anticipé dans un navigateur de test.

Le bouton « Mode dev » est rendu dans la page et son [gestionnaire, lignes 1014–1023](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L1014-L1023), transforme le terrain courant en victoire, ajoute une reprise et passe par la progression normale. Ces parcours invalident une mesure de difficulté fondée sur les étoiles gagnées.

**Recommandation.** Distinguer vague lancée et vague terminée ; attribuer les records sur les vagues réellement franchies. Faire décider explicitement si une tentative sans vague terminée doit recevoir une compensation, et sur quel effort vérifiable elle repose. Préserver une récompense de défaite utile sans donner au lancement/abandon immédiat un rendement supérieur au jeu. Isoler les victoires de développement des sauvegardes et récompenses de progression normales. Dans un jeu local, il s'agit d'assurer la cohérence du parcours ordinaire, pas de prétendre empêcher toute modification de données par le joueur.

**Acceptation.** Un lancement suivi d'un abandon sans vague terminée ne crée ni record ni récompense de progression ; une vague réellement terminée est comptée une fois ; abandon, fin d'animation et rechargement ne doublent pas un gain ; un parcours de test ne débloque pas le hardcore sur le profil ordinaire. Le choix d'une compensation éventuelle reste à valider par l'utilisateur.

### GD-02 — Mesurer les transitions, avec un examen prioritaire du Bastion

**Preuve.** Les multiplicateurs sont superposés dans [`spawn`, lignes 594–612](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L594-L612), et non résumés par le seul `STAGE_SCALE`. Les tableaux plus bas mesurent leur effet réel. Du terrain 3 au terrain 4, les PV du premier ennemi normal augmentent de **123 %**, la route terrestre sans tours passe de **14 à 10 cases**, la distance aérienne de **10,30 à 7,07 cases**, des boucliers de **23 %** apparaissent sur certaines unités et le nombre d'ennemis de vague 1 passe de **16 à 18**. L'enveloppe théorique de Z du terrain augmente seulement de **10,1 %**. Même avec tous les paliers permanents au maximum, le multiplicateur de dégâts direct passe de `5,032` à `5,704`, soit **+13,4 %**.

Cela signale un risque de rupture, **pas une preuve que le terrain est impossible** : la carte, les zones, le gel, la disposition des tours et le déblocage immédiat de POY au terrain 4 changent les possibilités. L'armée, les Z et les bonus de terrain sont réinitialisés par [`startLevel`/`resetGame`/`initial`](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L1003) ; on ne finance pas ce saut avec l'armée accumulée au terrain précédent.

**Recommandation.** Mesurer chaque transition avec plusieurs niveaux de progression et politiques d'achat légales, puis choisir une cible de tension et d'apprentissage. Examiner d'abord le Bastion et l'introduction des boucliers, ensuite les fins de terrains 6–7. Séparer les effets de topologie, de PV, de cadence d'apparition et de budget avant de changer un coefficient. La correction des reprises reportées et de la pause, signalée par QA, précède la calibration pour éviter d'attribuer un défaut technique à la difficulté.

**Acceptation.** Rapport avant/après couvrant les sept terrains, profils neufs/intermédiaires/maximaux, stratégie mixte et stratégies spécialisées ; mêmes placements et politique d'achat pour une comparaison donnée ; PV, vies, reprises, budget, vague atteinte et causes de défaite tracés. Les objectifs de succès et l'effort de progression sont validés avant le réglage. Aucune nouvelle valeur de PV ou de revenu n'est déclarée validée par cette mission.

### GD-03 — Automatiser les parties sans réécrire les règles

**Preuve.** Le noyau de [`D` à `step`, lignes 453–704](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L453-L704) peut être évalué hors DOM ; seuls les retours audio/visuels appelés doivent être neutralisés dans un banc de mesure. Trois premières vagues légales ont été simulées ; le protocole et les résultats figurent plus bas. Cela prouve la faisabilité technique, pas la qualité d'un bot de campagne.

**Recommandation.** Après validation, exposer une interface du noyau pour `initial`, `buy`, `upgrade`, `remove`, `begin`, `choose`, `step` et les transitions. Conserver une unique implémentation des règles. Commencer par des scénarios fixes, puis comparer plusieurs politiques : labyrinthe terrestre, couverture aérienne, composition mixte, spécialisation et achat d'évolutions. Ajouter des traces rejouables : actions de préparation, ordre de ciblage, dépenses, bonus, vagues, boss, reprises et étoiles. Utiliser des graines lorsque des choix aléatoires sont introduits ; le noyau de combat extrait n'en utilise pas dans les scénarios présents.

**Acceptation.** Un même scénario et un même pas de temps redonnent le même résultat ; le bot passe par les API d'achats légaux ; aucune injection de Z, de dégâts ou de victoire ; les événements clés sont comparés à un scénario navigateur. Couvrir ensuite les 70 vagues, les boucliers/régénérations, les zones retardées, le hardcore et les sauvegardes. Les essais à `1/60` et `1/30` doivent expliciter les écarts : l'ordonnancement discret du ciblage et des tirs peut modifier le résultat. Les simulations ne remplacent pas une évaluation humaine de compréhension et de plaisir.

### GD-04 — Faire correspondre la décision affichée à la règle

**Preuve.** [`B`, lignes 518–527](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L518-L527), conserve les libellés historiques `wave:5/10/15`, mais `bonusOptions` les traduit en choix après les vagues **3/6/9**. `wavePay` applique « Cagnotte des potes » aux vagues **4–6** et « La grosse prime » aux vagues **7–9**, alors que les descriptions annoncent **6–10** et **11–15**. Le jeu s'arrête à la vague 10 par terrain : le second texte désigne donc des vagues inexistantes dans ce contexte. Les bonus de héros qualifiés de « permanents » sont stockés dans `g.perks`, réinitialisé au terrain suivant ; cela se distingue des achats en étoiles.

Le bonus « Hiver nucléaire » annonce une cible voisine. `stats` ajoute bien puissance et durée du gel avec `has(g, 'jordan')`, mais [`attack`, lignes 678–682](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L678-L682) réserve la cible supplémentaire au palier permanent `ml>=1`, sans condition propre au bonus de tentative. Il existe donc un décalage précis entre promesse et exécution. Autre point à expliciter, sans en déduire un défaut de calcul : le palier permanent « Double explosion » affiche `×2` ondes, et l'onde différée utilise `0,34 × dégâts` avant armure/règles de zone. Ce texte ne doit pas être reformulé en promesse d'un doublement général des dégâts.

**Recommandation.** Utiliser des données communes pour calendrier, durée, montant et périmètre d'effet. Pour la première correction, aligner les textes sur les règles réelles ; un changement des effets nécessite sa propre décision d'équilibrage. Distinguer « jusqu'à la fin de ce terrain » et « acquis en étoiles pour les prochaines tentatives ». Ne pas transformer silencieusement une correction rédactionnelle en buff.

**Acceptation.** Un test de budget vérifie exactement trois versements pour chaque bonus économique ; aucun écran ne promet des vagues 11–15 ; les cibles supplémentaires sont justifiées par l'effet effectivement possédé ; le joueur peut distinguer une amélioration de tour, un boost de terrain et un palier permanent. Toutes les valeurs affichées sont rapprochées des mêmes scénarios de référence.

### GD-05 — Rendre le rythme roguelite et les cinq spécialisations vérifiables

**Preuve.** Chaque héros demande **41 étoiles** pour les trois paliers (`5+12+24`). Le premier achèvement complet de campagne donne **36 étoiles** si c'est un nouveau record, puis **34** sans nouveau record ; les étoiles ne sont attribuées qu'à la fin de la tentative, pas après chaque terrain. Hors faille GD-01, cela ne permet pas à lui seul de déduire la durée de progression : les défaites, abandons et décisions d'achat comptent. Les paliers ajoutent à la fois des capacités et un multiplicateur global de dégâts dépendant du terrain, visible dans [`ascensionPower`, ligne 570](https://github.com/Vegetom/friends-defense/blob/0e14138bc42eefbfcb7dcef06be3f955d328292d/index.html#L570). Par exemple le palier I multiplie déjà les dégâts directs par **1,525** en plaine, en plus de sa capacité annoncée. Les fiches de pouvoirs mettent surtout en avant la capacité, ce qui rend cette hausse difficile à anticiper.

Le DPS direct n'évalue pas à lui seul Tom contre rapides, le marquage/railgun de Raphaël, les zones d'Ylvine, le contrôle de Jordan ou la portée/puissance de POY. Le tableau de coûts ci-dessous sert de point de départ et n'établit aucune dominance.

**Recommandation.** Définir avec l'utilisateur un rythme cible en tentatives significatives pour le premier achat, un premier héros complet et une composition viable sur chacun des sept terrains. Expliquer les gains directs des paliers en plus des capacités. Mesurer le coût d'opportunité de monter un héros plutôt que diversifier ; comparer des portefeuilles d'étoiles de coût égal, plutôt qu'opposer seulement « rien » et « tout au maximum ». Préserver les cinq noms, rôles et silhouettes ; ne pas homogénéiser tous les DPS pour obtenir artificiellement une égalité.

**Acceptation.** Matrice de progression à coût égal, avec montants dépensés et gains par tentative ; chaque héros contribue à au moins un scénario expliqué ; aucune conclusion de dominance fondée sur le seul DPS. Le temps d'acquisition est mesuré après correction GD-01 et documenté séparément en temps simulé, temps d'interaction et retours humains. Les nouveaux prix/pouvoirs éventuels restent à valider.

## Courbe chiffrée des sept terrains

Les valeurs suivantes proviennent des fonctions du jeu, sans modifier leurs coefficients. Les routes sont calculées **sans tours** ; la distance aérienne est la ligne droite entre entrée et sortie, en cases de 60 pixels du Canvas, sans rapport direct avec la taille tactile affichée.

| Terrain | Grille | Route terrestre nue | Distance aérienne | Z initiaux | PV premier normal V1 | PV boss V5 | PV boss V10 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 — La plaine | 10 × 8 | 9 | 9,00 | 150 | 34,00 | 1 461 | 9 281 |
| 2 — La mare | 10 × 8 | 11 | 9,00 | 180 | 81,15 | 3 149 | 13 962 |
| 3 — Les deux forteresses | 10 × 8 | 14 | 10,30 | 200 | 175,11 | 6 843 | 30 851 |
| 4 — Le bastion | 6 × 6 | 10 | 7,07 | 215 | 390,70 | 15 375 | 70 451 |
| 5 — Le Défilé | 12 × 10 | 13 | 11,00 | 260 | 549,41 | 18 506 | 86 139 |
| 6 — L'Archipel | 13 × 10 | 15 | 12,04 | 300 | 731,14 | 21 588 | 102 035 |
| 7 — La Couronne | 14 × 11 | 17 | 13,00 | 340 | 929,21 | 25 385 | 121 776 |

PV du corps seulement ; les boucliers, l'armure et la régénération ne sont pas compris dans ces colonnes. Mode normal. Les boss hardcore finaux sont deux, avec coefficients spécifiques ; ils doivent faire l'objet d'un scénario séparé.

| Terrain | Ennemis V1 / V10 | Intervalle d'apparition V10 | Facteur de revenu de base | Éliminations sur 10 vagues | Primes sur 10 vagues | Enveloppe Z du terrain | Multiplicateur direct permanent I / III |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 14 / 33 | 0,470 s | 1,0000 | 1 055 | 790 | 1 995 | 1,525 / 3,688 |
| 2 | 14 / 33 | 0,470 s | 1,1076 | 1 085 | 873 | 2 138 | 1,656 / 4,360 |
| 3 | 16 / 35 | 0,452 s | 1,2204 | 1 517 | 963 | 2 680 | 1,788 / 5,032 |
| 4 | 18 / 37 | 0,434 s | 1,3384 | 1 679 | 1 058 | 2 952 | 1,919 / 5,704 |
| 5 | 20 / 39 | 0,416 s | 1,4742 | 2 112 | 1 164 | 3 536 | 2,050 / 6,376 |
| 6 | 22 / 41 | 0,398 s | 1,6165 | 2 376 | 1 278 | 3 954 | 2,181 / 7,048 |
| 7 | 24 / 43 | 0,380 s | 1,7792 | 2 890 | 1 405 | 4 635 | 2,250 / 7,400 |

L'enveloppe est `Z initiaux + toutes éliminations + toutes primes`, **sans bonus économiques et sans fuite**. Elle inclut la prime de vague 10 reçue après le combat final ; ce n'est donc pas intégralement un budget disponible pour gagner ce combat. Les récompenses sont arrondies unité par unité comme dans `step`. Les élites font croître les revenus aux terrains avancés ; le facteur de revenu seul ne suffit pas à les expliquer. Les Z/armées ne sont pas reportés au terrain suivant.

Le calendrier aérien est identique : vagues mixtes **4, 6, 8, 10**, vagues aériennes hors boss **7 et 9**, portée réduite à **68 %**. Les boss restent terrestres. Les élites et la régénération terrestre commencent au terrain 3, les boucliers au terrain 4, les accélérations sous seuil de PV aux terrains 5–7. Le boss final qui s'échappe met directement les vies à zéro. La multiplication des couches de pression exige une mesure par cause de fuite, pas seulement une moyenne de PV.

À titre de comparaison statique, la somme `PV/(1-armure) + bouclier` à l'apparition de toutes les unités, sans régénération ni sur-dégâts, passe d'environ **335 417** au terrain 3 à **928 928** au terrain 4 (**×2,77**). Ce budget de dégâts est un indicateur diagnostique ; il n'inclut ni exposition au feu, ni zones multiples, ni gel, ni régénération des boucliers et ne prédit pas à lui seul une victoire.

### Coûts et DPS directs de référence

Sans paliers permanents, sans boosts, sans armure ni interactions, avec une cible normale toujours à portée :

| Héros | Coût cumulé forme I / II / III en Z | DPS direct forme I / II / III |
| --- | --- | --- |
| Tom | 35 / 85 / 155 | 20,00 / 37,00 / 68,00 |
| Raphaël | 65 / 155 / 450 | 24,24 / 51,61 / 165,22 |
| Ylvine | 155 / 365 / 660 | 80,95 / 157,14 / 366,67 |
| Jordan | 155 / 365 / 660 | 52,38 / 104,76 / 195,24 |
| POY | 690 / 1 640 / 2 990 | 477,27 / 1 090,91 / 2 727,27 |

En plaine, Ylvine/Jordan sont disponibles après la vague 3 et POY après la vague 7 ; aux terrains 2–3 POY arrive après la vague 4 ; au terrain 4 tous sont disponibles dès la préparation. La plaine ne permet donc pas d'acheter POY pour sa première vague entièrement aérienne, la vague 7. Cela ne démontre pas un défaut : tous les héros ciblent les volants, avec couverture réduite. C'est un scénario pédagogique et de placement à mesurer.

## Simulations de faisabilité réellement exécutées

Noyau extrait du fichier étudié, `dt=1/60`, aucune graine nécessaire, mode normal, plaine vague 1. Deux Tom aux cellules `31` et `33`, un Raphaël à `35` ; indices de grille à partir de zéro, achat via `buy`, **135 Z dépensés sur 150**, aucun achat ultérieur, aucun choix de bonus, aucune reprise. Le pas de temps est fixe ; le seul code neutralisé est le feedback sonore/visuel appelé par le noyau.

| Profil permanent Tom/Raphaël/Ylvine/Jordan/POY | Coût du profil en étoiles | Temps simulé de vague | Ennemis éliminés / échappés | Vies finales | Z finaux |
| --- | --- | --- | --- | --- | --- |
| `[0,0,0,0,0]` | 0 | 13,933 s | 14 / 0 | 15 | 97 |
| `[1,1,0,0,0]` | 10 | 9,867 s | 14 / 0 | 15 | 97 |
| `[3,3,3,3,3]` | 205 | 9,150 s | 14 / 0 | 15 | 97 |

Ce sont trois scénarios déterministes d'une vague introductive, pas trois échantillons d'un taux de victoire. L'arrivée progressive des ennemis limite le gain de temps des profils très puissants. Cette mesure ne valide ni les terrains suivants, ni la difficulté réelle, ni les timings de rendu/tactile, ni la sauvegarde dans un navigateur. Un bot de campagne avec décisions d'achat reste à construire et à comparer à des parties humaines.

### Reproduire calculs, récompenses et sondes sans modifier le jeu

Exécuter depuis la racine du dépôt étudié avec Node.js. Le programme évalue des extraits en mémoire et écrit seulement sur la sortie standard ; il n'altère pas `index.html`. Vérifier d'abord que le fichier correspond au commit de référence (`git diff 0e14138 -- index.html` vide). L'extraction par marqueurs sert au diagnostic de cette révision ; elle n'est pas l'architecture durable recommandée.

```sh
node <<'JS'
const fs = require('fs'), vm = require('vm');
const source = fs.readFileSync('index.html', 'utf8');
const start = source.indexOf('const D=['), end = source.indexOf('const GRAPHICS=');
if (start < 0 || end <= start) throw Error('Marqueurs de noyau absents');
const core = source.slice(start, end);
const rewards = source.split('\n').filter(line =>
  line.startsWith('function globalWaveCleared(') ||
  line.startsWith('function rewardStars(')).join('\n');
const prelude = `
let metaLevels=[0,0,0,0,0], clock=0, runHearts=0, buildCheckpoint=null;
let stars=0, bestWave=0, completed=false, g=null, shake=0;
const settings={effects:false};
const playSound=()=>{}, damageFeedback=()=>{}, tickFeedback=()=>{};
const deathFeedback=()=>{}, heartDropFeedback=()=>{}, waveFeedback=()=>{};
const saveMeta=()=>{};
`;
const experiment = `
for (let lev=0;lev<7;lev++) {
  configureMap(lev); metaLevels=[0,0,0,0,0]; g=initial();
  const initialZ=g.money, route=g.route.length-1, air=airLength()/S;
  let kills=0, pay=0, hp1, b5, b10, n1, n10;
  for (let w=1;w<=10;w++) {
    g=initial(); g.wave=w-1; begin(g);
    while(g.spawned<g.total) spawn(g);
    kills+=g.enemies.reduce((sum,e)=>sum+
      Math.round(e.reward*(1+lev*.065)*ECON_STAGE[lev]),0);
    pay+=wavePay(g,w);
    if(w===1) {hp1=g.enemies[0].hp; n1=g.total;}
    if(w===5) b5=g.enemies.find(e=>e.boss).hp;
    if(w===10) {b10=g.enemies.find(e=>e.boss).hp; n10=g.total;}
  }
  console.log({terrain:lev+1,route,air,initialZ,hp1,b5,b10,n1,n10,
    kills,pay,envelope:initialZ+kills+pay});
}
configureMap(0); g=initial(); stars=0; bestWave=0; begin(g);
console.log('Abandon anticipé initial',rewardStars(false,true));
g=initial(); begin(g);
console.log('Abandon anticipé répété',rewardStars(false,true));
for(const profile of [[0,0,0,0,0],[1,1,0,0,0],[3,3,3,3,3]]) {
  configureMap(0); metaLevels=profile; g=initial(); clock=0;
  for(const [cell,type] of [[31,0],[33,0],[35,1]])
    if(!buy(g,cell,type)) throw Error('Achat illégal');
  begin(g); let frames=0;
  while(g.active && frames<36000) {step(g,1/60); clock+=1/60; frames++;}
  if(g.active) throw Error('Temps limite dépassé');
  console.log({profile,seconds:frames/60,killed:g.killed,
    escaped:g.escaped,life:g.life,money:g.money});
}
`;
vm.runInNewContext(prelude+core+'\n'+rewards+'\n'+experiment,
  {console}, {timeout:30000});
JS
```

## Coordination et limites de décision

Les corrections de récompenses et de reprises sont des prérequis de mesure partagés avec QA. Les corrections de textes peuvent avancer avec l'UX sans modifier les coefficients. Les ressources du Pixel Artist doivent garder les cinq héros et ne pas changer le moment d'application des dégâts sous couvert d'un nouveau timing d'animation.

La présente étude recommande une séquence : intégrité des parcours, protocole de simulation et de parties humaines, calibration des transitions, puis évolution des prix/pouvoirs selon les résultats. Elle ne propose ni nouveaux PV cibles ni refonte graphique à appliquer immédiatement. Les cinq recommandations sont soumises à validation avant implémentation.
