"""Вспомогательные утилиты для приложения."""

from typing import Any, Dict, Optional


def sanitize_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """Удалить None значения из словаря."""
    return {k: v for k, v in data.items() if v is not None}


def truncate_string(text: str, max_length: int = 100) -> str:
    """Обрезать строку до максимальной длины."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def safe_int(value: Any, default: int = 0) -> int:
    """Безопасное преобразование в int."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Безопасное преобразование в float."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

