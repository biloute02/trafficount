from collections import deque
from datetime import datetime
from typing import Optional
from postgrest import AsyncPostgrestClient
import supabase
import asyncio
import logging


from .tables.detection import Detection
from .tables.device import Device
from .tables.location import Location
from .tables.resolution import Resolution


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

        # Buffer of detections
        # If size=3600, one hour buffer for one insertion per second.
        self.detection_buffer_size: int = 3600
        self.detection_buffer: deque[Detection] = deque([], self.detection_buffer_size)

        # Insertion results
        # TODO: last_insertion_date is not of type datetime
        self.last_insertion_date: str = "-"
        self.last_insertion_count: int = 0
        self.last_insertion_exception: Exception = Exception()

        # Foreign keys
        self.device: Device = Device("Raspberry PI 5 Damien")
        self.location: Location = Location("Prototype nomade")
        self.resolution: Resolution = Resolution(640, 480)

        # Interval for inserting to the database
        # What is the good default value for insertion delay?
        self.insertion_delay: int = 10
        self.error_delay: int = 60

        # Activate the insertion of the detections values to the Database
        self.activate_insertion: bool = False

    def toggle_insertion(self, force: Optional[bool] = None) -> None:
        self.activate_insertion = force if force is not None else not self.activate_insertion
        logger.info(f"Set activate_insertion={self.activate_insertion}")

    def set_insertion_delay(self, insertion_delay: int | str) -> bool:
        """
        """
        try:
            insertion_delay = int(insertion_delay)
        except ValueError:
            logger.error(f"Delay not integer: insertion_delay={insertion_delay}")
            return False

        if insertion_delay < 0:
            logger.error(f"Delay must be positive: insertion_delay={insertion_delay}")
            return False

        self.insertion_delay = insertion_delay
        logger.info(f"Set insertion_delay={insertion_delay}")
        return True

    def set_error_delay(self, error_delay: int | str) -> bool:
        """
        """
        try:
            error_delay = int(error_delay)
        except ValueError:
            logger.error(f"Delay not integer: error_delay={error_delay}")
            return False

        if error_delay < 0:
            logger.error(f"Delay must be positive: error_delay={error_delay}")
            return False

        self.error_delay = error_delay
        logger.info(f"Set error_delay={error_delay}")
        return True

    async def update_device(self, device_name: str) -> None:
        """
        Update the device and try to retrieve its id from the database.
        """
        # Create a new device
        self.device = Device(device_name)
        logger.info(f"Set device_name={device_name}")

        # Retrive its id
        if self.postgrest_client is not None:
            await self.device.retrieve_device_id(self.postgrest_client)

    async def update_location(self, location_name: str) -> None:
        """
        Update the location and try to retrieve its id from the database.
        """
        # Create a new device
        self.location = Location(location_name)
        logger.info(f"Set location_name={location_name}")

        # Retrive its id
        if self.postgrest_client is not None:
            await self.location.retrieve_location_id(self.postgrest_client)

    async def update_resolution(self, width: int | str, height: int | str) -> bool:
        """
        Update the resolution and try to retrieve its id from the database.
        """
        try:
            width = int(width)
            height = int(height)
        except ValueError:
            logger.error(f"Resolution not integers: width={width} height={height}")
            return False

        if width < 0 or width > 9999 or height < 0 or height > 9999:
            logger.error(f"Resolution not between 0 and 9999: width={width} height={height}")
            return False

        # Create a new device
        self.resolution = Resolution(width, height)
        logger.info(f"Set width={width} height={height}")

        # Retrive its id
        if self.postgrest_client is not None:
            await self.resolution.retrieve_resolution_id(self.postgrest_client)
        return True

    def insert_detection(
        self,
        people_image_count: int,
        people_line_in_count: int,
        people_line_out_count: int,
    ) -> None:
        """
        Insert a detection to the buffer before being inserted to the database.
        """
        # No logging, too verbose
        detection = Detection(people_image_count, people_line_in_count, people_line_out_count)
        self.detection_buffer.append(detection)

    async def insert_detection_buffer(self) -> bool:
        """
        Insert the buffer to the database, then clear it if inserted
        """
        # Check if the buffer is non empty
        if not self.detection_buffer:
            logger.info(f"Empty buffer")
            return False

        # Check the postgrest client
        if self.postgrest_client is None:
            logger.info(f"No postgrest client")
            return False

        # TODO: Check if the postgrest client can access the database before retrieving the ID

        if not await self.device.retrieve_device_id(self.postgrest_client):
            logger.info(f"Missing the device id")
            return False

        if not await self.location.retrieve_location_id(self.postgrest_client):
            logger.info(f"Missing the location id")
            return False

        if not await self.resolution.retrieve_resolution_id(self.postgrest_client):
            logger.info(f"Missing the resolution id")
            return False

        try:
            # TODO: Move the table name and columns names in fields
            _ = (
                await self.postgrest_client
                .table("detections_suivi")
                .insert([
                    {
                        "nombre_personnes_image": detection.people_image_count,
                        "nombre_personnes_ligne_in": detection.people_line_in_count,
                        "nombre_personnes_ligne_out": detection.people_line_out_count,
                        "temps": detection.time,
                        "id_lieu": self.location.id,
                        "id_appareil": self.device.id,
                        "id_resolution": self.resolution.id
                    } for detection in self.detection_buffer
                ])
                .execute()
            )

            # If it succeeded (no exception raised)
            self.last_insertion_date = str(datetime.now().replace(microsecond=0))
            self.last_insertion_count = len(self.detection_buffer)
            self.detection_buffer.clear()

            return True
        except Exception as e:
            self.last_insertion_exception = e
            logger.error(f"Failed to insert the buffer to the database: {e}")
            return False

    # async def connection_test(self) -> bool:
    #     """
    #     Connection test to the database.
    #     :return: True if the client can query the database, else False
    #     """
    #     return True

    def set_url(self, url: str) -> None:
        self.url = url
        logger.info(f"Set database url={url}")

    def set_key(self, key: str) -> None:
        self.key = key
        logger.info(f"Set database key={key}")

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
            self.postgrest_client = None
            self.postgrest_client_exception = e
            logger.error(f"PostgreSQL client not initiated: {e}")
            return False

    async def start_pgclient(self) -> None:
        """
        Insert the buffer periodically to the database
        """
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
            if not await self.insert_detection_buffer():
                logger.info(f"{self.error_delay} seconds sleep before retrying insertion")
                await asyncio.sleep(self.error_delay)
