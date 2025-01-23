from datetime import datetime


class Detection:

    def __init__(
        self,
        people_image_count: int,
        people_line_in_count: int,
        people_line_out_count: int,
    ):
        self.people_image_count: int = people_image_count
        self.people_line_in_count: int = people_line_in_count
        self.people_line_out_count: int = people_line_out_count

        self.time: str = str(datetime.now())

    # TODO: Add the insertion to the Detection class?
    # - The foreign device/location/resolution key fields.
    # - Table name and column names for each field.
    # - update_device(), update_location(), update_resolution()
    # - The detection list buffer.
    # - insert_detection()
    # - insert_detection_buffer()
    # Problem:
    # - Detection is a data class:
    #   one object equals one detection; one object created for each detection.
    # - Device/Location/Resolution are not data classes:
    #   one object equals one device/location/resolution; only one object created for insertion.