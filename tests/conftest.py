import pytest
from fastapi.testclient import TestClient

from thunderstore_query_service.main import app


@pytest.fixture(autouse=True)
def _clickhouse_env(monkeypatch):
    monkeypatch.setenv("CLICKHOUSE_URI", "https://clickhouse.test")
    monkeypatch.setenv("CLICKHOUSE_USER", "test-user")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "test-password")
    monkeypatch.setenv("TABLE_PREFIX", "test")


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
