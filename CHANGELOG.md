Plan de développement du prototype

### 0.2.0 (?)

* Détection des voitures ?

* Tracking effectif

  * Configuration du tracker

* Sens de détection ?

### 0.1.0 (Prototype) En cours

* Démarrage hors connexion

* Format du modèle alternatif NCNN

* Interface web de contrôle

  * Marche / arrêt
  * Régler les paramètres
    * du dispositif (id de l’appareil, lieu)
    * du modèle (FPS, résolution de traitement, format du modèles)
    * du postgres (table, délai, URL, clé, taille du buffer)
    * du web (taux de rafraichissement)
  * Visualiser les résultas live (image annotée, compteur, temps d’inférence)
  * Voir les erreurs

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
