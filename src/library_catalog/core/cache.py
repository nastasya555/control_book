import hashlib
import json
import time
from functools import wraps
from typing import Any, Callable, Optional


class CacheService:
    """Сервис кэширования с поддержкой декораторов."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[Any, float]] = {}

    def _generate_cache_key(
        self, func_name: str, args: tuple, kwargs: dict
    ) -> str:
        """Генерирует ключ кэша на основе имени функции и аргументов."""
        key_data = {
            "func": func_name,
            "args": str(args),
            "kwargs": json.dumps(kwargs, sort_keys=True, default=str),
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def get(self, key: str, ttl: Optional[float] = None) -> Optional[Any]:
        """Получить значение из кэша."""
        if key not in self._cache:
            return None

        value, timestamp = self._cache[key]
        if ttl and (time.time() - timestamp) > ttl:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Установить значение в кэш."""
        self._cache[key] = (value, time.time())

    def clear(self) -> None:
        """Очистить весь кэш."""
        self._cache.clear()

    def cached(self, ttl: int = 3600):
        """Декоратор для кэширования результатов функции."""

        def decorator(func: Callable):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                key = self._generate_cache_key(func.__name__, args, kwargs)

                # Проверяем кэш
                cached_value = self.get(key, ttl=ttl)
                if cached_value is not None:
                    return cached_value

                # Вызываем функцию
                result = await func(*args, **kwargs)

                # Сохраняем в кэш
                self.set(key, result, ttl=ttl)
                return result

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                key = self._generate_cache_key(func.__name__, args, kwargs)

                # Проверяем кэш
                cached_value = self.get(key, ttl=ttl)
                if cached_value is not None:
                    return cached_value

                # Вызываем функцию
                result = func(*args, **kwargs)

                # Сохраняем в кэш
                self.set(key, result, ttl=ttl)
                return result

            # Возвращаем async или sync обёртку в зависимости от типа функции
            import inspect

            if inspect.iscoroutinefunction(func):
                return async_wrapper
            return sync_wrapper

        return decorator


# Глобальный экземпляр кэша
cache_service = CacheService()