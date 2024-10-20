## Plan

Plan de développement du prototype

### v1

* Contrôle du raspberry pi (marche / arrêt)

### v0

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
  * Régler les performances (FPS, résolution, taille du modèle utilisé)
