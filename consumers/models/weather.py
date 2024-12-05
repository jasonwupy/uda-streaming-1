"""Contains functionality related to Weather"""
from enum import IntEnum
import logging


logger = logging.getLogger(__name__)


class Weather:
    """Defines the Weather model"""
    
    status = IntEnum(
        "status", "sunny partly_cloudy cloudy windy precipitation", start=0
    )

    def __init__(self):
        """Creates the weather model"""
        self.temperature = 70.0
        self.status = "sunny"

    def process_message(self, message):
        data = message.value()
        self.temperature = data['temperature']
        self.status = data['status']