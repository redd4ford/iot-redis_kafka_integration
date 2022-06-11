from django.conf import settings
from redis.client import Redis

from app_services.logger import context


class RedisService:
    def __init__(self, redis_server: Redis = settings.REDIS_SERVER):
        self.redis = redis_server if redis_server else None

    def is_processed(self, link: str) -> bool:
        # TODO(redd4ford): remove these and make the app drop when there is no Redis server
        if self.redis:
            return self.redis.get(link) is not None
        else:
            return False

    def set(self, key: str, value: str) -> None:
        if self.redis:
            self.redis.set(key, value)

    def get(self, key: str) -> None:
        if self.redis:
            self.redis.get(key)

    def log_status(self, data: dict):
        if self.redis:
            self.set(**data)
            if not settings.WRITE_TO_KAFKA:
                context.write_log(**data)
