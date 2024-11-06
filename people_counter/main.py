import asyncio
import logging

from people_counter.counter import Counter
from people_counter.pgclient import PGClient
from people_counter.web import Web


logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main():
    pgclient = PGClient()
    counter = Counter(pgclient)
    web = Web(counter)

    await asyncio.gather(
        pgclient.start_pgclient(),
        counter.start_counter(),
        web.start_web(),
    )


asyncio.run(main())
