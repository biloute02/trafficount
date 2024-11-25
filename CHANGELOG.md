Plan de développement du prototype

### 0.3.0 (Mise à jour voiture)

* Détection des voitures ?

* Format du modèle alternatif NCNN

* Démarrage hors connexion lorsque le conteneur se crée pour la première fois

### 0.2.0 (Mise à jour suivi) en cours

* Activer le suivi grâce au tracker

* Interface web de contrôle suite

  * Régler tous les paramètres
    * du dispositif (id de l’appareil, lieu)
    * du modèle (FPS, résolution de traitement, format du modèles)
    * du postgres (table, délai, URL, clé, taille du buffer)
    * du web (taux de rafraichissement)
    * du suivi (ligne de franchissement)
  * Voir les erreurs
  * Marche / arrêt

* Utiliser la base de données multi tables avec id du dispositif, id du lieu et id de résolution

* Fonctionner à la résolution maximale pour la caméra (opencv et inférence)

* Fichier de configuration pour la persistence lors du redémarrage du conteneur
  à la place des variables d’environnement

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
