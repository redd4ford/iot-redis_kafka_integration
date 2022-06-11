import json
import os

from django.conf import settings


class FileGenerator:
    @classmethod
    def create_datasets_folder(cls) -> None:
        if not os.path.exists(settings.DATASETS_URL):
            os.mkdir(settings.DATASETS_URL)

    @classmethod
    def store_dataset(cls, filename: str, content: list) -> bool:
        FileGenerator.create_datasets_folder()

        with open(os.path.join(settings.DATASETS_URL, filename), 'w') as f:
            json.dump(content, f)

        return True
