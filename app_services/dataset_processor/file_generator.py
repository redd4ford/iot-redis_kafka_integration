import json
import os

from django.conf import settings


class FileGenerator:
    @classmethod
    def create_datasets_folder(cls) -> None:
        """
        Create datasets/ in the file system.
        """
        if not os.path.exists(settings.DATASETS_URL):
            os.mkdir(settings.DATASETS_URL)

    @classmethod
    def store_dataset(cls, filename: str, content: list) -> str:
        """
        Store the parsed JSON in a file under datasets/ folder.
        """
        FileGenerator.create_datasets_folder()
        filepath = os.path.join(settings.DATASETS_URL, filename)

        with open(filepath, 'w') as file:
            json.dump(content, file)

        return filepath
