from ultralytics import YOLO

#
# Voir pour le détail https://docs.ultralytics.com/modes/predict/#inference-arguments
#

PERSON_CLASS_LABEL = 0
BED_CLASS_LABEL = 59

# Chargement d’un modèle yolo déja entrainé (pretrained)
model = YOLO("yolo11n.pt")

# Exporter au format ncnn plus rapide pour le CPU
# TODO: À faire une seul fois
#model.export(format="ncnn")
#ncnn_model = YOLO(
#    model="yolo11n_ncnn_model",
#    task="detect",
#)

# Faire de la prédiction / inférence
model.predict(

    ## Arguments pour l’inférence
    source="https://youtu.be/wnLQaSm8LhM?feature=shared", # Flux vidéo
    #source=0,                                            # Flux de la caméra 0
    conf=0.5,               # Taux minimum du confiance autorisé
    imgsz=(360, 640),       # Meilleur résolution -> meilleur détection
    device="cpu",           # Utiliser le CPU
    max_det=20,             # Maximum number of detections
    #visualize=True, # Chais pas
    #agnostic_nms=False,    # Meilleur détection des formes qui se confondent (pas utile?)
    classes=[               # Filtrer les prédictions selon une liste d’ID de classes
        PERSON_CLASS_LABEL,
        #BED_CLASS_LABEL,
    ],

    ## Paramètres du stream
    stream_buffer=False,    # Bufferiser les frames du flux. Désactiver pour ne pas traiter les frames en retard
    #stream=True,           # Same than stream_buffer. See https://github.com/orgs/ultralytics/discussions/12848
    vid_stride=1,           # Number of frames to skip (30 is one frame per second for a 30fps camera)

    ## Arguments pour la visualisation
    show=True,
)