from pathlib import Path
from ultralytics import YOLO  # type: ignore

# TODO: Run a single inference to download libraries
model = YOLO(model="yolo11n_ncnn_model", verbose=True)
model.track(source=Path(__file__).with_name("sonnyrollins.jpg"), show=True)
