import os

from httpx2 import AsyncClient, BasicAuth, Response

DEFAULT_TIMEOUT_SECONDS = 5.0


async def query_clickhouse(
    sql: str,
    params: dict[str, str] | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> Response:
    async with AsyncClient() as client:
        response = await client.post(
            str(os.getenv("CLICKHOUSE_URI")),
            auth=BasicAuth(
                str(os.getenv("CLICKHOUSE_USER")), str(os.getenv("CLICKHOUSE_PASSWORD"))
            ),
            content=sql,
            params=params,
            timeout=timeout,
        )
    response.raise_for_status()
    return response
