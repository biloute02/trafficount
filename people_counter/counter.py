import asyncio
import time
import cv2
import logging
from ultralytics import YOLO # type: ignore
from ultralytics.engine.results import Results # type: ignore

from people_counter.pgclient import PGClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Counter:

    def __init__(
        self,
        pgclient: PGClient,
        delay: float = 0.5,
        confidence: float = 0.20,
    ) -> None:
        self.pgclient = pgclient

        # Parameters
        self.delay: float = delay
        self.confidence: float = confidence

        # Camera and model
        self.cap: cv2.VideoCapture
        self.model: YOLO

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
        self.model = YOLO(
            model="yolo11n.pt",
            verbose=True,
        )
        logger.info("Model loaded")
        return True

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
                    persist=True
                )

                # There is only one result because it is tracking
                # Save it in the global last_result for the web server
                self.last_result = results[0]

                # Get the greatest_id since the begin of the simulation
                #result.boxes.id.int().cpu().tolist()
                if results[0].boxes.id:
                    self.people_count = len(results[0].boxes.id)
                    self.greatest_id = max(
                        self.greatest_id,
                        max(results[0].boxes.id.cpu().int().tolist())
                    )
                else:
                    self.people_count = 0

                # Export the results to the database
                self.pgclient.insert_row(self.people_count)

                # Visualize the results on the frame
                annotated_frame = results[0].plot()
                # Display the annotated frame
                cv2.imshow("YOLO11 Tracking", annotated_frame)

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
        cv2.destroyAllWindows()
        logger.info("Video capture released")

    async def start_counter(self):
        """
        :param delay: delay between to inference in second
        """
        # Init the model
        if not self.init_model():
            await asyncio.sleep(10)
            return

        try:
            # Retry if a camera or tracking error occured
            while True:
                # Init the camera
                if not self.init_camera():
                    await asyncio.sleep(10)
                    continue

                # Start tracking
                # TODO: Function is never exiting
                await self.do_tracking()

                # Free the camera
                self.free_camera()

        except Exception as e:
            # Save exception for debugging (web server)
            self.last_exception = e

            logger.exception(f"An exception occured which failed the tracking")
