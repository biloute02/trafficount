## Docker

Build the images:

```
docker build -f .\docker\Dockerfile-cpu -t {registry}/trafficount:latest-cpu .
docker build -f .\docker\Dockerfile-cpu -t {registry}/trafficount:{version}-cpu .
docker build -f .\docker\Dockerfile-arm -t {registry}/trafficount:latest-arm --platform linux/arm64 .
docker build -f .\docker\Dockerfile-arm -t {registry}/trafficount:{version}-arm --platform linux/arm64 .
```

Push the images:

```
docker push biloute02/trafficount:{tag}
```

## Run the image

### Docker

Create `pgclient.env`:

```
SUPABASE_URL="https://x.x.x.x:8443/"
SUPABASE_KEY="x"
SUPABASE_TABLE="detections_personnes"
```

Run:

```
docker run --env-file docker/pgclient.env --name trafficount -it --rm trafficount:latest-cpu python3 /trafficount/sources/main_counter.py
```
```
docker-compose up
```

### Python client Windows

```ps
$Env:SUPABASE_URL = "https://x.x.x.x:8443/"
$Env:SUPABASE_KEY = "x"
```

Run:

```
.\.venv\Scripts\Activate.ps1
python3 sources/main_counter.py
```

## Téléchargement de vidéo

Utiliser `yt-dlp`: https://github.com/yt-dlp

```
# Lister les formats
.\yt-dlp.exe --list-formats url

# Télécharger entre la seconde 100 et 150 du flux 243
.\yt-dlp.exe --format 243 --download-sections "*250-265" url
```

## Conversion de vidéos

Utiliser ffmpeg:

```
 ffmpeg -i .\brutes\FAC.MOV -an -ss 00:00:12 -to 00:00:37 -vf scale=640:-1 FAC_360p.webm
```
