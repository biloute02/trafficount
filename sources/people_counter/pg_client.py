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
        self.url: str = url
        self.key: str = key
        self.table: str = table

        # TODO: Use a buffer?
        self.buffer: list[dict] = []
        self.buffer_size = 10

    async def send(
        self,
        people_count: int
    ) -> bool:
        """
        """
        row = {
            "lieu": "Trafficount",
            "timestamp": str(datetime.now()),
            "nombre_personnes": people_count,
            "resolution_image": "aucune"
        }

        try:
            response = (
                await self.postgrest_client.table("detections")
                .insert(row)
                .execute()
            )
            return True
        except Exception as e:
            logger.exception("Fail to insert the results remotly into the database")
            return False


    async def init_supabase(self) -> bool:
        """
        Create a connection
        """

        self.supabase_client: supabase.AsyncClient = await supabase.create_async_client(self.url, self.key)
        self.postgrest_client = supabase.AsyncClient._init_postgrest_client(
            rest_url=self.supabase_client.rest_url,
            headers=self.supabase_client.options.headers,
            schema=self.supabase_client.options.schema,
            verify=False
        )
        return True

    def start_pg_client(self) -> None:
        ...
