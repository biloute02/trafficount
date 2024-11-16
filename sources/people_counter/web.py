from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2

from .counter import Counter

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Web:

    def __init__(self, counter: Counter) -> None:
        self.counter = counter

    async def handle_test(self, request) -> web.Response:
        """
        """
        name = request.match_info.get('name', "Anonymous")
        text = "Hello, " + name
        return web.Response(text=text)

    async def handle_track_results(self, request) -> web.Response:
        """
        """
        text = str(self.counter.last_result.boxes)
        return web.Response(text=text)

    async def handle_root_ninja(self, request) -> web.Response:
        """
        """
        context = {
            'people_count': self.counter.people_count,
            'people_increment': self.counter.greatest_id,
        }
        response = await aiohttp_jinja2.render_template_async(
            'index.html', request, context)
        return response

    async def handle_root(self, request) -> web.Response:
        """
        """
        text =  f"people_count     = {self.counter.people_count}\n"
        text += f"people_increment = {self.counter.greatest_id}"
        return web.Response(text=text)

    async def start_web(self):
        app = web.Application()

        # Add the routes
        app.add_routes([
            web.get('/test/', self.handle_test),
            web.get('/test/{name}', self.handle_test),
            web.get('/results', self.handle_track_results),
            web.get('/', self.handle_root),
            web.get('/ninja', self.handle_root_ninja),
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
