## High priority

* Permettre un autre type de caméra que /dev/video0 
  - Soit côté système (ex: caméra IP -> /dev/video0)
  - Soit côté opencv (ex: open("url_caméra_ip"))

* Possibiliter de choisir le modèle utiliser

* Afficher la version de trafficount dans le web

* Afficher l’exception pour l’initialision du client postgrest à côté du champ key

## Medium priority

* Si la ligne de franchissement est à 45°, le sens est indéterminé

* Les dossiers video_writer et configuration déclarés en volume dans le Dockerfile

* Dans la page counter.html, calculer les informations utiles
  - FPS
  - Durée entre deux détections

* Ajouter bouton pour rénitialiser le buffer et les compteurs totaux IN et OUT
  - À la place de la rénitialisition quand on active l’insertion dans la base
  - Sur le menu d’accueil index.html
  - Reset all button ?

* Comprendre le message « WARNING: not enough matching points »

* Comptage dans un polygone au lieu de toute l’image

* Permettre de modifier le nom du modèle utilisé et le format (YOLO11n, YOLO11s, PyTorch, NCNN 640p, etc.)

* Résolution de traitement
  - Détection les résolutions de la caméra
  - Permettre de modifier la résolution des images capturées par la caméra
  - Changer la résolution de traitement

* Insertion de l’appareil, du lieu ou de la résolution s’ils n’existent pas dans la base.

## Low priority

* Add new location (latitude, longitude and name ) in the web interface:
  - Use the location from the phone?
  - Enter fields manually

* Mode détection des voitures

* Web
  - Formulaire pour *tous* les paramètres du modèle (résolution de traitement, format du modèle)
  - Formulaire pour *tous* les paramètres de la BDD (tables, délai, URL, clé, taille du buffer)
  - Changere le taux de rafraichissement du live
  - Voir *toutes* les erreurs (erreur chargement modèle, erreur chargement BDD, erreur chargement caméra)

## Idées

* Faire l’inférence sur un thread séparé :
  - Accélérer le nombre d’images traité par seconde
  - Enlever le temps d’exécution du web et du client postgrest

* Tester la connection à la base séparément :
  - Lors de l’initialisation du client postgrest init_pgclient()
  - Différencier l’erreur d’insertion de l’erreur de connection

* Créer des exceptions customisées pour avoir le même message d’information pour un type d’erreur. 
  - Message à changer qu’à un seul endroits
  - Exemple :
    + NoIdFound() -> Pas d’id trouvé pour un appareil, un lieu ou une résolution
    + NoConnection() -> Pas de connection à la base
