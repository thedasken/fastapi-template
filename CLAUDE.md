# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Commands

**Setup:**

```shell
cp .env.example .env
uv sync --all-groups
pre-commit install
just up
just migrate
```

**Development:**

```shell
just run
just run --log-config logging.ini
```

**Linting:**

```shell
just lint
```

This runs `ruff format src` and `ruff check --fix src`.

**Migrations:**

```shell
just mm <migration_name>
just migrate
just downgrade -1
```

Migration files use the `YYYY-MM-DD_slug` naming format.

**Docker:**

```shell
just up
just kill
just build
just ps
just down
docker compose -f docker-compose.prod.yml up -d --build
```

## Architecture

Application code lives in `src/`. Features should use a feature-slice layout like
`src/items`:

- `router.py` exposes FastAPI routes.
- `service.py` contains business logic and SQL execution.
- `dependencies.py` contains route dependencies such as entity validation.
- `schemas.py` contains request and response Pydantic models.
- `models.py` contains SQLAlchemy Core table definitions.
- `exceptions.py` contains feature-specific HTTP exceptions.
- `constants.py` contains feature-specific constants and error codes.

## Key Files

- `src/main.py` — FastAPI app setup, lifespan, Sentry initialization for deployed environments, CORS middleware, exception handlers, `/health`, and router registration.
- `src/config.py` — `pydantic-settings` config loaded from `.env`. `DATABASE_URL` is used by Alembic, `DATABASE_ASYNC_URL` is used at runtime. Deployed environments require `SENTRY_DSN`; non-debug environments hide OpenAPI docs.
- `src/database.py` — async SQLAlchemy engine, shared `metadata`, and `get_db_connection()` FastAPI dependency.
- `src/models.py` — imports every feature's `models` module so all `Table` objects are registered on `metadata` before Alembic autogenerate runs.
- `src/constants.py` — database naming convention and `Environment` enum.
- `src/schemas.py` — `CustomModel`, including timezone-aware datetime JSON serialization.
- `src/exceptions.py` — `DetailedHTTPException` base class and shared typed HTTP exceptions.
- `docs/middleware.md` — guidance for implementing custom middleware as pure ASGI middleware.

## Database Pattern

Use SQLAlchemy Core, not ORM declarative models. Define tables as `Table`
objects attached to the shared `metadata` from `src/database.py`.

Routes receive an `AsyncConnection` from `get_db_connection()`. The dependency
uses `engine.begin()`, so each request gets a transaction that commits when the
request succeeds and rolls back when an exception is raised.

Services should execute queries and DML with the provided connection. Do not call
`commit()` or `rollback()` inside services; transaction lifecycle belongs to the
FastAPI dependency or to an explicit outer context.

Alembic imports `metadata` from `src/database.py` for autogeneration. When you
add a new feature with a `models.py`, add an import for it in `src/models.py`
so its tables are registered on `metadata` before autogenerate runs.

## Logging

Declare a module-local logger only in modules that actually log:

```python
import logging

logger = logging.getLogger(__name__)
```

Avoid shared loggers in utility modules. A module-local logger preserves the real
source module name in logs.

## Middleware

Prefer pure ASGI middleware for custom middleware. Avoid subclassing
`BaseHTTPMiddleware`, especially for middleware that inspects request or response
bodies, because it can interfere with streaming responses and async behavior.
See `docs/middleware.md`.

## Environments

`LOCAL` and `TESTING` are debug environments: docs are visible and Sentry is not
required. `STAGING` and `PRODUCTION` are deployed environments: docs are hidden,
Sentry is required, and FastAPI uses `/v{API_VERSION}` as `root_path`.
