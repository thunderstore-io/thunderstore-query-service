import logging
from typing import Literal

from fastapi import APIRouter, Response, status
from httpx2 import HTTPError
from pydantic import BaseModel

from thunderstore_query_service._clickhouse import query_clickhouse

logger = logging.getLogger(__name__)

router = APIRouter()

CACHE_CONTROL = "no-store"
CLICKHOUSE_TIMEOUT_SECONDS = 2.0

type CheckStatus = Literal["ok", "unavailable"]


class LivenessStatus(BaseModel):
    status: Literal["ok"]


class ReadinessChecks(BaseModel):
    clickhouse: CheckStatus


class ReadinessStatus(BaseModel):
    status: CheckStatus
    checks: ReadinessChecks


async def _clickhouse_status() -> CheckStatus:
    try:
        await query_clickhouse("SELECT 1", timeout=CLICKHOUSE_TIMEOUT_SECONDS)
    except HTTPError:
        logger.exception("ClickHouse readiness check failed")
        return "unavailable"
    return "ok"


@router.get("/healthz")
async def get_liveness(response: Response) -> LivenessStatus:
    response.headers["Cache-Control"] = CACHE_CONTROL
    return LivenessStatus(status="ok")


@router.get("/readyz")
async def get_readiness(response: Response) -> ReadinessStatus:
    clickhouse = await _clickhouse_status()

    response.headers["Cache-Control"] = CACHE_CONTROL
    if clickhouse != "ok":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessStatus(
        status=clickhouse, checks=ReadinessChecks(clickhouse=clickhouse)
    )
