from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient

from tests.integration._clickhouse import ClickHouseHttp, to_datetime64
from tests.integration.conftest import DOWNLOAD_TABLE, VERSION_TABLE

NAMESPACE = "an-author"
PACKAGE = "package_name"
OTHER_PACKAGE = "other_package_name"

EXPECTED_POINTS = 7 * 24 + 1


def _version_row(
    version_id: int, package_id: int, namespace: str, package: str
) -> dict[str, Any]:
    return {
        "id": version_id,
        "is_active": 1,
        "owner__id": 1,
        "owner__name": namespace,
        "namespace__name": namespace,
        "name": package,
        "full_version_name": f"{namespace}-{package}-1.0.{version_id}",
        "version_number": f"1.0.{version_id}",
        "package__id": package_id,
        "date_created": to_datetime64(datetime.now(UTC)),
        "file_size": 1024,
    }


def _to_iso(value: datetime) -> str:
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _downloads_by_hour(payload: list[dict[str, Any]]) -> dict[str, int]:
    return {point["hour"]: point["downloads"] for point in payload}


@pytest.fixture
def seeded_hours(clickhouse_client: ClickHouseHttp) -> tuple[datetime, datetime]:
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    older_hour = now - timedelta(hours=2)
    recent_hour = now - timedelta(hours=1)
    outside_window = now - timedelta(days=10)

    clickhouse_client.insert(
        VERSION_TABLE,
        [
            _version_row(1001, 1, NAMESPACE, PACKAGE),
            _version_row(1002, 2, NAMESPACE, OTHER_PACKAGE),
            _version_row(1003, 1, NAMESPACE, PACKAGE),
        ],
    )
    clickhouse_client.insert(
        DOWNLOAD_TABLE,
        [
            {
                "id": 1,
                "version_id": 1001,
                "timestamp": to_datetime64(older_hour),
            },
            {
                "id": 2,
                "version_id": 1001,
                "timestamp": to_datetime64(older_hour + timedelta(minutes=17)),
            },
            {
                "id": 3,
                "version_id": 1003,
                "timestamp": to_datetime64(recent_hour + timedelta(minutes=5)),
            },
            {
                "id": 4,
                "version_id": 1002,
                "timestamp": to_datetime64(recent_hour),
            },
            {
                "id": 5,
                "version_id": 1001,
                "timestamp": to_datetime64(outside_window),
            },
        ],
    )
    return older_hour, recent_hour


def test_download_history_aggregates_by_hour(
    client: TestClient,
    seeded_hours: tuple[datetime, datetime],
):
    older_hour, recent_hour = seeded_hours

    response = client.get(f"/api/charts/downloads/{NAMESPACE}/{PACKAGE}")

    assert response.status_code == 200
    by_hour = _downloads_by_hour(response.json())

    assert by_hour[_to_iso(older_hour)] == 2
    assert by_hour[_to_iso(recent_hour)] == 1


def test_download_history_covers_every_hour_in_the_window(
    client: TestClient,
    seeded_hours: tuple[datetime, datetime],
):
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)

    response = client.get(f"/api/charts/downloads/{NAMESPACE}/{PACKAGE}")

    assert response.status_code == 200
    payload = response.json()

    assert len(payload) == EXPECTED_POINTS
    assert payload[0]["hour"] == _to_iso(now - timedelta(days=7))
    assert payload[-1]["hour"] == _to_iso(now)

    hours = [point["hour"] for point in payload]
    assert hours == sorted(hours)

    quiet_hour = _to_iso(now - timedelta(hours=3))
    assert _downloads_by_hour(payload)[quiet_hour] == 0


def test_download_history_is_all_zeroes_for_unknown_package(
    client: TestClient,
    seeded_hours: tuple[datetime, datetime],
):
    response = client.get(f"/api/charts/downloads/{NAMESPACE}/does-not-exist")

    assert response.status_code == 200
    payload = response.json()

    assert len(payload) == EXPECTED_POINTS
    assert all(point["downloads"] == 0 for point in payload)
