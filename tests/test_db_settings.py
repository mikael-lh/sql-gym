from unittest.mock import patch

import pytest

from app.db.settings import (
    DEFAULT_STATEMENT_TIMEOUT_MS,
    DEV_SESSION_SECRET,
    get_app_env,
    get_session_secret,
    get_statement_timeout_ms,
)


def test_get_statement_timeout_ms_default() -> None:
    with patch.dict("os.environ", {}, clear=True):
        assert get_statement_timeout_ms() == DEFAULT_STATEMENT_TIMEOUT_MS


def test_get_statement_timeout_ms_from_env() -> None:
    with patch.dict("os.environ", {"SQL_STATEMENT_TIMEOUT_MS": "45000"}, clear=True):
        assert get_statement_timeout_ms() == 45_000


def test_get_statement_timeout_ms_rejects_invalid_env() -> None:
    with patch.dict("os.environ", {"SQL_STATEMENT_TIMEOUT_MS": "fast"}, clear=True):
        assert get_statement_timeout_ms() == DEFAULT_STATEMENT_TIMEOUT_MS


def test_get_statement_timeout_ms_enforces_minimum() -> None:
    with patch.dict("os.environ", {"SQL_STATEMENT_TIMEOUT_MS": "250"}, clear=True):
        assert get_statement_timeout_ms() == 1_000


def test_get_app_env_defaults_to_development() -> None:
    with patch.dict("os.environ", {}, clear=True):
        assert get_app_env() == "development"


def test_get_session_secret_uses_dev_fallback() -> None:
    with patch.dict("os.environ", {}, clear=True):
        assert get_session_secret() == DEV_SESSION_SECRET


def test_get_session_secret_uses_env_value() -> None:
    with patch.dict(
        "os.environ",
        {"SESSION_SECRET": "prod-secret", "APP_ENV": "production"},
        clear=True,
    ):
        assert get_session_secret() == "prod-secret"


def test_get_session_secret_hard_fails_in_production_without_secret() -> None:
    with patch.dict("os.environ", {"APP_ENV": "production"}, clear=True):
        with pytest.raises(RuntimeError, match="SESSION_SECRET must be set"):
            get_session_secret()


def test_get_session_secret_hard_fails_on_whitespace_only_in_production() -> None:
    with patch.dict(
        "os.environ",
        {"APP_ENV": "production", "SESSION_SECRET": "   "},
        clear=True,
    ):
        with pytest.raises(RuntimeError, match="SESSION_SECRET must be set"):
            get_session_secret()


def test_create_app_hard_fails_in_production_without_secret() -> None:
    # Import first so module-level `app = create_app()` runs under development defaults.
    from app.main import create_app

    with patch.dict("os.environ", {"APP_ENV": "production"}, clear=True):
        with pytest.raises(RuntimeError, match="SESSION_SECRET must be set"):
            create_app()
