import os
from typing import Any

from fastapi import APIRouter
from httpx2 import AsyncClient, BasicAuth

router = APIRouter(prefix="/api/charts/downloads")


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
            content=(
                "WITH versions AS ( "
                "    SELECT id "
                f"    FROM analytics.thunderstore_{os.getenv('TABLE_PREFIX')}_model_package_version_update_v1 mpvu "
                "    WHERE mpvu.namespace__name = {namespace:String} "
                "    AND mpvu.name = {package:String} "
                ") "
                "SELECT "
                "    toStartOfHour(toDateTime(apd.timestamp)) AS hour, "
                "    count() AS downloads "
                f"FROM analytics.thunderstore_{os.getenv('TABLE_PREFIX')}_analytics_package_download_v1 apd "
                "WHERE timestamp >= toStartOfHour(now()) - INTERVAL 7 DAY "
                "  AND apd.version_id IN (SELECT id FROM versions) "
                "GROUP BY hour "
                "ORDER BY hour"
            ),
            params={
                "default_format": "JSON",
                "param_namespace": namespace,
                "param_package": package,
            },
        )
        response.raise_for_status()
        return response.json()["data"]
