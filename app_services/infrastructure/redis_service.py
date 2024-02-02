from typing import Optional

from django.conf import settings
from injector import inject
from redis.client import Redis

from django_app.exceptions import (
    FileStatusNotFoundError,
    LinkDoesNotContainJsonError,
)


class RedisService:
    @inject
    def __init__(self, redis_server: Redis = settings.REDIS_SERVER):
        self.redis = redis_server if redis_server else None
        super().__init__()

    def is_processed(self, link: str) -> bool:
        return self.get(link) is not None

    def set(self, key: str, value: str) -> None:
        self.redis.hset('file', key, value)

    def get(self, key: str) -> Optional[str]:
        if not key.endswith(".json"):
            raise LinkDoesNotContainJsonError(key)

        status = self.redis.hget('file', key)
        if status:
            return status.decode("utf-8")
        else:
            raise FileStatusNotFoundError

    def log_status(self, data: dict):
        self.set(**data)
