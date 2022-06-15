from django.conf import settings


def should_update_upload_status(processed_rows_number: int) -> bool:
    """
    Check if the current number of processed rows meets the requirements for the file
    processing status update.
    """
    return any([
        settings.BATCH_SIZE == processed_rows_number,
        settings.BATCH_SIZE < processed_rows_number and
        processed_rows_number % settings.BATCH_SIZE == 0,
    ])


def split_dataset_into_chunks(dataset: list, chunk_size: int = settings.BATCH_SIZE) -> list:
    """
    Split the dataset to chunks of chunk_size and make a list out of them.
    """
    return [dataset[i:i + chunk_size] for i in range(0, len(dataset), chunk_size)]
