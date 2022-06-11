class FileStatus:
    IN_PROGRESS = "In progress"
    N_RECORDS_UPLOADED = lambda number_of_records_uploaded: f"{number_of_records_uploaded} records uploaded"
    DONE = "Done"
    ALREADY_PROCESSED = "Already processed"
