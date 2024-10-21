from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")

#video_path = "videos/tokyo_cats_festival_foule_1080p.webm"
#cap = cv2.VideoCapture(video_path)
#success, frame = cap.read()

# Start tracking objects in a video
model.track(
    source = "videos/tokyo_cats_festival_foule_720p.webm",
    #source=0,
    #imgsz=(1080, 1920),
    imgsz=(720, 1280),
    #imgsz=(360, 640),
    stream_buffer=True,
    show=True,
    conf=0.5,
    classes=[0]
)
