import asyncio
import json
from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    Union,
    List,
)

from django.conf import settings
from django.utils import timezone
from injector import inject

from api.constants import FileStatus
from app_services.dataset_processor import FileStatusService
from app_services.infrastructure import EventHubService
from app_services.logger.utils import (
    should_update_upload_status,
    split_dataset_into_chunks,
)


class Logger(ABC):
    @abstractmethod
    def log(self, link: str, data: dict, is_status: bool = False):
        pass


class ConsoleLogger(Logger):
    def __init__(self):
        print("Console Logging enabled")

    def log(self, link: str, data: Union[List[dict], dict], is_status: bool = False) -> None:
        """
        Write rows to console. Update Redis status when a batch has been processed.
        """
        for counter, row in enumerate(data, start=1):
            print(
                f"[{timezone.now()}] --- {link} --- "
                f"#{counter} --- {json.dumps({'body': row})} --- "
            )
            if should_update_upload_status(processed_rows_number=counter):
                FileStatusService().log_status(
                    link,
                    status=FileStatus.N_RECORDS_UPLOADED(counter)
                )


class EventHubLogger(Logger):
    @inject
    def __init__(self, service: EventHubService = EventHubService()):
        self.service = service
        super().__init__()
        print("Event Hub Logging enabled")

    def log(self, link: str, data: Union[List[dict], dict], is_status: bool = False) -> None:
        """
        Batch send rows to Event Hub. Update Redis status after each processed batch.
        """
        data = split_dataset_into_chunks(data)
        for counter, chunk in enumerate(data, start=1):
            loop.run_until_complete(self.service.send_data(chunk))
            FileStatusService().log_status(
                link,
                status=FileStatus.N_RECORDS_UPLOADED(counter * settings.BATCH_SIZE)
            )


loop = asyncio.get_event_loop()
