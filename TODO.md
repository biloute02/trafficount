## High priority

* Activer le suivi sur un tronçon
  - Franchissement d’une ligne

* Utiliser la base de données multi tables avec id du dispositif, id du lieu et id de résolution (Damien)

* Gérer les erreurs si les résultas sont lus alors que le counter ne s’est pas encore lancé :
  - Derniers résultats
  - Dernière image annotée

## Medium priority

* Find a proper way to check if the database is online before trying insertion:
  - Exclude connection errors from the insert_dection_buffer function

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

## Low priority

* Add new location (latitude, longitude and name ) in the web interface :
  - Use the location from the phone?
  - Enter fields manually

* Mode détection des voitures

* Web
  - Formulaire pour *tous* les paramètres du modèle (résolution de traitement, format du modèle)
  - Formulaire pour *tous* les paramètres de la BDD (tables, délai, URL, clé, taille du buffer)
  - Changere le taux de rafraichissement du live
  - Voir *toutes* les erreurs (erreur chargement modèle, erreur chargement BDD, erreur chargement caméra)
