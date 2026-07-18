"""Shared PostgreSQL connection pool for learner query execution."""

from __future__ import annotations

from psycopg_pool import ConnectionPool

from app.db.settings import get_database_url

_pool: ConnectionPool | None = None


def get_pool() -> ConnectionPool | None:
    return _pool


def open_pool() -> ConnectionPool | None:
    """Create the shared pool when DATABASE_URL is set. Idempotent."""
    global _pool
    if _pool is not None:
        return _pool
    database_url = get_database_url()
    if not database_url:
        return None
    _pool = ConnectionPool(
        conninfo=database_url,
        min_size=1,
        max_size=10,
        open=True,
    )
    return _pool


def close_pool() -> None:
    global _pool
    if _pool is None:
        return
    _pool.close()
    _pool = None
