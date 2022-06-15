import json
from urllib.error import HTTPError
from urllib.request import urlopen

from api.exceptions import (
    HttpErrorOnProcessingError,
    JsonDecodeError,
)


class FileLoader:
    @classmethod
    def get_dataset_from_link(cls, link: str) -> list:
        """
        Fetch the dataset as JSON by link.
        """
        try:
            response = urlopen(link)
        except HTTPError as e:
            raise HttpErrorOnProcessingError(link, f"{e}")
        try:
            data_as_json = json.loads(response.read())
        except json.decoder.JSONDecodeError:
            raise JsonDecodeError(link)

        return data_as_json
