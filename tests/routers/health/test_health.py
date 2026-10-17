import httpx2
import pytest
from fastapi.testclient import TestClient

from tests._utils import mock_clickhouse, mock_clickhouse_error

CLICKHOUSE_OK = {"data": [{"1": 1}], "rows": 1}


def test_readiness_ok_when_clickhouse_is_reachable(client: TestClient):
    with mock_clickhouse(CLICKHOUSE_OK):
        response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"clickhouse": "ok"}}


def test_readiness_unavailable_when_clickhouse_is_unreachable(client: TestClient):
    with mock_clickhouse_error(httpx2.ConnectError("connection refused")):
        response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json()["checks"]["clickhouse"] == "unavailable"


@pytest.mark.parametrize("path", ["/healthz", "/readyz"])
def test_probes_are_never_cached(client: TestClient, path: str):
    with mock_clickhouse(CLICKHOUSE_OK):
        response = client.get(path)

    assert response.headers["Cache-Control"] == "no-store"
