from unittest.mock import patch

import httpx2
from httpx2 import AsyncClient, MockTransport

from thunderstore_query_service import _clickhouse


def _patch_transport(handler):
    transport = MockTransport(handler)
    return patch.object(
        _clickhouse, "AsyncClient", lambda: AsyncClient(transport=transport)
    )


def mock_clickhouse(json: dict, status_code=200):
    return _patch_transport(lambda request: httpx2.Response(status_code, json=json))


def mock_clickhouse_error(error: Exception):
    def raise_error(request):
        raise error

    return _patch_transport(raise_error)
