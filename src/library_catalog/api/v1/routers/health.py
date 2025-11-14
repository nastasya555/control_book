from fastapi import APIRouter

from ..schemas.common import HealthResponse

health_router = APIRouter()


@health_router.get("/health", response_model=HealthResponse)
def health_check():
    """Проверка здоровья API."""
    return HealthResponse(status="ok")

