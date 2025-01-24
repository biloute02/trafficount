from datetime import datetime
import time
import logging
import asyncio
import cv2
from collections import deque
from cachetools import LRUCache
from typing import Optional, TypedDict
from shapely.geometry import LineString

from ultralytics import YOLO # type: ignore
from ultralytics.engine.results import Results # type: ignore
from ultralytics.utils.plotting import Annotator, colors # type: ignore

from .pgclient import PGClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Counter:

    def __init__(
        self,
        pgclient: PGClient,
        delay: float = 1,
        confidence: float = 0.20,
    ) -> None:
        # Postgres client
        self.pgclient = pgclient

        # Parameters
        # TODO: Add a minimum time for delay
        self.delay: float = delay
        self.confidence: float = confidence

        # Detection model
        self.model: Optional[YOLO] = None

        # Camera
        self.cap: Optional[cv2.VideoCapture] = None
        self.last_frame: Optional[cv2.typing.MatLike] = None

        # Line crossing
        # TODO: Init to the middle vertical line of the image automatically
        self.region = [(320, 0), (320, 480)]  # Half of 480x640
        # self.region = [(640, 0), (640, 720)]  # Half of 720x1280

        # Last inference and counting results
        self.last_result: Optional[Results] = None

        class Track(TypedDict):
            """
            For each track, we store:
            - Its limited list of points (x, y).
            - If the line crossed the region and has been counted.
            """
            line: deque[tuple[int, int]]
            counted: bool

        # LRU cache of track: list of points and.
        # With maxsize=500, we buffer only the [maxsize] last recently used tracks.
        # With maxlen=50 and a delay of 100ms, we can save 10 points/seconds for 5 seconds.
        #
        # Only the last two points are useful to check if a track crosses the region line.
        # The other points are useful to plot a visual track on the image.
        class TrackHistory(LRUCache):
            def __missing__(self, key) -> Track:  # Overide the parent function
                track: Track = {
                    "line": deque(iterable=[], maxlen=50),
                    "counted": False,
                }
                self[key] = track
                return track
        self.track_history: LRUCache[int, Track] = TrackHistory(maxsize=500)

        # In and out counts for each inference
        self.in_count = 0
        self.out_count = 0

        # In and out counts since the beginning (or the last reset)
        # TODO: Reset the total count in the web
        self.total_in_count = 0
        self.total_out_count = 0

        self.people_image_count: int = 0
        self.greatest_id: int = 0

        # Time to sleep before the next inference.
        self.remaining_time: float = 0

        # The last frame is an annotated image with the results
        # instead of the original captured frame.
        self.activate_image_annotation: bool = False

        # Activate inference tracking and add the results to the buffer
        self.activate_counting: bool = False # Tracking disable at startup

        # Save the frames in a video if enabled
        # TODO: Add arguments fps, width and heigh depending of the delay value.
        # TODO: Save separate images and not a video?
        # BUG: If the counting is lagging behind, the video will accelerate
        self.activate_video_writer: bool = False
        self.video_writer: Optional[cv2.VideoWriter] = None

        # Debugging
        # TODO: Change name of last_exception
        self.last_exception: Exception = Exception()

    def init_model(self) -> bool:
        """
        Load the YOLO11 model.
        """
        try:
            self.model = YOLO(
                task="detect",
                model="yolo11n_ncnn_model",
                verbose=True,
            )
            logger.info("Model loaded")
            return True

        except Exception:
            self.model = None
            logger.exception("Failed to load the model")
            return False

    def init_camera(self) -> bool:
        """
        Open the camera
        """
        camera_index = 0
        self.cap = cv2.VideoCapture(camera_index)
        # Set the camera resolution
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        if not self.cap.isOpened():
            logger.error(f"Camera index {camera_index} not opened")
            # Don't forget to reset the capture to None
            self.cap = None
            return False

        logger.info(f"Camera index {camera_index} opened")
        return True

    def init_video_writer(self) -> None:
        """
        Creat a new video writer
        """
        if self.video_writer is not None:
            self.video_writer.release()
            # TODO: Add the name of the filename released
            logger.info("Existing video writer release")

        # TODO: Remove hardcoded parameters for the
        # TODO: Remove typing warning for the cv2.VideoWriter_fourcc function
        # The filename must be valid on Windows and Linux (':' doesn't work on Windows)
        filename = f"video_writer/trafficount-{datetime.now().strftime("%Y_%m_%d-%H_%M_%S")}.mp4"
        fps = 1 / self.delay

        self.video_writer = cv2.VideoWriter(
            filename=filename,
            fourcc=cv2.VideoWriter.fourcc(*"mp4v"),  # "m", "p", "4", "v"
            fps=fps,
            frameSize=(640, 480))  # (width, height)
        logger.info(f"New video writer: filename={filename}, fps={fps}")

    def count_track_intersects_region(
        self,
        current_centroid: tuple[int, int],
        previous_centroid: tuple[int, int],
        track_id: int
    ) -> None:
        """
        Count if the track is entering (IN) or leaving (OUT) the region
        """
        # Don't count the track intersection twice
        if self.track_history[track_id]["counted"]:
            return

        # Region is a Line but could be implemented as a polygon
        line = LineString(self.region)
        if line.intersects(LineString([previous_centroid, current_centroid])):

            # Determine orientation of the region (vertical or horizontal)
            if abs(self.region[0][0] - self.region[1][0]) < abs(self.region[0][1] - self.region[1][1]):

                # Vertical region: Compare x-coordinates to determine direction
                if current_centroid[0] > previous_centroid[0]:  # Moving right
                    self.in_count += 1
                else:  # Moving left
                    self.out_count += 1

            # Horizontal region: Compare y-coordinates to determine direction
            elif current_centroid[1] > previous_centroid[1]:  # Moving downward
                self.in_count += 1
            else:  # Moving upward
                self.out_count += 1

            self.track_history[track_id]["counted"] = True

    def count(
        self,
        model: YOLO,
        frame: cv2.typing.MatLike,
    ) -> None:
        """
        Count the number of people on the frame (people_count).
        Count the number of different boxes detected (greatest_id).
        Count how many people have crossed the line (in_count/out_count).
        :param model: The model to use for counting.
        :param frame: The initial frame to track (non annotated).
        """
        results = model.track(
            source=frame,
            persist=True, # Do tracking by comparing with the result of the last frame
            classes=[0], # Detect only persons
            conf=self.confidence, # Confidence threshold
            verbose=False, # Suppress inference messages
            # imgsz=(1280, 736),  # Image size for infererence. Greater increase detection, increase time and reduce confidence
            # imgsz=(640, 480),  # Default image size (YOLO11n.pt)
            # imgsz=(640, 640),  # Image size for NCNN format. No detections with other resolutions
        )
        self.last_result = results[0]

        # Draw the region just after the object tracking
        annotator: Optional[Annotator] = Annotator(frame, line_width=2) if self.activate_image_annotation else None
        if annotator is not None:
            annotator.draw_region(reg_pts=self.region, color=(255, 0, 255))  # Draw the region

        track_ids: list[int] = []
        track_confidences: list[int] = []
        track_boxes: list[list[int]] = []

        # Check if boxes are detected
        # boxes.id is None if nothing is detected
        # BEWARE!: boxes.id has no boolean value
        # https://discuss.pytorch.org/t/boolean-value-of-tensor-with-more-than-one-value-is-ambiguous/151004/2
        boxes = self.last_result.boxes
        if boxes is not None and boxes.id is not None:
            track_ids = boxes.id.int().cpu().tolist()
            track_confidences = boxes.conf.float().cpu().tolist()
            track_boxes = boxes.xyxy.cpu().tolist()

        # Count the number of people on the image
        self.people_image_count = len(track_ids)

        # Count the greatest id of all time
        self.greatest_id = max(
            self.greatest_id,
            max(track_ids, default=0)) # Use the default argument to prevent exception with the empty list

        # Counting for each track
        for track_id, track_confidence, track_box in zip(track_ids, track_confidences, track_boxes):

            # Calculate the position of the center of the box
            current_centroid = (
                int((track_box[0] + track_box[2]) / 2),
                int((track_box[1] + track_box[3]) / 2))

            # Append the position to the history
            track_line = self.track_history[track_id]["line"]
            track_line.append(current_centroid)

            # Annotate the track
            if annotator is not None:
                track_color = colors(int(track_id), True)  # A different color for each id
                annotator.box_label(
                    track_box,
                    label=f"id: {track_id} conf: {round(track_confidence, 2)}",
                    color=track_color)
                annotator.draw_centroid_and_tracks(track_line, color=track_color)

            # If the track has only one point skip counting
            if len(track_line) < 2:
                continue

            # Count interesection of the track with the region
            previous_centroid = track_line[-2]
            self.count_track_intersects_region(current_centroid, previous_centroid, track_id)

            # TODO: Count if centroid is in region (instead of counting in all the image)
            # count_track_in_region()

    async def do_tracking(self) -> None:
        """
        Do tracking until error
        """
        # TODO: Move the checkings inside the loop for dynamic camera or models?
        if self.cap is None or self.model is None:
            logger.error("Can't do tracking if the capture device or the model are None")
            return

        # Time of the last frame read
        start_time: float = time.time() # Initialization to now

        # Loop through the video frames
        # TODO: Add a condition to stop looping
        while self.cap.isOpened():

            # Sleep at least once for the other coroutines to execute.
            await asyncio.sleep(0.001)

            # Calculate the remaining_time:
            # - Each loop should be executed in [delay] seconds.
            # - If it lasts less than [delay], we sleep [remaning_time] seconds.
            # - If it lasts more than [delay], we print a warning.
            self.remaining_time = (start_time + self.delay) - time.time()
            if self.remaining_time > 0:
                await asyncio.sleep(self.remaining_time)
            else:
                logger.warning(f"Image processing is lagging behind of {self.remaining_time} second")

            start_time = time.time()

            # Read a frame from the video
            success, frame = self.cap.read()
            if not success:
                # Break the loop if the camera is disconnected
                logger.error("Can't get next frame. Exit tracking...")
                break
            self.last_frame = frame

            # Count the number of people on the original frame
            if self.activate_counting:
                self.count(self.model, frame)

            # Annotate the frame with the region only if counting is disabled
            elif self.activate_image_annotation:
                annotator = Annotator(frame, line_width=2)
                annotator.draw_region(reg_pts=self.region, color=(255, 0, 255))  # Draw the region

            # Save the frame if frame saving is activated
            if self.activate_video_writer:
                if self.video_writer is not None:
                    self.video_writer.write(self.last_frame)

            # If not counting, stop now
            if not self.activate_counting:
                continue

            # Export the results to the database
            self.pgclient.insert_detection(self.people_image_count, self.in_count, self.out_count)

            # Reset the in and out count for each frame.
            # Save the total for fun.
            self.total_in_count += self.in_count
            self.total_out_count += self.out_count
            self.in_count = 0
            self.out_count = 0

    def free_camera(self):
        # Release the video capture object and close the display window
        self.cap.release()
        self.cap = None
        cv2.destroyAllWindows()
        logger.info("Video capture released")

    async def start_counter(self):
        """
        """
        # Init the model at startup
        self.init_model()

        logger.info("Counter daemon started")
        # Retry if a camera or tracking error occured
        while True:

            # Wait the model is initiated (either at startup or in the web)
            if self.model is None:
                await asyncio.sleep(10)
                continue

            # Init the camera
            if self.cap is None and not self.init_camera():
                await asyncio.sleep(60)
                continue

            # Start tracking
            await self.do_tracking()

            # Free the camera
            if self.cap is not None:
                self.free_camera()

            # Retry in 10 seconds
            await asyncio.sleep(10)
