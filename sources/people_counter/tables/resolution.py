from postgrest import AsyncPostgrestClient
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Resolution:

    def __init__(self, width: int, height: int):
        self.table_name: str = "resolutions"

        self.id_column_name: str = "id_resolution"
        self.width_column_name: str = "largeur"
        self.height_column_name: str = "hauteur"

        self.id: int = 0 # Uninitialised
        self.width: str = width
        self.height: str = height

        self.last_exception: Exception = Exception()

    async def retrieve_resolution_id(self, postgrest_client: AsyncPostgrestClient) -> bool:
        """
        Retrieve the resolution id from the database given its name
        :return: True if the id has been fetched from the database, else False
        """
        # If the resolution id exists
        if self.id:
            return True

        # Fetch the resolution id from the table
        try:
            response = (
                await postgrest_client.table(self.table_name)
                .select(self.id_column_name).limit(1).eq(self.width_column_name, self.width).eq(self.height_column_name, self.height)
                .execute()
            )
        except Exception as e:
            self.last_exception = e
            logger.error(f"Failed to get the resolution id: {e}")
            return False

        # If it is not found (empty list)
        if not response.data:
            self.last_exception = Exception("Resolution id not found")
            logger.info(f"Resolution id not found")
            return False

        # Id is the first selected value in the list
        self.id = response.data[0][self.id_column_name]
        logger.info(f"Fetch the resolution id: {self.id}")
        return True
