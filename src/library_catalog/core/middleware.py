import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования запросов."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time

        # Логирование только в development
        if settings.debug:
            print(
                f"{request.method} {request.url.path} - "
                f"{response.status_code} - {process_time:.3f}s"
            )

        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """Простое CORS middleware."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        origin = request.headers.get("origin")
        if origin in settings.cors_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response

