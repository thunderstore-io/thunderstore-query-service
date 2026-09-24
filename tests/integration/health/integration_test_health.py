import pytest
from fastapi.testclient import TestClient


def test_readiness_ok_against_clickhouse(client: TestClient):
    response = client.get("/readyz")

    assert response.status_code == 200
    assert response.json()["checks"] == {"clickhouse": "ok"}


def test_readiness_unavailable_with_bad_credentials(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "wrong-password")

    response = client.get("/readyz")

    assert response.status_code == 503
    assert response.json()["checks"]["clickhouse"] == "unavailable"
