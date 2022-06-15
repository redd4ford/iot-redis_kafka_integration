class FileStatus:
    """
    File processing status.
    """
    # file processing has just started
    IN_PROGRESS: str = "In progress"
    # used when there is a need to update status every N rows
    # (see settings.UPDATE_STATUS_EVERY_N_ROWS)
    N_RECORDS_UPLOADED = (
        lambda number_of_records_uploaded: f"{number_of_records_uploaded} records uploaded"
    )
    # file processing has ended
    DONE: str = "Done"
    # link to the file is stored in Redis and thus does not need to be processed
    ALREADY_PROCESSED: str = "Already processed"
