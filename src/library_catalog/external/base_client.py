from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, Mapping, Optional

import httpx
from circuitbreaker import circuit

from ..domain.exceptions import ExternalServiceError


class BaseApiClient(ABC):
    """Базовый клиент для HTTP API.

    Держит общую конфигурацию, retry и Circuit Breaker.
    Наследники реализуют специфичные методы.
    """

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
        default_headers: Optional[Mapping[str, str]] = None,
        retries: int = 2,
        backoff: float = 0.5,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = dict(default_headers or {})
        self.retries = max(0, retries)
        self.backoff = max(0.0, backoff)
        self._client = httpx.Client(timeout=self.timeout)
        self.log = logger or logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str:
        """Имя сервиса для логирования (напр., 'openlibrary', 'jsonbin')."""

    # --- internal helpers ---
    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    def _merge_headers(
        self, headers: Optional[Mapping[str, str]]
    ) -> Dict[str, str]:
        merged = dict(self.default_headers)
        if headers:
            merged.update(headers)
        return merged

    @circuit(failure_threshold=5, recovery_timeout=60)
    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Mapping[str, Any]] = None,
        headers: Optional[Mapping[str, str]] = None,
        json: Any = None,
        expected_status: int | tuple[int, ...] = (200,),
        return_json: bool = True,
    ) -> Any:
        url = self._build_url(path)
        hdrs = self._merge_headers(headers)

        attempt = 0
        while True:
            try:
                self.log.debug("%s %s params=%s", method, url, params)
                resp = self._client.request(
                    method, url, params=params, headers=hdrs, json=json
                )
            except httpx.RequestError as exc:
                self.log.warning(
                    "%s network error: %s", self.client_name(), exc
                )
                if attempt >= self.retries:
                    raise ExternalServiceError(
                        f"{self.client_name()} network error"
                    ) from exc
                time.sleep(self.backoff * (2**attempt))
                attempt += 1
                continue

            ok = resp.status_code in (
                expected_status
                if isinstance(expected_status, tuple)
                else (expected_status,)
            )
            if not ok:
                body: Any
                try:
                    body = resp.json()
                except Exception:
                    body = resp.text
                msg = (
                    f"{self.client_name()} HTTP {resp.status_code} "
                    f"{method} {url}: {body}"
                )
                # 5xx можно повторить
                if 500 <= resp.status_code < 600 and attempt < self.retries:
                    self.log.warning(
                        "%s retry on %s", self.client_name(), msg
                    )
                    time.sleep(self.backoff * (2**attempt))
                    attempt += 1
                    continue
                self.log.error(msg)
                raise ExternalServiceError(msg)

            if not return_json:
                return resp
            try:
                return resp.json()
            except ValueError as exc:
                raise ExternalServiceError(
                    f"{self.client_name()} invalid JSON response"
                ) from exc

    # --- shortcuts ---
    def _get(self, path: str, **kwargs) -> Any:
        return self._request("GET", path, **kwargs)

    def _post(self, path: str, **kwargs) -> Any:
        return self._request("POST", path, **kwargs)

    def _put(self, path: str, **kwargs) -> Any:
        return self._request("PUT", path, **kwargs)

    def _patch(self, path: str, **kwargs) -> Any:
        return self._request("PATCH", path, **kwargs)

    def _delete(self, path: str, **kwargs) -> Any:
        return self._request("DELETE", path, **kwargs)

    # lifecycle
    def close(self) -> None:
        self._client.close()
