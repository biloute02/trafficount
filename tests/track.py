from ultralytics import YOLO  # type: ignore
import cv2

# model = YOLO("yolo11n.pt")
model = YOLO("yolo11n_ncnn_model")

#video_path = "videos/tokyo_cats_festival_foule_1080p.webm"
#cap = cv2.VideoCapture(video_path)
#success, frame = cap.read()

# Start tracking objects in a video
model.track(
    source = "videos/D02_720p.webm",
    #source = "videos/tokyo_cats_festival_foule_720p.webm",
    #source = "videos/moi.mp4",
    #source=0,
    #imgsz=(1080, 1920),
    #imgsz=(720, 1280),
    #imgsz=1280,
    imgsz=(640, 640),
    stream_buffer=False,
    #vid_stride=3,
    show=True,
    conf=0.3,
    #tracker="./trackers/my_botsort_tracker.yaml",
    #classes=[0]
)
