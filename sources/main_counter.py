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
    table: Optional[str] = os.environ.get("SUPABASE_TABLE")
    if url is None or key is None or table is None:
        logger.error("SUPABASE_URL and SUPABASE_KEY and SUPABASE_TABLE are not set")
        exit(1)

    logger.info(f"SUPABASE_URL={url}")
    logger.info(f"SUPABASE_KEY=x")
    logger.info(f"SUPABASE_TABLE={table}")

    pgclient = PGClient(url, key, table)
    counter = Counter(pgclient)
    web = Web(counter)

    await asyncio.gather(
        pgclient.start_pgclient(),
        counter.start_counter(),
        web.start_web(),
    )


asyncio.run(main())