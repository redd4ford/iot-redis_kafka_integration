from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Union,
    List,
)

from django.utils import timezone
from injector import inject

from app_services.infrastructure import EventHubService


class Logger(ABC):
    @abstractmethod
    def log(self, data: dict, is_status: bool = False):
        pass


class ConsoleLogger(Logger):
    def __init__(self):
        print("Console Logging enabled")

    def log(self, data: dict, is_status: bool = False) -> None:
        # TODO(redd4ford): implement logging with built-in logging lib
        if is_status:
            print(f"{timezone.now()} --- [{data['key']}] = {data['value']}")
        else:
            print(
                f"[{timezone.now()}] --- {data['link']} --- "
                f"#{data['counter']} --- {data['body']} --- "
            )


class EventHubLogger(Logger):
    @inject
    def __init__(self, service: EventHubService = EventHubService()):
        self.service = service
        super().__init__()
        print("Event Hub Logging enabled")

    async def log(self, data: Union[List[dict], dict], is_status: bool = False) -> None:
        await self.service.send_data(data)
