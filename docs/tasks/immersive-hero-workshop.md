# Atelier des héros plein écran

Référence `a07044a` (L3 déployé). Branche `feat/immersive-hero-workshop`. Le travail est limité à l’atelier, ses contrôles et sa présentation. Le combat, la campagne, les coûts, les effets et les données v38 restent la référence du jeu.

- `bd5095d` introduit le plein écran, les cinq portraits, les flèches, les onglets et la séparation entre aperçu et achat.
- `f36d26e` réemploie les trois silhouettes animées intégrées de chaque héros. La Base utilise la première silhouette. N1 la complète d’un motif pixel propre au héros. N2 et N3 reprennent les deux silhouettes transformées et leurs effets. Le rendu de l’atelier utilise une toile de 160 pixels, sans lissage, rafraîchie à chaque changement de pose. L’animation d’achat dure 480 ms et suit le réglage de mouvement réduit.
- La sélection et les aperçus résident en mémoire d’interface. L’achat appelle les mêmes données `META`, le même portefeuille et le même écrivain v38. La forme acquise est reconstruite depuis `metaLevels` au rechargement. Les contrôles de récupération restent accessibles dans l’atelier si le stockage est refusé.
- Les tests Chromium appuient sur les cinq portraits, comparent les vingt rendus, vérifient les refus, l’annulation, les octets de sauvegarde avant achat et la reprise après achat. Ils vérifient la géométrie et les cibles de 44 pixels CSS à cinq tailles mobiles.

Les limites de la validation et les résultats de publication sont consignés dans la PR.
