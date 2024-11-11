from ultralytics import YOLO

model = YOLO("yolo11n.pt")

model.export(format="ncnn")
ncnn_model = YOLO(
    model="yolo11n_ncnn_model",
    task="detect",
)