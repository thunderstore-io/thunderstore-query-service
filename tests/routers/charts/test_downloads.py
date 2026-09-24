from fastapi.testclient import TestClient

from tests._utils import mock_clickhouse
from thunderstore_query_service.main import app

MOCK_DATA = {
    "data": [
        {"hour": "2024-08-01T00:00:00Z", "downloads": 10},
        {"hour": "2024-08-01T01:00:00Z", "downloads": 0},
    ],
    "rows": 2,
}


def test_download_history_success(client: TestClient):
    with mock_clickhouse(MOCK_DATA):
        response = client.get("/api/charts/downloads/test-namespace/test-package")

    assert response.status_code == 200
    assert response.json() == [
        {"hour": "2024-08-01T00:00:00Z", "downloads": 10},
        {"hour": "2024-08-01T01:00:00Z", "downloads": 0},
    ]


def test_download_history_is_cacheable_for_a_minute(client: TestClient):
    with mock_clickhouse(MOCK_DATA):
        response = client.get("/api/charts/downloads/test-namespace/test-package")

    assert response.headers["Cache-Control"] == "public, max-age=300"


def test_download_history_does_not_cache_an_upstream_failure():
    with (
        TestClient(app, raise_server_exceptions=False) as client,
        mock_clickhouse({}, status_code=500),
    ):
        response = client.get("/api/charts/downloads/test-namespace/test-package")

    assert response.status_code == 500
    assert "Cache-Control" not in response.headers
