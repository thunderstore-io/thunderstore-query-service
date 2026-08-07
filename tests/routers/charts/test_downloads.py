from fastapi.testclient import TestClient

from tests._utils import mock_http
from thunderstore_query_service.routers.charts import downloads


def test_download_history_success(client: TestClient):

    MOCK_DATA = {
        "data": [
            {"hour": "2024-08-01 00:00:00", "downloads": "10"},
            {"hour": "2024-08-01 01:00:00", "downloads": "5"},
        ],
        "rows": 2,
    }

    with mock_http(MOCK_DATA, downloads):
        response = client.get("/api/charts/downloads/test-namespace/test-package")

    assert response.status_code == 200
    assert response.json() == [
        {"hour": "2024-08-01 00:00:00", "downloads": "10"},
        {"hour": "2024-08-01 01:00:00", "downloads": "5"},
    ]
