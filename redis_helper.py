import os

import redis


class RedisError(Exception):
    """Custom exception for Redis errors."""


CACHE_TTL = 3

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
PORT = os.getenv("REDIS_PORT", 6379)


class RedisClient:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(RedisClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.client = None

    def connect(self) -> None:
        """Connect to Redis Sentinel and get master instance."""
        if self.client is None:
            self.client = redis.Redis(
                host=REDIS_HOST,
                port=PORT,
                decode_responses=True,
            )

    def get(self, key: str):
        self.connect()
        result = self.client.get(key)
        return result

    def set(self, key: str, value: str, ex: int = CACHE_TTL):
        self.connect()
        self.client.set(key, value, ex=ex)

    def incr(self, key: str):
        self.connect()
        try:
            result = self.client.incr(key)
            return result
        except redis.RedisError as e:
            raise RedisError(str(e))

    def expire(self, key: str, ex: int):
        self.connect()
        try:
            self.client.expire(key, ex)
        except redis.RedisError as e:
            raise RedisError(str(e))
