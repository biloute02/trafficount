import cv2

def main():
    camera_index = 0

    # Open the camera
    cap = cv2.VideoCapture()
    opened = cap.open(camera_index)
    # cap = cv2.VideoCapture(camera_index)
    # cap.isOpened()
    if not opened:
        print(f"Error opening the camera index: {camera_index}")
        return False

    # Set the resolution (comment these lines to get the default resolution)
    # Set maximum resolution with a very high value (10000)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 10000)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 10000)

    # Grab an image
    success, frame = cap.read()
    if not success:
        print("Error getting the next frame")
        return False

    # Check the image shape
    print(f"frame shape: {frame.shape}")

    return True

main()