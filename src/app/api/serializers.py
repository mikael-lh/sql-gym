"""Shared JSON serializers for query results, errors, and grading."""

from __future__ import annotations

from typing import Any

from app.domain.grading import GradingResult
from app.execution.models import ExecutionError, QueryResult


def serialize_query_result(
    result: QueryResult,
    *,
    row_limit: int | None = None,
) -> dict[str, Any]:
    rows = result.rows
    preview_capped = False
    if row_limit is not None:
        preview_capped = len(rows) > row_limit
        rows = rows[:row_limit]
    return {
        "columns": list(result.columns),
        "rows": [list(row) for row in rows],
        "row_count": result.row_count,
        "truncated": result.truncated or preview_capped,
    }


def serialize_execution_error(
    error: ExecutionError,
    *,
    for_run: bool = False,
) -> dict[str, str]:
    if for_run and error.postgres_message:
        return {"message": error.postgres_message, "code": error.code}
    return {"message": error.message, "code": error.code}


def serialize_grading(result: GradingResult) -> dict[str, Any]:
    return {
        "exercise_id": result.exercise_id,
        "status": result.status,
        "summary": result.summary,
        "passed": result.passed,
        "is_placeholder": result.is_placeholder,
    }
