import sys
from typing import Tuple

from django.conf import settings


def should_update_upload_status(processed_rows_number: int) -> bool:
    """
    Check if the current number of processed rows meets the requirements for the file
    processing status update.
    """
    return any([
        settings.DEFAULT_BATCH_SIZE == processed_rows_number,
        settings.DEFAULT_BATCH_SIZE < processed_rows_number and
        processed_rows_number % settings.DEFAULT_BATCH_SIZE == 0,
    ])


def split_dataset_into_chunks(dataset: list, chunk_size: int = settings.DEFAULT_BATCH_SIZE) -> list:
    """
    Split the dataset to chunks of chunk_size and make a list out of them.
    """
    return [dataset[i:i + chunk_size] for i in range(0, len(dataset), chunk_size)]


def calculate_current_max_batch_size_in_bytes(batched_data: list) -> int:
    """
    Calculate size in bytes for each batch and get the greatest chunk size.
    """
    return max([sum([sys.getsizeof(f"{row}") for row in batch]) for batch in batched_data])


def get_optimal_batching(data: list) -> Tuple[int, list]:
    """
    Calculate optimal batching strategy based on your Azure subscription limitations.
    """
    optimal_chunk_size = settings.DEFAULT_BATCH_SIZE
    chunked_data = data

    is_optimal_batching_found = False
    while not is_optimal_batching_found:
        chunked_data = split_dataset_into_chunks(data, chunk_size=optimal_chunk_size)
        current_max_chunk_size_in_bytes = calculate_current_max_batch_size_in_bytes(chunked_data)
        if current_max_chunk_size_in_bytes >= settings.MAX_BATCH_SIZE_IN_BYTES:
            optimal_chunk_size = int(
                settings.DEFAULT_BATCH_SIZE /
                (current_max_chunk_size_in_bytes / settings.MAX_BATCH_SIZE_IN_BYTES)
            )
        else:
            is_optimal_batching_found = True
    return optimal_chunk_size, chunked_data
