# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Setup (first time):**
```shell
cp .env.example .env
uv sync --all-groups
pre-commit install
just up        # starts Postgres via docker-compose
just migrate   # run migrations
```

**Development:**
```shell
just run                              # uvicorn with --reload
just run --log-config logging.ini     # with structured logging
```

**Linting:**
```shell
just lint     # ruff format + ruff check --fix on src/
```

**Migrations:**
```shell
just mm <migration_name>   # autogenerate migration from src/database.py changes
just migrate               # upgrade to head
just downgrade -1          # step back (or -2, base, or migration hash)
```

Migration files are named `YYYY-MM-DD_slug` and are auto-formatted with ruff.

**Docker:**
```shell
just up / just kill / just build / just ps
docker compose -f docker-compose.prod.yml up -d --build   # production
```

## Architecture

All application code lives in `src/`. There is no subdirectory structure yet — routers, services, and models for new features should be added here as the project grows.

**Key files:**
- [src/main.py](src/main.py) — FastAPI app factory: lifespan, Sentry init (deployed envs only), CORS middleware, `/healthcheck` endpoint.
- [src/config.py](src/config.py) — `Config(pydantic_settings.BaseSettings)` loaded from `.env`. Two DB URLs are required: `DATABASE_URL` (sync, used by Alembic) and `DATABASE_ASYNC_URL` (async, used at runtime). `SENTRY_DSN` is mandatory when `ENVIRONMENT` is `STAGING` or `PRODUCTION`. OpenAPI docs (`/docs`) are hidden in non-debug environments.
- [src/database.py](src/database.py) — Async SQLAlchemy engine (asyncpg) with pessimistic connection pooling. Use `fetch_one`, `fetch_all`, `execute` helpers instead of raw session/connection management. Pass an `AsyncConnection` explicitly for multi-statement transactions; omit it for single-statement auto-connect. `get_db_connection` is a FastAPI dependency.
- [src/constants.py](src/constants.py) — `DB_NAMING_CONVENTION` (applied to `metadata`) and the `Environment` enum with `is_debug`, `is_testing`, `is_deployed` properties.
- [src/schemas.py](src/schemas.py) — `CustomModel(pydantic.BaseModel)` enforces UTC-aware datetime serialization. All request/response models should inherit from it.
- [src/exceptions.py](src/exceptions.py) — `DetailedHTTPException` base class with typed subclasses (`NotFound`, `PermissionDenied`, `BadRequest`, `NotAuthenticated`). Raise these instead of raw `HTTPException`.

**Database pattern:** Tables are defined directly on the `metadata` object in `src/database.py` (SQLAlchemy Core style, not ORM declarative). Alembic's `env.py` imports that `metadata` for autogenerate.

**Environments:** `LOCAL` and `TESTING` are debug (docs visible, no Sentry required). `STAGING` and `PRODUCTION` are deployed (docs hidden, Sentry required, `root_path` set to `/v{APP_VERSION}`).
