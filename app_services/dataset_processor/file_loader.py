import json
from urllib.error import HTTPError
from urllib.request import urlopen

from django.conf import settings

from django_app.exceptions import (
    HttpErrorOnProcessingError,
    JsonDecodeError,
)


class FileLoader:
    @classmethod
    def get_dataset_from_link(cls, link: str, requested_number_of_records: int) -> list[dict]:
        """
        Fetch the dataset as JSON by link.
        """
        try:
            limit = min([requested_number_of_records, settings.DEFAULT_BATCH_SIZE])
            processed_records = []
            offset = 0

            while len(processed_records) < requested_number_of_records:
                dataset_batch = urlopen(url=f'{link}?$limit={limit}&$offset={offset}')

                try:
                    dataset_batch_as_json = json.loads(dataset_batch.read())
                    if dataset_batch_as_json is None:
                        # requested_number_of_records is greater than the actual dataset size
                        return processed_records
                except json.decoder.JSONDecodeError:
                    if processed_records is not None:
                        return processed_records
                    raise JsonDecodeError(link)

                processed_records += dataset_batch_as_json
                if len(processed_records) > requested_number_of_records:
                    processed_records = processed_records[:requested_number_of_records]
                    break

                offset += limit
        except HTTPError as e:
            raise HttpErrorOnProcessingError(link, f"{e}")

        return processed_records
