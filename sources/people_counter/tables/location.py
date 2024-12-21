from postgrest import AsyncPostgrestClient
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Location:

    def __init__(self, name):
        self.table_name: str = "lieux"

        self.id_column_name: str = "id_lieu"
        self.name_column_name: str = "nom_lieu"

        self.id: int = 0 # Uninitialised
        self.name: str = name

        self.last_exception: Exception = Exception()

    async def retrieve_location_id(self, postgrest_client: AsyncPostgrestClient) -> bool:
        """
        Retrieve the location id from the database given its name
        :return: True if the id has been fetched from the database, else False
        """
        # If the location id exists
        if self.id:
            return True

        # Fetch the location id from the table
        try:
            response = (
                await postgrest_client.table(self.table_name)
                .select(self.id_column_name).limit(1).like(self.name_column_name, self.name)
                .execute()
            )
        except Exception as e:
            self.last_exception = e
            logger.error(f"Failed to get the location id: {e}")
            return False

        # If it is not found (empty list)
        if not response.data:
            self.last_exception = Exception("Location id not found")
            logger.info(f"Location id not found")
            return False

        # Id is the first selected value in the list
        self.id = response.data[0][self.id_column_name]
        logger.info(f"Fetch the location id: {self.id}")
        return True
