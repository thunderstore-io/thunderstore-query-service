from collections.abc import Iterator
from pathlib import Path

import pytest
from testcontainers.community.clickhouse import ClickHouseContainer
from testcontainers.core.container import DockerContainer
from testcontainers.core.network import Network

from tests.integration._clickhouse import ClickHouseHttp

REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATIONS_DIR = REPO_ROOT / "analytics-platform" / "aiven-clickhouse-migrations"

CLICKHOUSE_IMAGE = "clickhouse/clickhouse-server:25.3-alpine"
DBMATE_IMAGE = "ghcr.io/amacneil/dbmate:2.28.0"

CLICKHOUSE_DB = "analytics"
CLICKHOUSE_USER = "test_user"
CLICKHOUSE_PASSWORD = "test_password"
CLICKHOUSE_ALIAS = "clickhouse"

TABLE_PREFIX = "dev"

VERSION_TABLE = (
    f"{CLICKHOUSE_DB}.thunderstore_{TABLE_PREFIX}_model_package_version_update_v1"
)
DOWNLOAD_TABLE = (
    f"{CLICKHOUSE_DB}.thunderstore_{TABLE_PREFIX}_analytics_package_download_v1"
)


@pytest.fixture(scope="session")
def docker_available() -> None:
    from testcontainers.core.docker_client import DockerClient

    try:
        DockerClient().client.ping()
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Docker daemon is not reachable: {exc!r}")


@pytest.fixture(scope="session")
def migrations_dir() -> Path:
    if not any(MIGRATIONS_DIR.glob("*.sql")):
        pytest.fail(
            f"No ClickHouse migrations found at {MIGRATIONS_DIR}. "
            "Run `git submodule update --init --recursive`."
        )
    return MIGRATIONS_DIR


@pytest.fixture(scope="session")
def docker_network(docker_available: None) -> Iterator[Network]:
    with Network() as network:
        yield network


@pytest.fixture(scope="session")
def clickhouse_container(docker_network: Network) -> Iterator[ClickHouseContainer]:
    container = (
        ClickHouseContainer(
            image=CLICKHOUSE_IMAGE,
            username=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            dbname=CLICKHOUSE_DB,
        )
        .with_network(docker_network)
        .with_network_aliases(CLICKHOUSE_ALIAS)
    )
    with container:
        yield container


@pytest.fixture(scope="session")
def clickhouse(
    clickhouse_container: ClickHouseContainer,
    docker_network: Network,
    migrations_dir: Path,
) -> ClickHouseContainer:
    database_url = (
        f"clickhouse://{CLICKHOUSE_USER}:{CLICKHOUSE_PASSWORD}"
        f"@{CLICKHOUSE_ALIAS}:9000/{CLICKHOUSE_DB}"
    )

    dbmate = (
        DockerContainer(DBMATE_IMAGE)
        .with_network(docker_network)
        .with_env("DATABASE_URL", database_url)
        .with_env("DBMATE_MIGRATIONS_DIR", f"/db/{migrations_dir.name}")
        .with_command(["--wait", "--no-dump-schema", "up"])
        .with_copy_into_container(migrations_dir, "/db")
    )

    dbmate.start()
    try:
        exit_code = dbmate.wait()
        stdout, stderr = dbmate.get_logs()
    finally:
        dbmate.stop()

    if exit_code != 0:
        raise RuntimeError(
            f"dbmate exited with {exit_code}\n"
            f"--- stdout ---\n{stdout.decode(errors='replace')}\n"
            f"--- stderr ---\n{stderr.decode(errors='replace')}"
        )

    return clickhouse_container


@pytest.fixture(scope="session")
def clickhouse_http_url(clickhouse: ClickHouseContainer) -> str:
    host = clickhouse.get_container_host_ip()
    port = clickhouse.get_exposed_port(8123)
    return f"http://{host}:{port}/"


@pytest.fixture(scope="session")
def clickhouse_client(clickhouse_http_url: str) -> Iterator[ClickHouseHttp]:
    with ClickHouseHttp(
        clickhouse_http_url, CLICKHOUSE_USER, CLICKHOUSE_PASSWORD
    ) as ch_client:
        yield ch_client


@pytest.fixture(autouse=True)
def _reset_tables(clickhouse_client: ClickHouseHttp) -> None:
    for table in (VERSION_TABLE, DOWNLOAD_TABLE):
        clickhouse_client.execute(f"TRUNCATE TABLE IF EXISTS {table}")


@pytest.fixture(autouse=True)
def _clickhouse_env(clickhouse_http_url: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Autouse so no integration test can fall through to the ambient CLICKHOUSE_URI, which
    mise.local.toml points at the real Aiven cluster.
    """
    monkeypatch.setenv("CLICKHOUSE_URI", clickhouse_http_url)
    monkeypatch.setenv("CLICKHOUSE_USER", CLICKHOUSE_USER)
    monkeypatch.setenv("CLICKHOUSE_PASSWORD", CLICKHOUSE_PASSWORD)
    monkeypatch.setenv("TABLE_PREFIX", TABLE_PREFIX)
