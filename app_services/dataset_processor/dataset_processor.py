from typing import Tuple

from api.constants import FileStatus
from api.exceptions import LinkDoesNotContainJsonError
from app_services.dataset_processor import (
    FileLoader,
    FileGenerator,
    FileStatusService,
)
from app_services.infrastructure import RedisService
from app_services.logger import context


class DatasetProcessor:
    @classmethod
    def _parse_query_params(cls, **query_params) -> Tuple[str, bool, int]:
        """
        Process queried link and ignore_status parameters.
        """
        link = (
            query_params.get("link")[0]
        )
        if not link.endswith(".json"):
            raise LinkDoesNotContainJsonError(link)
        ignore_status = (
            query_params.get("ignore_status")[0].lower() == 'true'
        )
        rows_to_get = (
            int(query_params.get("rows_to_get")[0])
        )

        return link, ignore_status, rows_to_get

    @classmethod
    def process_link(cls, link: str, rows_to_get: int) -> list:
        """
        Get dataset by link as JSON, store it in the file, and return dataset for the further
        operations.
        """
        dataset_as_json = FileLoader().get_dataset_from_link(link, rows_to_get)
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
        FileStatusService().log_status(link, status=FileStatus.IN_PROGRESS)
        context.write_log(link, dataset)
        FileStatusService().log_status(link, status=FileStatus.DONE)

    @classmethod
    def run(cls, **query_params) -> str:
        """
        Load dataset and write it to Kafka/console.
        """
        link, ignore_status, rows_to_get = DatasetProcessor._parse_query_params(**query_params)

        if RedisService().is_processed(link) and not ignore_status:
            FileStatusService().log_status(link, status=FileStatus.ALREADY_PROCESSED)
        else:
            dataset = cls.process_link(link, rows_to_get)
            cls.log_dataset_rows(link, dataset)
        return RedisService().get(link)
