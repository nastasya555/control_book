from typing import Any, Dict, Optional, Tuple

from ..base_client import BaseApiClient, ApiClientError


class JsonBinClient(BaseApiClient):
    """Мини‑клиент jsonbin.io для чтения/записи целого JSON‑объекта с ETag.

    Ожидается схема: {"books": [...]}.
    """

    def __init__(self, base_url: str, bin_id: str, api_key: str) -> None:
        super().__init__(base_url)
        self.bin_id = bin_id
        self.api_key = api_key
        self._headers = {"X-Master-Key": self.api_key}

    def client_name(self) -> str:
        return "jsonbin"

    def _bin_url(self) -> str:
        return f"{self.base_url}/b/{self.bin_id}"

    def read_all(self) -> Tuple[Dict[str, Any], Optional[str]]:
        """Прочитать весь объект и вернуть (record, etag)."""
        raw = self._request(
            "GET", "/b/" + self.bin_id, headers=self._headers, return_json=False
        )
        payload = raw.json() if raw else {}
        record = payload.get("record", payload)
        etag = raw.headers.get("etag") if raw is not None else None
        return record, etag

    def write_all(self, record: Dict[str, Any], etag: Optional[str]) -> str:
        """Перезаписать объект целиком. Если передан etag — используем If-Match.

        Возвращает новый etag из ответа.
        """
        headers = dict(self._headers)
        headers["Content-Type"] = "application/json"
        if etag:
            headers["If-Match"] = etag
        raw = self._request(
            "PUT", "/b/" + self.bin_id, headers=headers, json=record, return_json=False
        )
        if raw.status_code == 412:
            raise ApiClientError(
                "jsonbin: ETag mismatch (412). Re-read and retry.", status=412
            )
        return raw.headers.get("etag", "")

