Plan de développement du prototype

### 0.3.0 (En cours)

* Ajout des nombres de franchissement totaux IN et OUT sur l’images
* Option pour enregistrer les frames dans une vidéo
* Option pour activer ou désactiver les annotations
* Limitation de la taille du buffer pour l’historique du traking

### 0.2.1 (Format NCNN)

* Ajout de la persistance de la configuration
* Utilisation du modèle de données NCNN

### 0.2.0 (Mise à jour suivi)

* Base de données multi tables
* Ajout de deux modes opératoires sur la page d’accueil web : activation du compteur et activation de l’insertion dans la BDD
* Comptage par le franchissement d’une ligne (suivi)

### 0.1.1

* Fonctionner à la résolution maximale pour la caméra (opencv et inférence)

### 0.1.0 (Prototype)

* Interface web de contrôle

  * Ajout d’une template
  * Modifier quelques paramètres du client BDD et du counter sans vérifications
  * Voir l’état du client BDD et du counter
  * Visualiser les résultas live (image annotée, compteur, temps d’inférence)

### 0.0.1 (Avant prototype) OK

* Détection des personnes `model.predict()`

  * Configuration du modèle (CPU, classe des personnes, FPS)
  * Choix du format du modèle NCNN

* Traçage des personnes `model.track()`

* Comptage des personnes

* Serveur HTTP pour permettre de voir les métriques de comptage

* Client pour envoyer les métriques vers une base de données

* Faire fonctionner le projet dans un conteneur docker

* Portage du projet vers un Raspberry PI

  * Connectivité au réseau internet
