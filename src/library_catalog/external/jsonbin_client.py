import os
from typing import Any, Dict, Tuple

import httpx


class JsonBinClient:
    """Мини‑клиент jsonbin.io для чтения/записи целого JSON‑объекта с ETag.

    Ожидается схема: {"books": [...]}.
    """

    def __init__(self, base_url: str, bin_id: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.bin_id = bin_id
        self.api_key = api_key
        self._headers = {"X-Master-Key": self.api_key}

    def _bin_url(self) -> str:
        return f"{self.base_url}/b/{self.bin_id}"

    def read_all(self) -> Tuple[Dict[str, Any], str | None]:
        """Прочитать весь объект и вернуть (record, etag)."""
        url = self._bin_url()
        with httpx.Client(timeout=10) as client:
            r = client.get(url, headers=self._headers)
            r.raise_for_status()
            payload = r.json()
            record = payload.get("record", payload)
            etag = r.headers.get("etag")
            return record, etag

    def write_all(self, record: Dict[str, Any], etag: str | None) -> str:
        """Перезаписать объект целиком. Если передан etag — используем If-Match.

        Возвращает новый etag из ответа.
        """
        url = self._bin_url()
        headers = dict(self._headers)
        headers["Content-Type"] = "application/json"
        if etag:
            headers["If-Match"] = etag
        with httpx.Client(timeout=10) as client:
            r = client.put(url, headers=headers, json=record)
            if r.status_code == 412:
                raise RuntimeError("jsonbin: ETag mismatch (412). Re-read and retry.")
            r.raise_for_status()
            new_etag = r.headers.get("etag", "")
            return new_etag


