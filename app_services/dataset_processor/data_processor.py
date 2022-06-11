import json

from django.conf import settings

from api.constants import FileStatus
from api.exceptions import LinkDoesNotContainJsonError
from app_services.dataset_processor.file_loader import FileLoader
from app_services.dataset_processor.file_generator import FileGenerator
from app_services.infrastructure import RedisService
from app_services.logger import context


class DataProcessor:
    @classmethod
    def _parse_query_params(cls, **query_params) -> str:
        link = (
            query_params.get("link")[0]
        )
        if not link.endswith(".json"):
            raise LinkDoesNotContainJsonError(link)

        return link

    @classmethod
    def process_file(cls, link: str) -> list:
        data_as_json = FileLoader().get_dataset_from_link(link)
        FileGenerator().store_dataset(
            filename=link.split(sep='/')[-1],
            content=data_as_json
        )

        return data_as_json

    @classmethod
    def log_dataset_rows(cls, link: str, dataset: list):
        RedisService().log_status(data={link: FileStatus.IN_PROGRESS})
        for counter, row in enumerate(dataset, start=1):
            context.write_log(
                data={
                    "link": link,
                    "counter": counter,
                    "body": json.dumps({"body": row})
                }
            )

            if settings.UPDATE_UPLOAD_STATUS_EVERY_N_ROWS > 0:
                update_every_n_rows = settings.UPDATE_UPLOAD_STATUS_EVERY_N_ROWS
                if any([
                    update_every_n_rows < counter and counter % update_every_n_rows == 0,
                    update_every_n_rows >= counter and update_every_n_rows % counter == 0
                ]):
                    RedisService().log_status(data={link: FileStatus.N_RECORDS_UPLOADED(counter)})

        RedisService().log_status(data={link: FileStatus.DONE})

    @classmethod
    def process(cls, **query_params) -> None:
        """
        Load dataset, write it to Kafka or console, add file processing status in Redis.
        """
        link = DataProcessor._parse_query_params(**query_params)

        if RedisService().is_processed(link):
            RedisService().log_status(data={link: FileStatus.ALREADY_PROCESSED})
        else:
            dataset = cls.process_file(link)
            cls.log_dataset_rows(link, dataset)
