import cv2

from ultralytics import solutions

cap = cv2.VideoCapture("videos/FAC_720p.webm")

# Only for cameras
#cap = 0
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)

assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

# Define region points
# region_points = [(20, 400), (1080, 400)]  # For line counting
# region_points = [(20, 400), (1080, 400), (1080, 360), (20, 360)]  # For rectangle region counting
# region_points = [(20, 400), (1080, 400), (1080, 360), (20, 360), (20, 400)]  # For polygon region counting

region_points = [(500, 20), (500, 700)]  # For line counting
# region_points = [(500, 20), (500, 700), (600, 700), (600, 20)]  # For line counting

# Video writer
# video_writer = cv2.VideoWriter("object_counting_FAC_720p_conf0_25_yolo11n_10fps.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

# Init ObjectCounter
counter = solutions.ObjectCounter(
    show=True,  # Display the output
    region=region_points,  # Pass region points
    model="yolo11n_ncnn_model",  # model="yolo11n-obb.pt" for object counting using YOLO11 OBB model.
    classes=[0,1],  # If you want to count specific classes i.e person and car with COCO pretrained model.
    conf=0.25,
    # classes=[0, 2],  # If you want to count specific classes i.e person and car with COCO pretrained model.
    # show_in=True,  # Display in counts
    # show_out=True,  # Display out counts
    # line_width=2,  # Adjust the line width for bounding boxes and text display
)

# Process video
mod = 0
im1 = None
while cap.isOpened():
    success, im0 = cap.read()
    # print(im0.shape)
    if not success:
        print("Video frame is empty or video processing has been successfully completed.")
        break

    if mod % 3 == 0:
        im1 = counter.count(im0)

    # video_writer.write(im1 if im1 is not None else im0)
    mod += 1

cap.release()
# video_writer.release()
cv2.destroyAllWindows()
