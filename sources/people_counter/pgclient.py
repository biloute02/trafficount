from collections import deque
from datetime import datetime
from typing import Optional
from postgrest import AsyncPostgrestClient
import supabase
import asyncio

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PGClient:

    def __init__(
        self,
        url: str,
        key: str,
        table: str,
    ) -> None:
        # Identification credentials
        self.url = url
        self.key = key

        # Postgrest client
        self.postgrest_client: Optional[AsyncPostgrestClient] = None

        # Table to insert values
        self.table: str = table

        # Buffer of rows
        self.row_buffer_size: int = 3600
        self.row_buffer: deque[dict] = deque([], self.row_buffer_size)

        # Interval for inserting to the database
        self.insert_delay: int = 60

    def insert_row(
        self,
        people_count: int
    ) -> bool:
        """
        Insert a row to the buffer before being inserted to the database
        """
        row = {
            "lieu": "Trafficount",
            "timestamp": str(datetime.now()),
            "nombre_personnes": people_count,
            "resolution_image": "aucune"
        }
        self.row_buffer.append(row)
        return True

    async def insert_buffer(self) -> bool:
        """
        Insert the buffer to the database, then clear it
        """
        # TODO
        assert(self.postgrest_client is not None)

        try:
            _ = (
                await self.postgrest_client.table(self.table)
                .insert(list(self.row_buffer))
                .execute()
            )
            self.row_buffer.clear()
            logger.info(f"Buffer inserted to {self.table}")
            return True
        except Exception:
            logger.exception("Failed to insert the buffer to the database")
            return False

    def init_pgclient(self) -> bool:
        """
        Create a connection. Always succeed
        """
        try:
            supabase_client: supabase.Client = supabase.create_client(self.url, self.key)
            self.postgrest_client = supabase.AsyncClient._init_postgrest_client(
                rest_url=supabase_client.rest_url,
                headers=supabase_client.options.headers,
                schema=supabase_client.options.schema,
                verify=False
            )
            logger.info("PostgreSQL client initiated:")
            return True

        except Exception:
            logger.exception("PostgreSQL client not initiated")
            return False

    async def start_pgclient(self) -> None:
        """
        Insert the buffer periodically to the database
        """
        # Init the Postgres Client
        self.init_pgclient()

        logger.info("PostgreSQL daemon started")
        while True:

            # Wait the postgrest client is initiated (either at startup or in the web)
            if self.postgrest_client is None:
                await asyncio.sleep(10)
                continue

            # Wait until insert buffer delay has elapsed
            await asyncio.sleep(self.insert_delay)

            # Insert the buffer to the databse
            if not await self.insert_buffer():
                failed_sleep_delay = 60
                logger.info(f"{failed_sleep_delay} minutes sleep before retrying insertion")
                await asyncio.sleep(failed_sleep_delay)
