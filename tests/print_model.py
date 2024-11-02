from ultralytics import YOLO
from pprint import pprint

#
# Afficher les noms de classe de détection
#

# Chargement d’un modèle yolo déja entrainé
model = YOLO("yolo11n.pt")

# Afficher si CPU ou GPU
print(model.device)

# Afficher les classes
pprint(model.names)