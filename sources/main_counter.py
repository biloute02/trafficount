import asyncio
import logging
import os
from pathlib import Path
from typing import Optional


from people_counter.counter import Counter
from people_counter.pgclient import PGClient
from people_counter.web import Web
from people_counter.configuration import Configuration


logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(funcName)s:%(message)s',
    datefmt='%m/%d/%Y %H:%M:%S',
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def main() -> None:
    config_path = os.environ.get("CONFIG_PATH")

    pgclient = PGClient()
    counter = Counter(pgclient)

    configurator = Configuration(
        pgclient=pgclient,
        counter=counter,
        config_path=config_path
    )

    web = Web(
        counter=counter,
        pgclient=pgclient,
        configurator=configurator
    )

    # Read the configuration and apply it if it exists
    if (config := (await configurator.read_configuration_from_file())) is not None:
        await configurator.apply_configuration(config)

    await asyncio.gather(
        web.start_web(), # Start the website firt to have an interactive interface
        pgclient.start_pgclient(),
        counter.start_counter(),
    )


asyncio.run(main())
