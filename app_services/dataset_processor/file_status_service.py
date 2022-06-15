from django.conf import settings
from injector import inject

from app_services.infrastructure import RedisService
from app_services.logger import context


class FileStatusService:
    @inject
    def __init__(self, redis_service: RedisService = RedisService()):
        self.redis_service = redis_service
        super().__init__()

    def log_status(self, status: dict):
        """
        Log file processing status in Redis, and also console if Kafka is not integrated.
        """
        self.redis_service.log_status(status)
        if not settings.WRITE_TO_KAFKA:
            context.write_log(status, is_status=True)
