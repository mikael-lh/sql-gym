import os

DEFAULT_STATEMENT_TIMEOUT_MS = 30_000
DEV_SESSION_SECRET = "dev-only-session-secret-change-me"


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


def get_app_env() -> str:
    raw = os.environ.get("APP_ENV", "development").strip().lower()
    return raw or "development"


def get_session_secret() -> str:
    """Return the cookie/session signing secret.

    Development may use the committed fallback. Production refuses to start
    without an explicit SESSION_SECRET.
    """
    secret = os.environ.get("SESSION_SECRET")
    if secret:
        return secret
    if get_app_env() == "production":
        raise RuntimeError(
            "SESSION_SECRET must be set when APP_ENV=production. "
            "Refusing to start with the public development default."
        )
    return DEV_SESSION_SECRET
