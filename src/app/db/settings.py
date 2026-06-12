import os

DEFAULT_STATEMENT_TIMEOUT_MS = 30_000


def get_database_url() -> str | None:
    return os.environ.get("DATABASE_URL")


def get_statement_timeout_ms() -> int:
    raw = os.environ.get("SQL_STATEMENT_TIMEOUT_MS")
    if raw is None:
        return DEFAULT_STATEMENT_TIMEOUT_MS
    try:
        parsed = int(raw)
    except ValueError:
        return DEFAULT_STATEMENT_TIMEOUT_MS
    return max(1_000, parsed)
