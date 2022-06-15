class FileStatus:
    """
    File processing status.
    IN_PROGRESS: file processing has just started
    N_RECORDS_UPLOADED: used when there is a need to update status every N rows
        (see settings.UPDATE_STATUS_EVERY_N_ROWS)
    DONE: file processing has ended
    ALREADY_PROCESSED: link to the file is stored in Redis and thus does not need to be processed
    """
    IN_PROGRESS = "In progress"
    N_RECORDS_UPLOADED = lambda number_of_records_uploaded: f"{number_of_records_uploaded} records uploaded"
    DONE = "Done"
    ALREADY_PROCESSED = "Already processed"
