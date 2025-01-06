from collections import defaultdict, deque
from typing import Optional
import cv2

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results
from ultralytics.utils.plotting import Annotator, colors

from shapely.geometry import LineString

# Model
model = YOLO(model="yolo11n.pt")

# Define region points
# region: list[tuple[int, int]] = [(320, 0), (320, 480)]
region: list[tuple[int, int]] = [(640, 0), (640, 720)]
# region: Optional[list[tuple[int, int]]] = None # For line counting

in_count = 0
out_count = 0  # Counter for objects moving outward
counted_ids: list[int] = []

people_count = 0
greatest_id = 0

# Dictionarry of id to list of points (track).
# Track is a maximum of 50 points (use the deque to limit the size)
# TODO: Limit the size of the dictionary
track_history: defaultdict[int, list[tuple[int, int]]] = defaultdict(lambda: deque([], 50))

def count_track_intersects_region(
    current_centroid: tuple[int, int],
    previous_centroid: tuple[int, int],
    track_id: int
) -> None:
    """
    Count if the track is entering (IN) or leaving (OUT) the region
    """
    global in_count, out_count

    # Don't count the track intersection twice
    if track_id in counted_ids:
        return

    # Region is a Line but could be implemented as a polygon
    line = LineString(region)
    if line.intersects(LineString([previous_centroid, current_centroid])):

        # Determine orientation of the region (vertical or horizontal)
        if abs(region[0][0] - region[1][0]) < abs(region[0][1] - region[1][1]):

            # Vertical region: Compare x-coordinates to determine direction
            if current_centroid[0] > previous_centroid[0]:  # Moving right
                in_count += 1
            else:  # Moving left
                out_count += 1

        # Horizontal region: Compare y-coordinates to determine direction
        elif current_centroid[1] > previous_centroid[1]:  # Moving downward
            in_count += 1
        else:  # Moving upward
            out_count += 1

        counted_ids.append(track_id)

def count(frame: np.ndarray) -> np.ndarray:
    """
    Count the number of people on the frame.
    Count the number of different boxes detected.
    Count how many people have crossed the line.
    :return: A new annotated frame with boxes and tracks
    """
    global greatest_id, people_count

    results = model.track(
        frame,
        persist=True, # Do tracking by comparing with the result of the last frame
        classes=[0], # Detect only persons
        conf=0.5, # Confidence threshold
        verbose=True, # Suppress inference messages
        # INFO: hardcoded imgsz for the presentation
        # imgsz=(640, 480)
    )
    result = results[0]

    # Annotate a new frame copy
    annotated_frame = frame.copy()
    annotator = Annotator(annotated_frame, line_width=2)
    annotator.draw_region(reg_pts=region, color=(104, 0, 123))  # Draw the region

    track_ids: list[int] = []
    track_boxes: list[list[int]] = []

    # Check if boxes are detected
    boxes = result.boxes
    if boxes is not None and boxes.id is not None:
        track_ids = boxes.id.int().cpu().tolist()
        track_boxes = boxes.xyxy.cpu().tolist()

    # Count the number of people on the image
    people_count = len(track_ids)

    # Count the greatest id of all time
    greatest_id = max(greatest_id, max(track_ids, default=0)) # Use the default argument to prevent exception with the empty list

    # Counting for each track
    for track_id, track_box in zip(track_ids, track_boxes):

        # Calculate the position of the center of the box
        current_centroid = ((track_box[0] + track_box[2]) / 2, (track_box[1] + track_box[3]) / 2)

        # Append the position to the history
        track_line = track_history[track_id]
        track_line.append(current_centroid)

        # Annotate the track
        track_color = colors(int(track_id), True)
        annotator.box_label(track_box, color=track_color)
        annotator.draw_centroid_and_tracks(track_line, color=track_color)

        # If the track has only one point skip counting
        if len(track_line) < 2:
            continue

        # Count interesection of the track with the region
        previous_centroid = track_line[-2]
        count_track_intersects_region(current_centroid, previous_centroid, track_id)

        # TODO: Count if centroid is in region (instead of counting in all the image)
        # count_track_in_region()

    # TODO: Annote the frame with the results
    return annotated_frame

def main():
    # Capture
    # cap = cv2.VideoCapture("videos/FAC_720p.webm")
    cap = cv2.VideoCapture(0)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    assert cap.isOpened(), "Error reading video file"
    # w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))

    # video_writer = cv2.VideoWriter("object_counting_output.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    #mod = 0
    while cap.isOpened():

        success, frame = cap.read()
        if not success:
            print("Video frame is empty or video processing has been successfully completed.")
            break

        #mod += 1
        #if mod % 10 != 0:
        #    continue

        last_capture = count(frame)

        print(f"in_count: {in_count}")
        print(f"out_count: {out_count}")

        cv2.imshow("Object counting", last_capture)
        if cv2.waitKey(1) & 0xFF == ord("q"):
           break

        # video_writer.write(im0)

    cap.release()
    cv2.destroyAllWindows()
    # video_writer.release()

main()
