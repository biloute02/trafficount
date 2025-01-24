import cv2

from ultralytics import YOLO  # type: ignore

# Load the YOLO11 model
model = YOLO(
    model="yolo11n_ncnn_model",
    verbose=True,
)

# Open the video file
#video_path = "videos/tokyo_cats_festival_foule_720p.webm"
video_path=0
cap = cv2.VideoCapture(video_path)

# Loop through the video frames
while cap.isOpened():

    # Read a frame from the video
    success, frame = cap.read()

    if success:
        # Run YOLO11 tracking on the frame, persisting tracks between frames
        results = model.track(
            frame,
            persist=True,
            # imgsz=(720, 1280)
        )

        result = results[0]
        print(f"result: {result}")
        print(f"boxes: {result.boxes}")
        print(f"boxes conf: {result.boxes.conf.cpu().tolist()}")
        # print(f"boxes xyxy: {result.boxes.xyxy.cpu().tolist()}")

        # print(f"boxes: {result.boxes}")
        # print(f"masks: {result.masks}")
        # print(f"probs: {result.probs}")
        # print(f"obb: {result.obb}")

        cv2.imshow("Tracking", result.plot())
        if cv2.waitKey(0) & 0xFF == ord("q"):
            break

        # Visualize the results on the frame
        #annotated_frame = results[0].plot()

        # Display the annotated frame
        #cv2.imshow("YOLO11 Tracking", annotated_frame)

        # Break the loop if 'q' is pressed
        #if cv2.waitKey(0) & 0xFF == ord("q"):
        #    break
    else:
        print("Failure")
        break

# Release the video capture object and close the display window
cap.release()
cv2.destroyAllWindows()