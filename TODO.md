## High priority

* Ajouter la date d’insertion et le nombre d’éléments insérés dans le web

* Fichier de configuration pour la persistence lors du redémarrage du conteneur
  - Renplace les variables d’environnement
  - Sauvegarde du fichier avec un bouton dans la page web d’accueil
  - Chargement du fichier au démarrage et avec un bouton dans la page web d’accueil

## Medium priority

* Boutons de rénitialisation pour les comptages totaux du franchissement de la ligne in et out (?)

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
