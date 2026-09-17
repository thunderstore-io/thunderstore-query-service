from unittest.mock import patch

import httpx2
from httpx2 import AsyncClient, MockTransport


def mock_http(json: dict, router, status_code=200):
    transport = MockTransport(lambda request: httpx2.Response(status_code, json=json))
    return patch.object(router, "AsyncClient", lambda: AsyncClient(transport=transport))
