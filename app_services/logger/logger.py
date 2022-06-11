from abc import (
    ABC,
    abstractmethod,
)
from typing import Union

from django.conf import settings

# TODO(redd4ford): implement logging with built-in logging lib
from django.utils import timezone


class Logger(ABC):
    @abstractmethod
    def log(self, data: dict):
        pass


class Context:
    def __init__(self, logger: Logger):
        self.logger = logger

    def write_log(self, data: Union[dict, str]) -> None:
        self.logger.log(data)


class ConsoleLogger(Logger):
    def __init__(self):
        print("Console Logging")

    def log(self, data: dict, is_status: bool = False) -> None:
        if is_status:
            print(f"{timezone.now()} --- [{data.keys()}] = {data.values()}")
        else:
            print(f"[{timezone.now()}] --- #{data['counter']} [{data['link']}] --- {data['body']}")


class EventHubLogger(Logger):
    def __init__(self):
        print("Event Hub Logging")

    def log(self, data: dict) -> None:
        print(f"{data['body']}")


context = Context(
    EventHubLogger() if settings.WRITE_TO_KAFKA
    else ConsoleLogger()
)
