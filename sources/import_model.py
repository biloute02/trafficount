from ultralytics import YOLO  # type: ignore

# Load a YOLO11n PyTorch model
model = YOLO(model="yolo11n.pt", verbose=True)

# Export the model to NCNN format
# Default exported image size is 640x640
model.export(format="ncnn")  # creates 'yolo11n_ncnn_model'
