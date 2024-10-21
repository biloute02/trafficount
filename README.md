## Téléchargement de vidéo

Utiliser `yt-dlp`: https://github.com/yt-dlp

```
# Lister les formats
.\yt-dlp.exe --list-formats url

# Télécharger entre la seconde 100 et 150 du flux 243
.\yt-dlp.exe --format 243 --download-sections "*250-265" url
```

## Plan

Plan de développement du prototype

### v1

* Système hors connexion (connexion perdu ou totalement)

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
