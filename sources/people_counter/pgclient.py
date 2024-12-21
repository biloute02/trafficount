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

    def __init__(self) -> None:
        # Identification credentials
        self.url = ""
        self.key = ""

        # Postgrest client
        self.postgrest_client: Optional[AsyncPostgrestClient] = None
        self.postgrest_client_exception: Exception = Exception()

        # Connection test
        # self.connection_status: bool = False
        # self.connection_message: str = "Uninitialized"
        # self.connection_last_date: datetime = datetime.date()

        # Identification
        self.device_id: int = 0
        self.location_id: int = 0
        self.resolution_id: int = 0
        # Buffer of detections
        self.detection_buffer_size: int = 3600
        self.detection_buffer: deque[Detection] = deque([], self.detection_buffer_size)


        # Interval for inserting to the database
        # What is the good default value for insertion delay?
        self.insertion_delay: int = 10
        self.error_delay: int = 60

        # Activate the insertion of the detections values to the Database
        self.activate_insertion: bool = False

    def insert_detection(self, people_count: int) -> None:
        """
        Insert a detection to the buffer before being inserted to the database.
        """
        detection = Detection(people_count)
        self.detection_buffer.append(detection)

    async def insert_buffer(self) -> bool:
        """
        Insert the buffer to the database, then clear it
        """
        # TODO
        assert(self.postgrest_client is not None)

            return False

        try:
            _ = (
                await self.postgrest_client
                .table(self.detection_buffer[0].table_name)
                .insert([
                    {
                        "nombre_personnes": detection.people_count,
                        "temps": detection.time,
                        "id_lieu": self.location.id,
                        "id_appareil": self.device.id,
                        "id_resolution": self.resolution.id
                    } for detection in self.detection_buffer
                ])
                .execute()
            )

            # If it succeeded (no exception raised)
            self.detection_buffer.clear()
            # TODO: Too verbose. Check length of buffer or set a variable to the result of insertion
            # logger.info(f"Buffer inserted to {self.table}")
            return True
        except Exception as e:
            logger.error(f"Failed to insert the buffer to the database: {e}")
            return False

    # async def connection_test(self) -> bool:
    #     """
    #     Connection test to the database.
    #     :return: True if the client can query the database, else False
    #     """
    #     return True

    def init_pgclient(self) -> bool:
        """
        Create a new pg client. pg client and connection test is different,
        because the database can be unaccessible the moment the client is created.
        :return: True if the client is created, else False
        """
        if not self.url:
            self.postgrest_client = None
            logger.info("Missing the url")
            return False

        if not self.key:
            self.postgrest_client = None
            logger.info("Missing the key")
            return False

        try:
            logger.info(f"New pgclient with url={self.url} and key={self.key[0:10]}...")

            # Create the pgclient (no connection tests)
            supabase_client: supabase.Client = supabase.create_client(self.url, self.key)
            self.postgrest_client = supabase.AsyncClient._init_postgrest_client(
                rest_url=supabase_client.rest_url,
                headers=supabase_client.options.headers,
                schema=supabase_client.options.schema,
                verify=False
            )

            logger.info("PostgreSQL client initiated")
            return True

        except Exception as e:
            self.postgrest_client_exception = e
            logger.exception(f"PostgreSQL client not initiated")
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
            await asyncio.sleep(self.insertion_delay)

            # Check if insertion mode is ON
            if not self.activate_insertion:
                continue

            # Insert the buffer to the databse
            if not await self.insert_buffer():
                logger.info(f"{self.error_delay} minutes sleep before retrying insertion")
                await asyncio.sleep(self.error_delay)
