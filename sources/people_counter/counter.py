import asyncio
import time
from typing import Optional
import cv2
import logging
import numpy as np
from ultralytics import YOLO # type: ignore
from ultralytics.engine.results import Results # type: ignore

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

        # Camera
        self.cap: Optional[cv2.VideoCapture] = None

        # Detection model
        self.model: Optional[YOLO] = None

        # Results
        # TODO: Init values ?
        self.last_result: Results
        self.last_capture: np.ndarray

        self.people_count: int = 0
        self.greatest_id: int = 0
        self.remaining_time: float = 0

        # Mode d'envoi vers la BDD - True = Oui / False = Non
        self.activate_counting: bool = False # Tracking disable at startup

        # Debugging
        self.last_exception: Exception = Exception()


    def init_model(self) -> bool:
        """
        Load the YOLO11 model.
        """
        # TODO: Catch exception or error?
        try:
            self.model = YOLO(
                model="yolo11n.pt",
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
        # TODO: Set the camera resolution in this order
        # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        # success, frame = cap.read()
        # cap.release()
        camera_index = 0
        self.cap = cv2.VideoCapture(camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        if not self.cap.isOpened():
            logger.error(f"Camera index {camera_index} not opened")
            # Don't forget to reset the capture to None
            self.cap = None
            return False

        logger.info(f"Camera index {camera_index} opened")
        return True

    async def do_tracking(self) -> None:
        """
        Do tracking until error
        """
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

            # Check if counting is activated
            if not self.activate_counting:
                continue

            # Run YOLO11 tracking on the frame, persisting tracks between frames
            # TODO: Set imgsz and confidence
            results = self.model.track(
                frame,
                persist=True, # Do tracking by comparing with the result of the last frame
                classes=[0], # Detect only persons
                conf=self.confidence, # Confidence threshold
                verbose=False, # Suppress inference messages
                # INFO: hardcoded imgsz for the presentation
                imgsz=(1280,736),
            )

            # There is only one result because it is tracking
            # Save it in the global last_result for the web server
            self.last_result = results[0]

            # Visualize the results on the frame
            self.last_capture = results[0].plot()

            # Get the greatest_id since the begin of the simulation
            # boxes.id is None if nothing is detected
            # BEWARE!: boxes.id has no boolean value
            # https://discuss.pytorch.org/t/boolean-value-of-tensor-with-more-than-one-value-is-ambiguous/151004/2
            if results[0].boxes.id is None:
                self.people_count = 0
            else:
                self.people_count = len(results[0].boxes.id)
                self.greatest_id = max(
                    self.greatest_id,
                    max(results[0].boxes.id.int().tolist())
                )

            # Export the results to the database
            self.pgclient.insert_detection(self.people_count)

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
