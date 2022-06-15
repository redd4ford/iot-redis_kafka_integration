import json

from django.conf import settings

from api.constants import FileStatus
from api.exceptions import LinkDoesNotContainJsonError
from app_services.dataset_processor import (
    FileLoader,
    FileGenerator,
    FileStatusService,
)
from app_services.infrastructure import RedisService
from app_services.logger import context


class DataProcessor:
    @classmethod
    def _parse_query_params(cls, **query_params) -> str:
        """
        Process queried link.
        """
        link = (
            query_params.get("link")[0]
        )
        if not link.endswith(".json"):
            raise LinkDoesNotContainJsonError(link)

        return link

    @classmethod
    def _should_update_upload_status(cls, processed_rows_number: int) -> bool:
        """
        Check if the current number of processed rows meets the requirements for the file
        processing status update.
        """
        return any([
            settings.UPDATE_STATUS_EVERY_N_ROWS == processed_rows_number,
            settings.UPDATE_STATUS_EVERY_N_ROWS < processed_rows_number and
            processed_rows_number % settings.UPDATE_STATUS_EVERY_N_ROWS == 0,
        ])

    @classmethod
    def process_link(cls, link: str) -> list:
        """
        Get dataset by link as JSON, store it in the file, and return dataset for the further
        operations.
        """
        dataset_as_json = FileLoader().get_dataset_from_link(link)
        FileGenerator().store_dataset(
            filename=link.split(sep='/')[-1],
            content=dataset_as_json
        )
        return dataset_as_json

    @classmethod
    def log_dataset_rows(cls, link: str, dataset: list):
        """
        Iterate over dataset rows, write the content to Kafka/console, and update file
        processing status.
        """
        FileStatusService().log_status(status=FileStatus.in_progress(link))

        for counter, row in enumerate(dataset, start=1):
            context.write_log(
                data={
                    "link": link,
                    "counter": counter,
                    "body": json.dumps({"body": row})
                }
            )

            if settings.UPDATE_STATUS_EVERY_N_ROWS > 0:
                if cls._should_update_upload_status(processed_rows_number=counter):
                    FileStatusService().log_status(status=FileStatus.n_records_uploaded(link, counter))

        FileStatusService().log_status(status=FileStatus.done(link))

    @classmethod
    def run(cls, **query_params) -> None:
        """
        Load dataset and write it to Kafka/console.
        """
        link = DataProcessor._parse_query_params(**query_params)

        if RedisService().is_processed(link):
            FileStatusService().log_status(status=FileStatus.already_processed(link))
        else:
            dataset = cls.process_link(link)
            cls.log_dataset_rows(link, dataset)
