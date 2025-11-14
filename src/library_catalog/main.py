from fastapi import FastAPI
import uvicorn

from .api.v1.routers import books, health
from .core.config import settings
from .core.error_handlers import domain_exception_handler
from .domain.exceptions import DomainException

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    docs_url=settings.docs_url,
)
app.add_exception_handler(DomainException, domain_exception_handler)

# API v1 routes
app.include_router(
    books.book_router,
    prefix=f"{settings.api_v1_prefix}/books",
    tags=["books"],
)
app.include_router(
    health.health_router,
    prefix=settings.api_v1_prefix,
    tags=["health"],
)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
