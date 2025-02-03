from postgrest import AsyncPostgrestClient
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class Device:

    def __init__(self, name: str) -> None:
        self.table_name: str = "appareils"

        self.id_column_name: str = "id_appareil"
        self.name_column_name: str = "nom_appareil"

        self.id: int = 0 # Uninitialised
        self.name: str = name

        self.last_exception: Exception = Exception() # Empty exception

    async def retrieve_device_id(self, postgrest_client: AsyncPostgrestClient) -> bool:
        # TODO: Device id can be updated in the database and become outdated
        """
        Retrieve the device id from the database given its name
        :return: True if the id has been fetched from the database, else False
        """
        # If the device id exists
        if self.id:
            return True

        # Check if the device name exists
        if not self.name:
            logger.error(f"No device name")
            return False

        # Fetch the device id from the table
        try:
            response = (
                await postgrest_client.table(self.table_name)
                .select(self.id_column_name).limit(1).like(self.name_column_name, self.name)
                .execute()
            )
        except Exception as e:
            self.last_exception = e
            logger.error(f"Failed to get the device id: {e}")
            return False

        # If it is not found (empty list)
        if not response.data:
            # TODO: Insert the no-found device in the database
            self.last_exception = Exception("Device id not found")
            logger.info(f"Device id not found")
            return False

        # Id is the first selected value in the list
        self.id = response.data[0][self.id_column_name]
        logger.info(f"Fetch the device id: {self.id}")
        return True
