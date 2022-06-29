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

from django.utils import timezone
from injector import inject

from api.constants import FileStatus
from app_services.dataset_processor import FileStatusService
from app_services.infrastructure import EventHubService
from app_services.logger.utils import (
    should_update_upload_status,
    get_optimal_batching,
)


class Logger(ABC):
    @abstractmethod
    def log(self, link: str, data: dict):
        pass


class ConsoleLogger(Logger):
    def __init__(self):
        print("Console Logging enabled")

    def log(self, link: str, data: Union[List[dict], dict]) -> None:
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

    def log(self, link: str, data: Union[List[dict], dict]) -> None:
        """
        Batch send rows to Event Hub. Update Redis status after each processed batch.
        """
        chunk_size, chunked_data = get_optimal_batching(data)

        counter = 0
        for chunk in chunked_data:
            loop.run_until_complete(self.service.send_data(chunk))
            counter += len(chunk)
            FileStatusService().log_status(
                link,
                status=FileStatus.N_RECORDS_UPLOADED(counter)
            )


loop = asyncio.get_event_loop()
