import logging
import sys
from typing import Optional

from .config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """Настройка логирования для приложения."""
    level = log_level or settings.log_level
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Получить логгер с заданным именем."""
    return logging.getLogger(name)

