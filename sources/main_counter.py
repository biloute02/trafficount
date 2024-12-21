import asyncio
import logging
import os
from typing import Optional


from people_counter.counter import Counter
from people_counter.pgclient import PGClient
from people_counter.web import Web


logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main() -> None:
    url: Optional[str] = os.environ.get("SUPABASE_URL")
    key: Optional[str] = os.environ.get("SUPABASE_KEY")
    if url is None or key is None:
        logger.error("SUPABASE_URL and SUPABASE_KEY are not set")
        exit(1)

    logger.info(f"SUPABASE_URL={url}")
    logger.info(f"SUPABASE_KEY=x")

    pgclient = PGClient()
    # TODO: Temporary until the configuration file
    pgclient.url = url
    pgclient.key = key

    counter = Counter(pgclient)
    web = Web(counter, pgclient)

    await asyncio.gather(
        web.start_web(), # Start the website firt to have an interactive interface
        pgclient.start_pgclient(),
        counter.start_counter(),
    )


asyncio.run(main())
