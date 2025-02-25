from contextlib import suppress
from dataclasses import dataclass
import json
import logging
from pathlib import Path
from typing import Optional

from .counter import Counter
from .pgclient import PGClient


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class ConfMap:
    database_url = "database_url"
    database_key = "database_key"
    database_buffer_size = "database_buffer_size"
    database_insert_delay = "database_insert_delay"
    database_error_delay = "database_error_delay"
    database_device_name = "database_device_name"
    database_location_name = "database_location_name"
    database_resolution_width = "database_resolution_width"
    database_resolution_height = "database_resolution_height"

    counting_confidence = "counting_confidence"
    counting_delay = "counting_delay"
    counting_aggregated_frames_number = "counting_aggregated_frames_number"
    counting_line_p1_x = "counting_line_first_point_x"
    counting_line_p1_y = "counting_line_first_point_y"
    counting_line_p2_x = "counting_line_second_point_x"
    counting_line_p2_y = "counting_line_second_point_y"

    activate_counting = "activate_counting"
    activate_database_insertion = "activate_database_insertion"
    activate_image_annotation = "activate_image_annotation"
    # Activate Video writer is not saved...


confmap = ConfMap()


class Configuration:

    def __init__(
        self,
        pgclient: PGClient,
        counter: Counter,
        config_path: Optional[str] = None,  # None is convenient for env variables which are None if not defined.
    ):
        self.pgclient: PGClient = pgclient
        self.counter: Counter = counter

        self.config_path = Path("./configuration/trafficount.json")   # Default configuration file
        if config_path is not None:
            self.config_path = Path(config_path)

    def generate_configuration(self) -> dict[str, str]:
        """
        """
        # INFO: Way to get the field name
        # print(f"{toto.alembrique=}".split("=")[0].split(".")[1])

        config: dict[str, str] = {
            confmap.database_url: self.pgclient.url,
            confmap.database_key: self.pgclient.key,
            confmap.database_buffer_size:  str(self.pgclient.detection_buffer_size),
            confmap.database_insert_delay: str(self.pgclient.insertion_delay),
            confmap.database_error_delay:  str(self.pgclient.error_delay),

            confmap.database_device_name:       self.pgclient.device.name,
            confmap.database_location_name:     self.pgclient.location.name,
            confmap.database_resolution_width:  str(self.pgclient.resolution.width),
            confmap.database_resolution_height: str(self.pgclient.resolution.height),

            confmap.counting_confidence:               str(self.counter.confidence),
            confmap.counting_delay:                    str(self.counter.delay),
            confmap.counting_aggregated_frames_number: str(self.counter.aggregated_frames_number),
            confmap.counting_line_p1_x: str(self.counter.region[0][0]),
            confmap.counting_line_p1_y: str(self.counter.region[0][1]),
            confmap.counting_line_p2_x: str(self.counter.region[1][0]),
            confmap.counting_line_p2_y: str(self.counter.region[1][1]),

            confmap.activate_counting:           str(self.counter.activate_counting),
            confmap.activate_image_annotation:   str(self.counter.activate_image_annotation),
            confmap.activate_database_insertion: str(self.pgclient.activate_insertion),
        }

        return config

    async def save_configuration_to_file(self, config: dict[str, str]) -> bool:
        """
        """
        try:
            # TODO: do async
            self.config_path.parent.mkdir(exist_ok=True)
            with open(self.config_path, "w") as f:
                try:
                    json.dump(obj=config, fp=f, indent=2)
                except ValueError as e:
                    logger.exception(f"Can't serialize the configuration as JSON: {e}")
                    return False

        except OSError as e:
            logger.error(f"Can't open the configuration file for writing: {e}")
            return False

        logger.info(f"Configuration wrote to {self.config_path}")
        return True

    async def read_configuration_from_file(self) -> Optional[dict[str, str]]:
        """
        """
        config: dict[str, str] = {}
        try:
            # TODO: do async
            with open(self.config_path, "r") as f:
                try:
                    config = json.load(f)
                except ValueError as e:
                    logger.error(f"Failed to deserialize the configuration as JSON: {e}")
                    return None

        except OSError as e:
            logger.error(f"Can't read the configuration file: {e}")
            return None

        logger.info(f"Read the configuration from {self.config_path}")
        return config

    async def apply_configuration(self, config: dict[str, str]) -> None:
        """
        """
        # Set the database key or url
        if (database_key := config.get(confmap.database_key)):
            self.pgclient.set_key(database_key)
        if (database_url := config.get(confmap.database_url)):
            self.pgclient.set_url(database_url)
        if database_key or database_url:
            self.pgclient.init_pgclient()

        # Set the database ids
        if device_name := config.get(confmap.database_device_name):
            await self.pgclient.update_device(device_name)
        if location_name := config.get(confmap.database_location_name):
            await self.pgclient.update_location(location_name)
        if ((width  := config.get(confmap.database_resolution_width)) and
            (height := config.get(confmap.database_resolution_height))):
            await self.pgclient.update_resolution(width, height)

        # Set the delays
        if insert_delay := config.get(confmap.database_insert_delay):
            self.pgclient.set_insertion_delay(insert_delay)
        if error_delay := config.get(confmap.database_error_delay):
            self.pgclient.set_error_delay(error_delay)

        # Set the counting parameters
        if confidence := config.get(confmap.counting_confidence):
            self.counter.set_confidence(confidence)
        if delay := config.get(confmap.counting_delay):
            self.counter.set_delay(delay)
        if aggregated_frames_number := config.get(confmap.counting_aggregated_frames_number):
            self.counter.set_aggregated_frames_number(aggregated_frames_number)

        # Set modes
        # TODO: Convertions errors are not in toggle functions
        if activate_counting := config.get(confmap.activate_counting):
            with suppress(ValueError):
                self.counter.toggle_counting(force=(activate_counting=="True"))
        if activate_image_annotation := config.get(confmap.activate_image_annotation):
            with suppress(ValueError):
                self.counter.toggle_image_annotation(force=(activate_image_annotation=="True"))
        if activate_insertion := config.get(confmap.activate_database_insertion):
            with suppress(ValueError):
                self.pgclient.toggle_insertion(force=(activate_insertion=="True"))

        # Set the crossing line
        if ((line_p1_x := config.get(confmap.counting_line_p1_x)) and
            (line_p1_y := config.get(confmap.counting_line_p1_y))):
            self.counter.set_region_point_index((line_p1_x, line_p1_y), 0)

        if ((line_p2_x := config.get(confmap.counting_line_p2_x)) and
            (line_p2_y := config.get(confmap.counting_line_p2_y))):
            self.counter.set_region_point_index((line_p2_x, line_p2_y), 1)

        logger.info("Configuration applied!")
