from datetime import datetime


class Detection:

    def __init__(self, people_count: int):
        self.table_name: str = "detections"

        self.people_count: int = people_count
        self.time: int = str(datetime.now())
