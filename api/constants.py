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

    @classmethod
    def _build_status(cls, link_to_file: str, status: str) -> dict:
        """
        Return processing status for a specific file as a key-value pair suitable for Redis
        caching.
        """
        return {"key": link_to_file, "value": status}

    @classmethod
    def in_progress(cls, link_to_file: str) -> dict:
        """
        Build IN_PROGRESS status for a file.
        """
        return cls._build_status(link_to_file, status=FileStatus.IN_PROGRESS)

    @classmethod
    def n_records_uploaded(cls, link_to_file: str, counter: int) -> dict:
        """
        Build N_RECORDS_UPLOADED status for a file.
        """
        return cls._build_status(link_to_file, status=FileStatus.N_RECORDS_UPLOADED(counter))

    @classmethod
    def done(cls, link_to_file: str) -> dict:
        """
        Build DONE status for a file.
        """
        return cls._build_status(link_to_file, status=FileStatus.DONE)

    @classmethod
    def already_processed(cls, link_to_file: str) -> dict:
        """
        Build ALREADY_PROCESSED status for a file.
        """
        return cls._build_status(link_to_file, status=FileStatus.ALREADY_PROCESSED)
