from typing import Union

from django.conf import settings

from app_services.logger.logger import Logger
from app_services.logger import (
    EventHubLogger,
    ConsoleLogger,
)


class Context:
    def __init__(self, logger: Logger):
        self.logger = logger

    def write_log(self, link: str, data: Union[dict, str], is_status: bool = False) -> None:
        self.logger.log(link, data, is_status)


context = Context(
    EventHubLogger() if settings.WRITE_TO_KAFKA
    else ConsoleLogger()
)
