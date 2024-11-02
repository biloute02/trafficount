import asyncio
import time
from aiohttp import web
import cv2
from ultralytics import YOLO
from ultralytics.engine.results import Results


last_result: Results
people_count: int = 0
greatest_id: int = 0


async def people_counter(delay: float):
    """
    :param delay: delay between to inference in second
    """
    global last_result
    global people_count
    global greatest_id

    # Open the video file
    #video_path = "videos/tokyo_cats_festival_foule_720p.webm"
    video_path = 0
    cap = cv2.VideoCapture(video_path)

    # Load the YOLO11 model
    model = YOLO(
        model="yolo11n.pt",
        verbose=True,
    )
    print("Model loaded!")

    last_time: float = time.time()

    # Loop through the video frames
    while cap.isOpened():

        # Read a frame from the video
        success, frame = cap.read()

        if not success:
            # Break the loop if
            # - the end of the video is reached
            # - the camera is disconnected
            print("Can't get next frame. Existing...")
            break
        else:
            # Run YOLO11 tracking on the frame, persisting tracks between frames
            results = model.track(frame, persist=True)

            # There is only one result because it is tracking
            # Save it in the global last_result for the web server
            last_result = results[0]

            # Get the greatest_id since the begin of the simulation
            #result.boxes.id.int().cpu().tolist()
            if results[0].boxes.id:
                people_count = len(results[0].boxes.id)
                greatest_id = max(greatest_id, max(results[0].boxes.id.cpu().int().tolist()))
            else:
                people_count = 0

            # Print tracking IDs
            #for r in results:
            #    print(r.boxes)

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
            remaining_time = (last_time + delay) - current_time

            # Sleep until the next image inference depending of how much time we have
            if remaining_time > 0:
                await asyncio.sleep(remaining_time)
                # The time now is last_time + delay
                last_time += delay
            else:
                print("Image processing is lagging behind!")
                # As we are lagging behind (more than delay), last_time is now current time
                last_time = current_time


    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()
    print("Video capture released")

async def handle_test(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name
    return web.Response(text=text)

async def handle_track_results(request):
    global last_result

    text = str(last_result.boxes)
    return web.Response(text=text)

async def handle(request):
    global people_count
    global greatest_id

    text =  f"people_count     = {people_count}\n"
    text += f"people_increment = {greatest_id}"
    return web.Response(text=text)

async def main():

    app = web.Application()
    app.add_routes([web.get('/test/', handle_test),
                    web.get('/test/{name}', handle_test),
                    web.get('/results', handle_track_results),
                    web.get('/', handle)])

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

    await asyncio.gather(
        people_counter(0.200)
    )

asyncio.run(main())
