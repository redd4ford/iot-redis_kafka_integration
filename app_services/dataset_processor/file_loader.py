import json
from urllib.error import HTTPError
from urllib.request import urlopen

from api.exceptions import (
    HttpErrorOnProcessingError,
    JsonDecodeError,
)


class FileLoader:
    @classmethod
    def get_dataset_from_link(cls, link: str, rows_to_get: int) -> list:
        """
        Fetch the dataset as JSON by link.
        """
        try:
            limit = rows_to_get if rows_to_get < 200 else 200
            processed_rows_as_json = []
            offset = 0
            while len(processed_rows_as_json) < rows_to_get:
                dataset_patch = urlopen(f'{link}?$limit={limit}&$offset={offset}')

                try:
                    dataset_batch_as_json = json.loads(dataset_patch.read())
                    if not dataset_batch_as_json:
                        # rows_to_get is greater than the actual dataset size
                        return processed_rows_as_json
                except json.decoder.JSONDecodeError:
                    if not processed_rows_as_json:
                        raise JsonDecodeError(link)
                    else:
                        return processed_rows_as_json

                processed_rows_as_json += dataset_batch_as_json
                if len(processed_rows_as_json) > rows_to_get:
                    # the last batch was greater than needed
                    processed_rows_as_json = processed_rows_as_json[:rows_to_get]

                offset += limit
        except HTTPError as e:
            raise HttpErrorOnProcessingError(link, f"{e}")

        return processed_rows_as_json
