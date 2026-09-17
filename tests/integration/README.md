# Integration Tests

_Integration tests for the Thunderstore Query Service._

## Overview

These tests run under TestContainers, and start a throwaway ClickHouse container that is set up using analytics-platform migrations.

This is so that we can have a reproducible, dev/production accurate environment where we can run accurate query service tests.

## Making a test

### Building the test

You are expected to use the appropriate fixtures in your tests.

An integration test will have the name format of `integration_test_<name>.py`.
It will also look something like:

```python
def test_example(client: TestClient):
    response = client.get("/api/v1/some-endpoint")
    assert response.status_code == 200
    assert response.json() == {"data": []}
```

This in itself does nothing and runs queries against an empty database.

To make it do something, you'll want to populate the database using your own fixture (and related insertion fixtures):

```python
from tests.integration._clickhouse import ClickHouseHttp
from tests.integration.conftest import MY_TABLE


# ...
@pytest.fixture
def seed_database(clickhouse_client: ClickHouseHttp):
    clickhouse_client.insert(
        MY_TABLE,
        [
            {"id": 1, "name": "Test"},
        ],
    )
```

If you need to reference a table that isn't in conftest.py, then add it to there.
Ensure that it's included in `_reset_tables` so that data is properly cleaned up between tests.

You can then use this fixture in your test:

```python
def test_example(client: TestClient, seed_database):
    response = client.get("/api/v1/some-endpoint")
    assert response.status_code == 200
    assert response.json() == {"data": [{"id": 1, "name": "Test"}]}
```
