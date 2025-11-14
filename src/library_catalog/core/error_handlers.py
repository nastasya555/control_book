from __future__ import annotations

from fastapi import Request, status
from fastapi.responses import JSONResponse

from ..domain.exceptions import (
    DomainException,
    BookNotFoundException,
    ExternalServiceError,
    DatabaseError,
)


async def domain_exception_handler(
    request: Request, exc: DomainException
) -> JSONResponse:
    """Единое место обработки доменных исключений."""

    if isinstance(exc, BookNotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    if isinstance(exc, ExternalServiceError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": str(exc)},
        )

    if isinstance(exc, DatabaseError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc)},
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )
