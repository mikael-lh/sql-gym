import os

DEFAULT_STATEMENT_TIMEOUT_MS = 30_000
DEV_SESSION_SECRET = "dev-only-session-secret-change-me"
DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_OLLAMA_PULL_TIMEOUT_SECONDS = 120.0
DEFAULT_OLLAMA_REQUEST_TIMEOUT_SECONDS = 30.0


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
    secret = (os.environ.get("SESSION_SECRET") or "").strip()
    if secret:
        return secret
    if get_app_env() == "production":
        raise RuntimeError(
            "SESSION_SECRET must be set when APP_ENV=production. "
            "Refusing to start with the public development default."
        )
    return DEV_SESSION_SECRET


def get_ollama_base_url() -> str:
    raw = (os.environ.get("OLLAMA_BASE_URL") or "").strip()
    return raw.rstrip("/") if raw else DEFAULT_OLLAMA_BASE_URL


def get_ollama_model() -> str:
    raw = (os.environ.get("OLLAMA_MODEL") or "").strip()
    return raw or DEFAULT_OLLAMA_MODEL


def get_ollama_keep_model() -> bool:
    raw = (os.environ.get("OLLAMA_KEEP_MODEL") or "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def get_ollama_pull_timeout_seconds() -> float:
    raw = os.environ.get("OLLAMA_PULL_TIMEOUT_SECONDS")
    if raw is None:
        return DEFAULT_OLLAMA_PULL_TIMEOUT_SECONDS
    try:
        parsed = float(raw)
    except ValueError:
        return DEFAULT_OLLAMA_PULL_TIMEOUT_SECONDS
    return max(1.0, parsed)


def get_ollama_request_timeout_seconds() -> float:
    raw = os.environ.get("OLLAMA_REQUEST_TIMEOUT_SECONDS")
    if raw is None:
        return DEFAULT_OLLAMA_REQUEST_TIMEOUT_SECONDS
    try:
        parsed = float(raw)
    except ValueError:
        return DEFAULT_OLLAMA_REQUEST_TIMEOUT_SECONDS
    return max(1.0, parsed)
