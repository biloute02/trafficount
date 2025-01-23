from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import cv2
import jinja2

from .counter import Counter
from .pgclient import PGClient

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Web:

    def __init__(self, counter: Counter, pgclient: PGClient) -> None:
        self.counter = counter
        self.pgclient = pgclient

        self.update_interval = 1
        self.config_file = "trafficount.conf" # json config

    async def handle_last_frame(self, request: web.Request) -> web.Response:
        """
        Display the last camera frame.
        It is annotated if counting is activated.
        The numpy array is encode to jpg before sending.
        """
        # encoding speed sort (timeit): bmp, jpg, png
        # 0.012, 0.497, 1.2771 secondes/(100xframes)
        # encoding size  sort: jpg, png, bmp
        # 50784, 296532, 921654 bytes
        if self.counter.last_frame is None:
            return web.Response(text="No camera image")
        else:
            _, image = cv2.imencode(".jpg", self.counter.last_frame)
            return web.Response(body=image.tobytes(), content_type="image/jpg")

    async def handle_last_result(self, request: web.Request) -> web.Response:
        """
        Display the last result of the inference.
        """
        if self.counter.last_result is None:
            return web.Response(text="No inference result")
        else:
            return web.Response(text=str(self.counter.last_result))

    async def handle_last_boxes(self, request: web.Request) -> web.Response:
        """
        Display the last boxes object of the last inference result.
        """
        if self.counter.last_result is None or self.counter.last_result.boxes is None:
            return web.Response(text="No inference boxes")
        else:
            return web.Response(text=str(self.counter.last_result.boxes))

    async def handle_index(self, request: web.Request) -> web.Response:
        """
        Handle the index page and toggle mode if requested
        """
        data = await request.post()
        if data:
            # Check if the toggle fields are in the POST data
            if "toggle_counting" in data:
                self.counter.activate_counting = not self.counter.activate_counting
            if "toggle_database_insertion" in data:
                self.pgclient.activate_insertion = not self.pgclient.activate_insertion

                # Clear the detection buffer when the insertion is activated
                # and all the informative counters.
                if self.pgclient.activate_insertion:
                    self.pgclient.detection_buffer.clear()
                    self.counter.total_in_count = 0
                    self.counter.total_out_count = 0

            if "toggle_image_annotation" in data:
                self.counter.activate_image_annotation = not self.counter.activate_image_annotation

            # Redirect with the GET method
            raise web.HTTPSeeOther(request.rel_url.path)

        context = {
            # Status must be booleans
            'model_status': self.counter.model is not None,
            'camera_status': self.counter.cap is not None,
            'postgrest_client_status': self.pgclient.postgrest_client is not None,

            # Modes must be booleans
            'activate_counting': self.counter.activate_counting,
            'activate_database_insertion': self.pgclient.activate_insertion,

            # Testing features
            'activate_image_annotation': self.counter.activate_image_annotation,
        }
        response = await aiohttp_jinja2.render_template_async(
            'index.html', request, context)
        return response

    async def handle_results(self, request: web.Request) -> web.Response:
        """
        """
        context = {
            'people_image_count': self.counter.people_image_count,
            'people_increment': self.counter.greatest_id,

            'people_in_count': self.counter.in_count,
            'people_out_count': self.counter.out_count,
            'people_total_in_count': self.counter.total_in_count,
            'people_total_out_count': self.counter.total_out_count,

            'remaining_time': self.counter.remaining_time,
            'buffer_length': len(self.pgclient.detection_buffer),
            # 'boxes': self.counter.last_result.boxes,
        }
        response = await aiohttp_jinja2.render_template_async(
            'results.html', request, context)
        return response

    async def handle_results_live(self, request: web.Request) -> web.Response:
        """
        """
        response = await self.handle_results(request)
        response.headers['refresh'] = str(self.update_interval)
        return response

    async def handle_configure_camera(self, request: web.Request) -> web.Response:
        """
        """
        data = await request.post()
        if data:
            if data['line_first_point_x'] and data['line_first_point_y']:
                try:
                    self.counter.region[0] = (
                        int(data['line_first_point_x']),
                        int(data['line_first_point_y']))
                except:
                    pass
            if data['line_second_point_x'] and data['line_second_point_y']:
                try:
                    self.counter.region[1] = (
                        int(data['line_second_point_x']),
                        int(data['line_second_point_y']))
                except:
                    pass

            # Redirect with the GET method
            raise web.HTTPSeeOther(request.rel_url.path)

        context = {
            'line_first_point': self.counter.region[0],
            'line_second_point': self.counter.region[1],
        }
        response = await aiohttp_jinja2.render_template_async(
            'camera.html', request, context)
        return response

    async def handle_configure_database(self, request: web.Request) -> web.Response:
        """
        """
        # TODO: show database connection error
        data = await request.post()
        if data:
            if data['url']:
                self.pgclient.url = data['url']
            if data['key']:
                self.pgclient.key = data['key']
            if data['url'] or data['key']:
                self.pgclient.init_pgclient()

            if data['device_name']:
                await self.pgclient.update_device(data['device_name'])
            if data['location_name']:
                await self.pgclient.update_location(data['location_name'])
            if data['resolution_width'] and data['resolution_height']:
                try:
                    await self.pgclient.update_resolution(
                        int(data['resolution_width']),
                        int(data['resolution_height']))
                except:
                    pass

            if data['insertion_delay']:
                try:
                    self.pgclient.insertion_delay = int(data['insertion_delay'])
                except:
                    pass
            if data['error_delay']:
                try:
                    self.pgclient.error_delay = int(data['error_delay'])
                except:
                    pass

            # Redirect with the GET method
            raise web.HTTPSeeOther(request.rel_url.path)

        context = {
            'url': self.pgclient.url,
            'key': "x" if self.pgclient.key else "",
            'insertion_delay': self.pgclient.insertion_delay,
            'error_delay': self.pgclient.error_delay,

            'device_name': self.pgclient.device.name,
            'location_name': self.pgclient.location.name,
            'resolution_width': self.pgclient.resolution.width,
            'resolution_height': self.pgclient.resolution.height,

            'device_id': self.pgclient.device.id,
            'location_id': self.pgclient.location.id,
            'resolution_id': self.pgclient.resolution.id,

            'device_exception': str(self.pgclient.device.last_exception),
            'location_exception': str(self.pgclient.location.last_exception),
            'resolution_exception': str(self.pgclient.resolution.last_exception),

            'last_insertion_date': self.pgclient.last_insertion_date,
            'last_insertion_count': self.pgclient.last_insertion_count,
            'last_insertion_exception': str(self.pgclient.last_insertion_exception),
        }

        response = await aiohttp_jinja2.render_template_async(
            'database.html', request, context)
        return response

    async def handle_configure_counter(self, request: web.Request) -> web.Response:
        """
        """
        # TODO: show database connection error
        error: str

        data = await request.post()
        if data:
            if data['delay']:
                try:
                    self.counter.delay = float(data['delay'])
                except:
                    pass
            if data['confidence']:
                try:
                    self.counter.confidence = float(data['confidence'])
                except:
                    pass

            # Redirect with the GET method
            raise web.HTTPSeeOther(request.rel_url.path)

        context = {
            'delay': self.counter.delay,
            'confidence': self.counter.confidence,
        }

        response = await aiohttp_jinja2.render_template_async(
            'counter.html', request, context)
        return response

    async def start_web(self):
        app = web.Application()

        # Add the routes
        app.add_routes([
            # Non templated
            web.get('/last_frame', self.handle_last_frame),
            web.get('/last_result', self.handle_last_result),
            web.get('/last_boxes', self.handle_last_boxes),

            # Templated
            web.get("/", self.handle_index),
            web.post("/", self.handle_index),

            # Camera image
            web.get('/camera', self.handle_configure_camera),
            web.post('/camera', self.handle_configure_camera),

            # Inference results
            web.get('/results', self.handle_results),
            web.get('/results/live', self.handle_results_live),

            # Database form
            web.get('/database', self.handle_configure_database),
            web.post('/database', self.handle_configure_database),

            # Counter form
            web.get('/counter', self.handle_configure_counter),
            web.post('/counter', self.handle_configure_counter),
        ])

        # Search the templates directory in the same parent directory than this module
        templates_path = Path(__file__).with_name("templates")

        # Create the jinja2 environment to load the templates
        # TODO: Use a different loader to automatically load the templates folder in the module
        aiohttp_jinja2.setup(
            app,
            loader=jinja2.FileSystemLoader(templates_path),
            enable_async=True,
        )

        # Launch the website
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        logger.info("Web daemon started")
