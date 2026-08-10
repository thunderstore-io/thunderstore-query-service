import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from httpx2 import AsyncClient, BasicAuth

from thunderstore_query_service._sql_utils import load_sql_template

router = APIRouter(prefix="/api/charts/downloads")

DOWNLOAD_HISTORY_QUERY = load_sql_template(
    Path(__file__).parent / "get_download_history.sql"
)


@router.get("/{namespace}/{package}")
async def get_mod_download_url(namespace: str, package: str) -> list[dict[str, Any]]:
    """
    Retrieves JSON chart download history for a given namespace and package.
    """
    async with AsyncClient() as client:
        response = await client.post(
            f"{os.getenv('CLICKHOUSE_URI')}",
            auth=BasicAuth(
                str(os.getenv("CLICKHOUSE_USER")), str(os.getenv("CLICKHOUSE_PASSWORD"))
            ),
            content=DOWNLOAD_HISTORY_QUERY.substitute(
                table_prefix=os.getenv("TABLE_PREFIX")
            ),
            params={
                "default_format": "JSON",
                "param_namespace": namespace,
                "param_package": package,
            },
        )
        response.raise_for_status()
        return response.json()["data"]
