from collections import deque
from datetime import datetime
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
    ):
        # Identification credentials
        self.url: str = url
        self.key: str = key
        self.table: str = table

        # Buffer of rows
        self.row_buffer_size: int = 10
        self.row_buffer: deque[dict] = deque([], self.row_buffer_size)

        # Interval for inserting to the database
        self.insert_delay: int = 10

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
        try:
            _ = (
                await self.postgrest_client.table("detections")
                .insert(list(self.row_buffer))
                .execute()
            )
            self.row_buffer.clear()
            return True
        except Exception:
            logger.exception("Failed to insert the results to the database")
            return False

    async def init_pgclient(self) -> bool:
        """
        Create a connection
        """
        # TODO: Check if the connection is ok. Create the client doesn't try to connect to the databases
        self.supabase_client: supabase.AsyncClient = await supabase.create_async_client(self.url, self.key)
        self.postgrest_client = supabase.AsyncClient._init_postgrest_client(
            rest_url=self.supabase_client.rest_url,
            headers=self.supabase_client.options.headers,
            schema=self.supabase_client.options.schema,
            verify=False
        )
        logger.info("PostgreSQL client initiated")
        return True

    async def start_pgclient(self) -> None:
        """
        Insert the buffer periodically to the database
        """
        logger.info("PostgreSQL daemon started")
        while True:
            await asyncio.sleep(self.insert_delay)
            await self.insert_buffer()
