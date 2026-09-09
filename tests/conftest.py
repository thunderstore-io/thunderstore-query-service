from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from thunderstore_query_service.main import app

INTEGRATION_DIR = Path(__file__).parent / "integration"


def pytest_collection_modifyitems(config, items):
    for item in items:
        path = getattr(item, "path", None)
        if path is not None and path.is_relative_to(INTEGRATION_DIR):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(autouse=True)
def _clickhouse_env(request, monkeypatch):
    if "integration" in request.keywords:
        return
    monkeypatch.setenv("CLICKHOUSE_URI", "https://clickhouse.test")
    monkeypatch.setenv("CLICKHOUSE_USER", "test-user")
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", "test-password")
    monkeypatch.setenv("TABLE_PREFIX", "test")


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
