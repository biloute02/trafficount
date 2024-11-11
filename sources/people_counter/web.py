from aiohttp import web


from people_counter.counter import Counter


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

    async def handle_root(self, request) -> web.Response:
        """
        """
        text =  f"people_count     = {self.counter.people_count}\n"
        text += f"people_increment = {self.counter.greatest_id}"
        return web.Response(text=text)

    async def start_web(self):
        app = web.Application()
        app.add_routes([web.get('/test/', self.handle_test),
                        web.get('/test/{name}', self.handle_test),
                        web.get('/results', self.handle_track_results),
                        web.get('/', self.handle_root)])

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()
        logger.info("Web daemon started")
