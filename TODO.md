## High priority

* Activer le suivi sur un tronçon
  - Franchissement d’une ligne

* Utiliser la base de données multi tables avec id du dispositif, id du lieu et id de résolution (Damien)

* Bouton marche / arrêt (comptage ou BDD ?)

## Medium priority

* Format du modèle alternatif NCNN

* Démarrage hors connexion lorsque le conteneur se crée pour la première fois
  - Le modèle est téléchargé lors du premier démarrage du conteneur
  - Télécharger le modèle lors du `docker build`

* Fichier de configuration pour la persistence lors du redémarrage du conteneur
  à la place des variables d’environnement

* Comptage dans un polygone au lieu de toute l’image

* Déterminer la résolution maximale de la caméra et l’utiliser pour le traitement
  - Par défaut, `opencv` utilise la résolution (480,640)

## Low priority

* Mode détection des voitures

* Web
  - Formulaire pour *tous* les paramètres du modèle (résolution de traitement, format du modèle)
  - Formulaire pour *tous* les paramètres de la BDD (tables, délai, URL, clé, taille du buffer)
  - Changere le taux de rafraichissement du live
  - Voir *toutes* les erreurs (erreur chargement modèle, erreur chargement BDD, erreur chargement caméra)
