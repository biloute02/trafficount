import asyncio
import time
from typing import Optional
import cv2
import logging
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
        self.delay: float = delay
        self.confidence: float = confidence

        # Camera
        self.cap: Optional[cv2.VideoCapture] = None

        # Detection model
        self.model: Optional[YOLO] = None

        # Results
        self.last_result: Results
        self.people_count: int = 0
        self.greatest_id: int = 0

        # Debugging
        self.last_exception: Exception

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
            logger.exception("Failed to load the model")
            return False

    def init_camera(self) -> bool:
        """
        Open the camera
        """
        camera_index = 0
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            logger.error(f"Camera index {camera_index} not opened")
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

        last_time: float = time.time()

        # Loop through the video frames
        while self.cap.isOpened():

            # Read a frame from the video
            success, frame = self.cap.read()

            if not success:
                # Break the loop if the camera is disconnected
                logger.error("Can't get next frame. Exit tracking...")
                break
            else:
                # Run YOLO11 tracking on the frame, persisting tracks between frames
                results = self.model.track(
                    frame,
                    persist=True, # Do tracking by comparing with the result of the last frame
                    classes=[0], # Detect only persons
                    verbose=False, # Suppress inference messages
                )

                # There is only one result because it is tracking
                # Save it in the global last_result for the web server
                self.last_result = results[0]

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
                self.pgclient.insert_row(self.people_count)

                # Visualize the results on the frame
                #annotated_frame = results[0].plot()
                # Display the annotated frame
                #cv2.imshow("YOLO11 Tracking", annotated_frame)

                # Wait 1 millisecond. Break the loop if 'q' is pressed
                # TODO: Change the exist method for production
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                # Sleep at least one time between for the web server.
                await asyncio.sleep(0.001)

                # Calculate how much time we must sleep
                # TODO: Use absolute times and not relative times?
                current_time = time.time()
                remaining_time = (last_time + self.delay) - current_time

                # Sleep until the next image inference depending of how much time we have
                if remaining_time > 0:
                    await asyncio.sleep(remaining_time)
                    # The time now is last_time + delay
                    last_time += self.delay
                else:
                    logger.warning(f"do_tracking: Image processing is lagging behind of {remaining_time} second")
                    # As we are lagging behind (more than delay), last_time is now current time
                    last_time = current_time

    def free_camera(self):
        # Release the video capture object and close the display window
        self.cap.release()
        self.cap = None
        cv2.destroyAllWindows()
        logger.info("Video capture released")

    async def start_counter(self):
        """
        :param delay: delay between to inference in second
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
