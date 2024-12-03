from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from asyncio import Semaphore

class ConcurrentRequestMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_concurrent: int = 15):
        super().__init__(app)
        self._semaphore = Semaphore(max_concurrent)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ):
        async with self._semaphore:
            return await call_next(request)