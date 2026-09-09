# Setup
FROM ghcr.io/astral-sh/uv:0.12.1 AS uv
FROM python:3.14.3-slim-bookworm AS builder

COPY --from=uv /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY README.md ./
COPY src ./src
RUN uv sync --locked --no-dev

# Prepare for runtime
FROM python:3.14.3-slim-bookworm

ENV PATH="/app/.venv/bin:$PATH"

RUN groupadd --system app && useradd --system --gid app app

WORKDIR /app
COPY --from=builder --chown=app:app /app /app
USER app

CMD ["fastapi", "run", "src/thunderstore_query_service/main.py", "--host", "0.0.0.0", "--port", "8000"]
