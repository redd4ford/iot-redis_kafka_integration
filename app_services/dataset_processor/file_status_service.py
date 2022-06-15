from django.conf import settings
from django.utils import timezone
from injector import inject

from app_services.infrastructure import RedisService


class FileStatusService:
    @inject
    def __init__(self, redis_service: RedisService = RedisService()):
        self.redis_service = redis_service
        super().__init__()

    def log_status(self, link: str, status: str):
        """
        Log file processing status in Redis, and also console if Kafka is not integrated.
        """
        self.redis_service.log_status({'key': link, 'value': status})
        if not settings.WRITE_TO_KAFKA:
            print(f"{timezone.now()} --- [{link}] = {status}")
