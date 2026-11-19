# Refonte des sprites ennemis

Référence `1ef008b`. L’ancien rendu utilisait un corps chibi vectoriel commun, un balancement global et des ailes ajoutées séparément. Les couleurs distinguaient les factions, mais la silhouette variait peu à l’échelle du plateau. Les boss utilisaient la même famille de formes.

La nouvelle planche comporte six silhouettes par terrain et quatre poses par silhouette. Les rapides portent une écharpe en mouvement, les tanks des épaulières et un masque, et les volants ont leurs propres battements d’ailes. Les boss de vague 5 et de vague 10 reçoivent une couronne ou une crête propre à leur faction. Le jeu conserve les noms des boss et la position réelle des ennemis. Les barres superposées montrent la vie et le bouclier. Le losange d’élite est placé à côté des barres pour éviter le chevauchement du visage. Les effets de marque, de gel et de régénération restent actifs.

Le rendu choisit la pose selon la progression ou l’horloge du combat. La pause immobilise les poses et la préférence système de mouvement réduit conserve la première pose. Le jeu utilise une seule planche intégrée de 54 690 octets en PNG, agrandie sans interpolation. Le fichier reste autonome.

Pour régénérer la planche avec Pillow :

```sh
python tools/art/enemy_atlas.py --embed index.html --output /tmp/enemy-atlas.png
```

Les scènes Chromium synthétiques couvrent les sept terrains, les familles d’ennemis, les deux variantes de boss et une vague de 30 ennemis avec pause et reprise. Le moteur, les récompenses, la sérialisation et les 52 images préexistantes sont identiques à la référence. Le validateur v38 donne les mêmes résultats sur le corpus de 1 252 états. Les contrôles et le déploiement sont consignés dans la PR.
