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

    async def handle_boxes(self, request: web.BaseRequest) -> web.Response:
        """
        """
        text = str(self.counter.last_result.boxes)
        return web.Response(text=text)

    async def handle_last_frame(self, request: web.BaseRequest) -> web.Response:
        """
        """
        # encoding speed sort (timeit): bmp, jpg, png
        # 0.012, 0.497, 1.2771 secondes/(100xframes)
        # encoding size  sort: jpg, png, bmp
        # 50784, 296532, 921654 bytes
        _, image = cv2.imencode(".jpg", self.counter.last_capture)
        return web.Response(body=image.tobytes(), content_type="image/jpg")

    async def handle_index(self, request: web.BaseRequest) -> web.Response:
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

        context = {
            'model_status': "DOWN" if self.counter.model is None else "UP",
            'camera_status': "DOWN" if self.counter.cap is None else "UP",
            'postgrest_client_status': "DOWN" if self.pgclient.postgrest_client is None else "UP",

            'activate_counting': self.counter.activate_counting,
            'activate_database_insertion': self.pgclient.activate_insertion,
        }
        response = await aiohttp_jinja2.render_template_async(
            'index.html', request, context)
        return response

    async def handle_results(self, request: web.BaseRequest) -> web.Response:
        """
        """
        context = {
            'people_count': self.counter.people_count,
            'people_increment': self.counter.greatest_id,
            'remaining_time': self.counter.remaining_time,
            'buffer_length': len(self.pgclient.row_buffer),
            # 'boxes': self.counter.last_result.boxes,
        }
        response = await aiohttp_jinja2.render_template_async(
            'results.html', request, context)
        return response

    async def handle_results_live(self, request: web.BaseRequest) -> web.Response:
        """
        """
        context = {
            'update_interval': self.update_interval,
            'people_count': self.counter.people_count,
            'people_increment': self.counter.greatest_id,
            'remaining_time': self.counter.remaining_time,
            'buffer_length': len(self.pgclient.row_buffer),
        }
        response = await aiohttp_jinja2.render_template_async(
            'live.html', request, context)
        return response

    async def handle_configure_database(self, request: web.BaseRequest) -> web.Response:
        """
        """
        # TODO: Firefox resend the POST request even if the form is empty
        # TODO: show database connection error
        error: str

        data = await request.post()
        if data:
            # TODO: Use setters in pgclient to automatically call functions
            # Set fields
            if data['url']:
                self.pgclient.url = data['url']
            if data['key']:
                self.pgclient.key = data['key']
            if data['url'] or data['key']:
                self.pgclient.init_pgclient()

            if data['table']:
                self.pgclient.table = data['table']
            # TODO: KeyError: 'device_id' if key not in the form
            # if data['device_id']:
            #     try:
            #         self.pgclient.device_id = int(data['device_id'])
            #     except:
            #         pass
            # if data['location_id']:
            #     try:
            #         self.pgclient.location_id = int(data['location_id'])
            #     except:
            #         pass
            # if data['resolution_id']:
            #     try:
            #         self.pgclient.resolution_id = int(data['resolution_id'])
            #     except:
            #         pass
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

        context = {
            'url': self.pgclient.url,
            'key': "x" if self.pgclient.key else "",
            'table': self.pgclient.table,
            'device_id': self.pgclient.device_id,
            'location_id': self.pgclient.location_id,
            'resolution_id': self.pgclient.resolution_id,
            'insertion_delay': self.pgclient.insertion_delay,
            'error_delay': self.pgclient.error_delay,
        }

        response = await aiohttp_jinja2.render_template_async(
            'database.html', request, context)
        return response

    async def handle_configure_counter(self, request: web.BaseRequest) -> web.Response:
        """
        """
        # TODO: show database connection error
        error: str

        data = await request.post()
        if data:
            # TODO: Use setters in pgclient to automatically call functions
            # Set fields
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
            web.get('/boxes', self.handle_boxes),
            web.get('/last_frame', self.handle_last_frame),

            # Templated
            web.get("/", self.handle_index),
            web.post("/", self.handle_index),

            # TODO: One handle function with ?live=1 and live set in header.
            web.get('/results', self.handle_results),
            web.get('/live', self.handle_results_live),

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
