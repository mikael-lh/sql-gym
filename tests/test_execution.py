import os
from unittest.mock import MagicMock, patch

import pytest
from psycopg import errors as pg_errors

from app.execution import ExecutionError, QueryResult, execute_query, validate_select_only


def _column(name: str) -> MagicMock:
    column = MagicMock()
    column.name = name
    return column


def test_validate_select_only_rejects_empty_sql() -> None:
    error = validate_select_only("   ")
    assert error is not None
    assert error.code == "empty_sql"


def test_validate_select_only_rejects_dml() -> None:
    error = validate_select_only("DELETE FROM times_archive")
    assert error is not None
    assert error.code == "not_select"


def test_validate_select_only_allows_select() -> None:
    assert validate_select_only("SELECT headline_main FROM times_archive") is None


def test_validate_select_only_allows_cte_select() -> None:
    sql = "WITH c AS (SELECT 1 AS n) SELECT n FROM c"
    assert validate_select_only(sql) is None


def test_validate_select_only_allows_keyword_inside_string() -> None:
    sql = "SELECT headline_main FROM times_archive WHERE headline_main = 'plans to create jobs'"
    assert validate_select_only(sql) is None


def test_validate_select_only_allows_semicolon_inside_string() -> None:
    sql = "SELECT headline_main FROM times_archive WHERE headline_main = 'a;b'"
    assert validate_select_only(sql) is None


def test_validate_select_only_allows_multiple_select_statements() -> None:
    # Text check is UX-only; a second SELECT is harmless under a read-only transaction.
    assert validate_select_only("SELECT 1; SELECT 2;") is None


@patch("app.execution.execute.get_database_url", return_value=None)
def test_execute_query_without_database_url(_mock_url: MagicMock) -> None:
    result = execute_query("SELECT 1")
    assert isinstance(result, ExecutionError)
    assert result.code == "database_unavailable"


@patch("app.execution.execute.psycopg.connect")
@patch("app.execution.execute.get_database_url", return_value="postgresql://example")
def test_execute_query_returns_query_result(_mock_url: MagicMock, mock_connect: MagicMock) -> None:
    cursor = MagicMock()
    cursor.description = [_column("n")]
    cursor.fetchmany.return_value = [(1,), (2,)]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    mock_connect.return_value.__enter__.return_value = connection

    result = execute_query("SELECT 1 AS n")
    assert isinstance(result, QueryResult)
    assert result.columns == ("n",)
    assert result.rows == ((1,), (2,))
    assert result.row_count == 2
    assert result.truncated is False
    assert connection.read_only is True


@patch("app.execution.execute.psycopg.connect")
@patch("app.execution.execute.get_database_url", return_value="postgresql://example")
def test_execute_query_marks_truncated_results(
    _mock_url: MagicMock,
    mock_connect: MagicMock,
) -> None:
    cursor = MagicMock()
    cursor.description = [_column("n")]
    cursor.fetchmany.return_value = [(index,) for index in range(501)]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    mock_connect.return_value.__enter__.return_value = connection

    result = execute_query("SELECT generate_series(1, 1000) AS n")
    assert isinstance(result, QueryResult)
    assert result.row_count == 500
    assert result.truncated is True


@patch("app.execution.execute.psycopg.connect")
@patch("app.execution.execute.get_database_url", return_value="postgresql://example")
def test_execute_query_timeout(_mock_url: MagicMock, mock_connect: MagicMock) -> None:
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.cursor_execute = None
    connection.cursor.return_value.__enter__.return_value.execute.side_effect = (
        pg_errors.QueryCanceled("timeout")
    )
    mock_connect.return_value.__enter__.return_value = connection

    result = execute_query("SELECT pg_sleep(10)")
    assert isinstance(result, ExecutionError)
    assert result.code == "timeout"


@patch("app.execution.execute.psycopg.connect")
@patch("app.execution.execute.get_database_url", return_value="postgresql://example")
def test_execute_query_returns_postgres_message(
    _mock_url: MagicMock,
    mock_connect: MagicMock,
) -> None:
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.execute.side_effect = (
        pg_errors.UndefinedColumn('column "missing_col" does not exist')
    )
    mock_connect.return_value.__enter__.return_value = connection

    result = execute_query("SELECT missing_col FROM times_archive")
    assert isinstance(result, ExecutionError)
    assert result.code == "execution_error"
    assert result.postgres_message is not None
    assert "missing_col" in result.postgres_message


@patch("app.execution.execute.validate_select_only", return_value=None)
@patch("app.execution.execute.psycopg.connect")
@patch("app.execution.execute.get_database_url", return_value="postgresql://example")
def test_execute_query_rejects_write_via_read_only_transaction(
    _mock_url: MagicMock,
    mock_connect: MagicMock,
    _mock_validate: MagicMock,
) -> None:
    """Safety must hold even when the UX text check is bypassed."""
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value.execute.side_effect = (
        pg_errors.ReadOnlySqlTransaction("cannot execute DELETE in a read-only transaction")
    )
    mock_connect.return_value.__enter__.return_value = connection

    result = execute_query("DELETE FROM times_archive")
    assert isinstance(result, ExecutionError)
    assert result.code == "read_only_violation"
    assert connection.read_only is True


@patch("app.execution.execute.get_pool")
@patch("app.execution.execute.get_database_url", return_value="postgresql://example")
def test_execute_query_uses_pool_when_available(
    _mock_url: MagicMock,
    mock_get_pool: MagicMock,
) -> None:
    cursor = MagicMock()
    cursor.description = [_column("n")]
    cursor.fetchmany.return_value = [(1,)]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    pool = MagicMock()
    pool.connection.return_value.__enter__.return_value = connection
    mock_get_pool.return_value = pool

    result = execute_query("SELECT 1 AS n")
    assert isinstance(result, QueryResult)
    pool.connection.assert_called()
    assert connection.read_only is True


@patch("app.execution.execute.get_pool")
@patch("app.execution.execute.get_database_url", return_value="postgresql://example")
def test_execute_query_reuses_pool_across_calls(
    _mock_url: MagicMock,
    mock_get_pool: MagicMock,
) -> None:
    cursor = MagicMock()
    cursor.description = [_column("n")]
    cursor.fetchmany.return_value = [(1,)]
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    pool = MagicMock()
    pool.connection.return_value.__enter__.return_value = connection
    mock_get_pool.return_value = pool

    first = execute_query("SELECT 1 AS n")
    second = execute_query("SELECT 1 AS n")
    assert isinstance(first, QueryResult)
    assert isinstance(second, QueryResult)
    assert pool.connection.call_count == 2


@patch("app.execution.execute.get_pool")
@patch("app.execution.execute.get_database_url", return_value="postgresql://example")
def test_execute_query_concurrent_borrows_stay_within_pool(
    _mock_url: MagicMock,
    mock_get_pool: MagicMock,
) -> None:
    """Concurrent Run/Submit calls borrow from the shared pool without failing."""
    import threading
    from collections.abc import Iterator
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from contextlib import contextmanager

    active = 0
    peak = 0
    lock = threading.Lock()
    max_size = 4

    @contextmanager
    def _connection() -> Iterator[MagicMock]:

        nonlocal active, peak
        with lock:
            active += 1
            peak = max(peak, active)
            assert active <= max_size
        try:
            cursor = MagicMock()
            cursor.description = [_column("n")]
            cursor.fetchmany.return_value = [(1,)]
            connection = MagicMock()
            connection.cursor.return_value.__enter__.return_value = cursor
            yield connection
        finally:
            with lock:
                active -= 1

    pool = MagicMock()
    pool.connection = _connection
    mock_get_pool.return_value = pool

    with ThreadPoolExecutor(max_workers=max_size) as executor:
        futures = [executor.submit(execute_query, "SELECT 1 AS n") for _ in range(16)]
        results = [future.result() for future in as_completed(futures)]

    assert all(isinstance(result, QueryResult) for result in results)
    assert peak <= max_size
    assert peak >= 1


@pytest.mark.integration
def test_execute_query_integration_select() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set")

    with patch("app.execution.execute.get_database_url", return_value=database_url):
        result = execute_query("SELECT COUNT(*) AS article_count FROM times_archive")

    assert isinstance(result, QueryResult)
    assert result.columns == ("article_count",)
    assert result.row_count == 1


@pytest.mark.integration
def test_execute_query_integration_keyword_in_string() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set")

    sql = (
        "SELECT headline_main FROM times_archive "
        "WHERE headline_main = 'plans to create jobs' LIMIT 1"
    )
    with patch("app.execution.execute.get_database_url", return_value=database_url):
        result = execute_query(sql)

    assert isinstance(result, QueryResult)


@pytest.mark.integration
@patch("app.execution.execute.validate_select_only", return_value=None)
def test_execute_query_integration_write_rejected(_mock_validate: MagicMock) -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set")

    with patch("app.execution.execute.get_database_url", return_value=database_url):
        result = execute_query("DELETE FROM times_archive WHERE false")

    assert isinstance(result, ExecutionError)
    assert result.code == "read_only_violation"


@pytest.mark.integration
def test_execute_query_integration_concurrent_pool_borrows() -> None:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from app.execution.pool import close_pool, open_pool

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set")

    close_pool()
    with patch("app.execution.pool.get_database_url", return_value=database_url):
        pool = open_pool()
    assert pool is not None
    try:
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [
                executor.submit(execute_query, "SELECT 1 AS n") for _ in range(24)
            ]
            results = [future.result() for future in as_completed(futures)]
        assert all(isinstance(result, QueryResult) for result in results)
    finally:
        close_pool()
