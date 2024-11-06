import traceback
import cv2
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
)

def main():
    camera_index = 1
    cap = cv2.VideoCapture()
    opened = cap.open(camera_index)
    logger.error("ok")

main()