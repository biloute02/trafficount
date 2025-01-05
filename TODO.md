## High priority

* Activer le suivi sur un tronçon
  - Franchissement d’une ligne


## Medium priority


* Format du modèle alternatif NCNN

* Démarrage hors connexion lorsque le conteneur se crée pour la première fois :
  - Le modèle est téléchargé lors du premier démarrage du conteneur
  - Télécharger le modèle lors du `docker build`

* Fichier de configuration pour la persistence lors du redémarrage du conteneur
  à la place des variables d’environnement :
  - Génération du fichier avec des valeurs par défaut s’il n’existe pas
  - Écrasement du fichier pour toute modification de la configuration
  - Chargement du fichier au démarrage

* Comptage dans un polygone au lieu de toute l’image

* Déterminer la résolution maximale de la caméra et l’utiliser pour le traitement
  - Par défaut, `opencv` utilise la résolution (480,640)

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

* Les pages web results et live devraient être les mêmes :
  - La page live a un paramètre dans son header pour recharger la page automatiquement.

* Tester la connection à la base séparément :
  - Lors de l’initialisation du client postgrest init_pgclient()
  - Différencier l’erreur d’insertion de l’erreur de connection

* Créer des exceptions customisées pour avoir le même message d’information pour un type d’erreur. 
  - Message à changer qu’à un seul endroits
  - Exemple :
    + NoIdFound() -> Pas d’id trouvé pour un appareil, un lieu ou une résolution
    + NoConnection() -> Pas de connection à la base
