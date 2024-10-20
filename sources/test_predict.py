from ultralytics import YOLO
from pprint import pprint

# Voir pour le détail https://docs.ultralytics.com/modes/predict/#inference-arguments

# Chargement d’un modèle yolo déja entrainé (pretrained)
model = YOLO("yolo11n.pt")

PERSON_CLASS_LABEL = 0
BED_CLASS_LABEL = 59

# Faire de la prédiction / inférence
model.predict(
    ## Arguments pour l’inférence
    source="https://youtu.be/wnLQaSm8LhM?feature=shared", # Flux vidéo
    #source=0,                                            # Flux de la caméra 0
    device="cpu",           # Utiliser le CPU
    conf=0.5,               # Taux minimum du confiance autorisé
    max_det=10,             # Maximum number of detections
    #visualize=True, # Chais pas
    stream_buffer=False,    # Bufferiser les frames du flux. Désactiver pour ne pas traiter les frames en retard
    vid_stride=1,           # Number of frames to skip (30 is one frame per second for a 30fps camera)
    agnostic_nms=False,     # Meilleur détection des formes qui se confondent (pas utile?)
    classes=[               # Filtrer les prédictions selon une liste d’ID de classes
        PERSON_CLASS_LABEL,
        #BED_CLASS_LABEL,
    ],

    ## Arguments pour la visualisation
    show=True,
)