import time
from datetime import timedelta
from typing import Callable, Union

from fastapi import Request
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from redis_helper import RedisClient


class RedisRateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Middleware for rate limiting based on Redis.
    """

    def __init__(
        self,
        app,
        redis_client: RedisClient,
        limit: int,
        window: Union[int, timedelta] = timedelta(minutes=1),
    ):
        super().__init__(app)
        self.redis_client = redis_client
        self.limit = limit
        self.window = window

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:

        client_ip = request.client.host

        key = f"{client_ip}:{int(time.time() // self.window)}"

        request_count = self.redis_client.incr(key)
        if request_count is None:
            return PlainTextResponse("Internal server error.", status_code=500)

        if request_count == 1:
            self.redis_client.expire(key, self.window)

        if request_count > self.limit:
            return PlainTextResponse(
                "Rate limit exceeded. Try again later.", status_code=429
            )

        response = await call_next(request)
        return response
