from __future__ import annotations

import re
from decimal import Decimal

import psycopg
from psycopg import errors as pg_errors

from app.db.settings import get_database_url, get_statement_timeout_ms
from app.execution.models import ExecutionError, QueryResult
from app.execution.sql_sanitize import strip_sql_comments

MAX_ROWS = 500

_SELECT_PREFIX = re.compile(r"^\s*(with\s+.+?\)\s*)?select\b", re.IGNORECASE | re.DOTALL)
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy)\b",
    re.IGNORECASE,
)


def _normalize_cell(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def validate_select_only(sql: str) -> ExecutionError | None:
    stripped = strip_sql_comments(sql)
    if not stripped:
        return ExecutionError(message="Enter a SQL query to run.", code="empty_sql")
    if ";" in stripped.rstrip(";"):
        return ExecutionError(
            message="Only a single SELECT statement is allowed.",
            code="multiple_statements",
        )
    if _FORBIDDEN_KEYWORDS.search(stripped):
        return ExecutionError(
            message="Only SELECT queries are allowed in the practice database.",
            code="forbidden_statement",
        )
    if not _SELECT_PREFIX.match(stripped):
        return ExecutionError(
            message="Only SELECT queries are allowed in the practice database.",
            code="not_select",
        )
    return None


def execute_query(sql: str) -> QueryResult | ExecutionError:
    guard_error = validate_select_only(sql)
    if guard_error is not None:
        return guard_error

    database_url = get_database_url()
    if not database_url:
        return ExecutionError(
            message=(
                "Database is not configured. Start Docker Postgres — "
                "see docs/times-data-setup.md."
            ),
            code="database_unavailable",
        )

    executable_sql = strip_sql_comments(sql).rstrip(";")
    try:
        with psycopg.connect(database_url) as conn:
            conn.execute(f"SET statement_timeout = {get_statement_timeout_ms()}")
            with conn.cursor() as cur:
                cur.execute(executable_sql)
                if cur.description is None:
                    return ExecutionError(
                        message="The query did not return a result set.",
                        code="no_result_set",
                    )
                columns = tuple(desc.name for desc in cur.description)
                fetched = cur.fetchmany(MAX_ROWS + 1)
                truncated = len(fetched) > MAX_ROWS
                rows = tuple(
                    tuple(_normalize_cell(value) for value in row)
                    for row in fetched[:MAX_ROWS]
                )
    except pg_errors.QueryCanceled:
        return ExecutionError(
            message="The query took too long and was stopped. Try simplifying your SQL.",
            code="timeout",
        )
    except pg_errors.SyntaxError:
        return ExecutionError(
            message="PostgreSQL could not parse the SQL. Check syntax and try again.",
            code="syntax_error",
        )
    except psycopg.Error:
        return ExecutionError(
            message="The query could not be executed. Check your SQL and try again.",
            code="execution_error",
        )

    return QueryResult(
        columns=columns,
        rows=rows,
        row_count=len(rows),
        truncated=truncated,
    )
