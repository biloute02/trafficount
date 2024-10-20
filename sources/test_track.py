from ultralytics import YOLO

model = YOLO("yolo11n.pt")

# Start tracking objects in a video
model.track(source="url", show=True)
