from unittest.mock import patch

from app.db.settings import DEFAULT_STATEMENT_TIMEOUT_MS, get_statement_timeout_ms


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
