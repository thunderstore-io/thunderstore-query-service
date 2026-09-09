import os
from pathlib import Path

from fastapi import APIRouter, Response
from httpx2 import AsyncClient, BasicAuth
from pydantic import AwareDatetime, BaseModel

from thunderstore_query_service._sql_utils import load_sql_template

router = APIRouter(prefix="/api/charts/downloads")

DOWNLOAD_HISTORY_QUERY = load_sql_template(
    Path(__file__).parent / "get_download_history.sql"
)

CACHE_CONTROL = "public, max-age=300"


class DownloadHistoryPoint(BaseModel):
    hour: AwareDatetime
    downloads: int


@router.get("/{namespace}/{package}")
async def get_download_history(
    namespace: str, package: str, response: Response
) -> list[DownloadHistoryPoint]:
    async with AsyncClient() as client:
        clickhouse_response = await client.post(
            f"{os.getenv('CLICKHOUSE_URI')}",
            auth=BasicAuth(
                str(os.getenv("CLICKHOUSE_USER")), str(os.getenv("CLICKHOUSE_PASSWORD"))
            ),
            content=DOWNLOAD_HISTORY_QUERY.substitute(
                table_prefix=os.getenv("TABLE_PREFIX")
            ),
            params={
                "default_format": "JSON",
                "date_time_output_format": "iso",
                "param_namespace": namespace,
                "param_package": package,
            },
        )
        clickhouse_response.raise_for_status()
        response.headers["Cache-Control"] = CACHE_CONTROL
        return clickhouse_response.json()["data"]
