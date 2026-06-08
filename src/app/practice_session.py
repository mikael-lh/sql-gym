from __future__ import annotations

from typing import Any

from starlette.requests import Request

from app.domain.exercises import Exercise
from app.domain.grading import GradingResult, grading_result_from_outcome
from app.execution.models import ExecutionError, QueryResult
from app.grading import grade

SESSION_KEY = "practice_attempts"


def _attempts(request: Request) -> dict[str, dict[str, Any]]:
    attempts = request.session.get(SESSION_KEY)
    if not isinstance(attempts, dict):
        attempts = {}
        request.session[SESSION_KEY] = attempts
    return attempts


def get_stored_sql(request: Request, exercise_id: str) -> str:
    attempt = _attempts(request).get(exercise_id, {})
    sql = attempt.get("sql")
    return sql if isinstance(sql, str) else ""


def _serialize_query_result(result: QueryResult) -> dict[str, Any]:
    return {
        "columns": list(result.columns),
        "rows": [list(row) for row in result.rows],
        "row_count": result.row_count,
        "truncated": result.truncated,
    }


def _serialize_execution_error(error: ExecutionError) -> dict[str, str]:
    return {"message": error.message, "code": error.code}


def _serialize_grading(result: GradingResult) -> dict[str, Any]:
    return {
        "exercise_id": result.exercise_id,
        "status": result.status,
        "summary": result.summary,
        "passed": result.passed,
        "is_placeholder": result.is_placeholder,
    }


def get_attempt_state(request: Request, exercise_id: str) -> dict[str, Any]:
    attempt = _attempts(request).get(exercise_id, {})
    return {
        "sql": get_stored_sql(request, exercise_id),
        "query_result": attempt.get("query_result"),
        "execution_error": attempt.get("execution_error"),
        "grading": attempt.get("grading"),
        "status": attempt.get("status", "not_started"),
    }


def store_run_result(
    request: Request,
    exercise_id: str,
    sql: str,
    outcome: QueryResult | ExecutionError,
) -> None:
    attempts = _attempts(request)
    payload: dict[str, Any] = {
        "sql": sql,
        "status": "draft",
        "grading": None,
    }
    if isinstance(outcome, QueryResult):
        payload["query_result"] = _serialize_query_result(outcome)
        payload["execution_error"] = None
    else:
        payload["query_result"] = None
        payload["execution_error"] = _serialize_execution_error(outcome)
    attempts[exercise_id] = payload
    request.session[SESSION_KEY] = attempts


def store_submit_result(
    request: Request,
    exercise: Exercise,
    sql: str,
    outcome: QueryResult | ExecutionError,
) -> GradingResult | None:
    if isinstance(outcome, ExecutionError):
        store_run_result(request, exercise.id, sql, outcome)
        return None

    expected_grid = exercise.expected_result.expected_grid
    if expected_grid is None:
        store_run_result(request, exercise.id, sql, outcome)
        return None

    grading_outcome = grade(outcome, expected_grid)
    grading = grading_result_from_outcome(exercise.id, grading_outcome)
    attempts = _attempts(request)
    attempts[exercise.id] = {
        "sql": sql,
        "query_result": _serialize_query_result(outcome),
        "execution_error": None,
        "grading": _serialize_grading(grading),
        "status": "graded" if grading_outcome.passed else "submitted",
    }
    request.session[SESSION_KEY] = attempts
    return grading
