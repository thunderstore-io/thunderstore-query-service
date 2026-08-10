import json
from datetime import UTC, datetime
from types import TracebackType
from typing import Any, Self

import httpx2


def to_datetime64(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def to_datetime(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")


class ClickHouseHttp:
    def __init__(self, base_url: str, username: str, password: str) -> None:
        self._client = httpx2.Client(
            base_url=base_url,
            auth=httpx2.BasicAuth(username, password),
            timeout=30.0,
        )

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def execute(self, sql: str) -> str:
        response = self._client.post("/", content=sql.encode())
        response.raise_for_status()
        return response.text

    def insert(self, table: str, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        payload = "\n".join(json.dumps(row) for row in rows)
        self.execute(f"INSERT INTO {table} FORMAT JSONEachRow\n{payload}")
