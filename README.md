# Thunderstore Query Service

An API service to query information to gain insight into mods and packages.

## Setup

```bash
mise trust
mise install
git submodule update --init --recursive
uv sync
```

Copy `mise.local.toml.template` to `mise.local.toml` and fill in the ClickHouse settings
to run the service locally with `mise run dev`.

## Testing

To run all tests:
- `mise run test`

To run only unit tests:
- `mise run test-unit`

To run only integration tests:
- `mise run test-integration`
