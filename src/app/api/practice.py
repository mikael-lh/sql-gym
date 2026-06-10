from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.exercises import Exercise
from app.domain.progress import ProgressStore
from app.execution import execute_query
from app.execution.models import ExecutionError, QueryResult
from app.practice import PracticeFilters, lookup_exercise
from app.practice_session import store_run_result, store_submit_result
from app.progress import attach_progress_cookie, clear_progress_cookie, load_progress
from app.workspace.context import get_workspace_context, parse_workspace_filters
from app.workspace.navigation import filtered_exercises

_PROGRESS_LABELS = {
    "not_started": "Not started",
    "attempted": "Attempted",
    "passed": "Passed",
}


class RunRequest(BaseModel):
    sql: str


class SubmitRequest(BaseModel):
    sql: str
    elapsed_seconds: int | None = None


def _serialize_query_result(result: QueryResult) -> dict[str, Any]:
    return {
        "columns": list(result.columns),
        "rows": [list(row) for row in result.rows],
        "row_count": result.row_count,
        "truncated": result.truncated,
    }


def _serialize_execution_error(error: ExecutionError) -> dict[str, str]:
    return {"message": error.message, "code": error.code}


def _exercise_list_item(exercise: Exercise, request: Request) -> dict[str, Any]:
    store = load_progress(request)
    status = store.get_status(exercise.id)
    return {
        "id": exercise.id,
        "dataset_id": exercise.dataset_id,
        "title": exercise.title,
        "difficulty": exercise.difficulty,
        "mode": exercise.mode,
        "progress_status": status,
        "progress_label": _PROGRESS_LABELS[status],
        "url": f"/practice/{exercise.dataset_id}/{exercise.id}",
    }


def _parse_elapsed_seconds(exercise: Exercise, elapsed_seconds: int | None) -> int | None:
    if elapsed_seconds is not None and exercise.mode == "Timed":
        max_seconds = exercise.estimated_time_minutes * 60
        if 0 < elapsed_seconds <= max_seconds:
            return elapsed_seconds
    return None


def api_list_exercises(
    request: Request,
    dataset: str | None = None,
    difficulty: str | None = None,
    mode: str | None = None,
) -> dict[str, Any]:
    filters = parse_workspace_filters(difficulty=difficulty, mode=mode)
    if dataset:
        filters = PracticeFilters(
            dataset_id=dataset,
            difficulty=filters.difficulty,
            mode=filters.mode,
        )
    exercises = filtered_exercises(filters)
    return {
        "exercises": [_exercise_list_item(exercise, request) for exercise in exercises],
        "total": len(exercises),
    }


def api_get_exercise(
    request: Request,
    dataset_id: str,
    exercise_id: str,
    difficulty: str | None = None,
    mode: str | None = None,
) -> dict[str, Any]:
    filters = parse_workspace_filters(difficulty=difficulty, mode=mode)
    context = get_workspace_context(request, dataset_id, exercise_id, filters)
    if context is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {
        "exercise": context["exercise"],
        "dataset": context["dataset"],
        "schema": context["schema"],
        "attempt": {
            "sql": context["sql"],
            "query_result": context["query_result"],
            "execution_error": context["execution_error"],
            "grading": context["grading"],
            "status": context["attempt_status"],
        },
        "progress": {
            "status": context["progress_status"],
            "label": context["progress_label"],
            "best_elapsed": context["best_elapsed"],
        },
        "navigation": context["navigation"],
        "filters": context["filters"],
    }


def api_run_sql(
    request: Request,
    dataset_id: str,
    exercise_id: str,
    body: RunRequest,
) -> JSONResponse:
    exercise = lookup_exercise(dataset_id, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    outcome = execute_query(body.sql)
    store_run_result(request, exercise.id, body.sql, outcome)
    if isinstance(outcome, ExecutionError):
        return JSONResponse(
            status_code=422,
            content={"error": _serialize_execution_error(outcome)},
        )
    return JSONResponse(content=_serialize_query_result(outcome))


def api_submit_sql(
    request: Request,
    dataset_id: str,
    exercise_id: str,
    body: SubmitRequest,
) -> JSONResponse:
    exercise = lookup_exercise(dataset_id, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    outcome = execute_query(body.sql)
    grading = store_submit_result(request, exercise, body.sql, outcome)
    if grading is None:
        if isinstance(outcome, ExecutionError):
            return JSONResponse(
                status_code=422,
                content={"error": _serialize_execution_error(outcome)},
            )
        return JSONResponse(
            status_code=422,
            content={"error": {"message": "Grading unavailable", "code": "grading_unavailable"}},
        )

    elapsed = _parse_elapsed_seconds(exercise, body.elapsed_seconds)
    progress = load_progress(request).apply_submit_outcome(
        exercise.id,
        passed=grading.passed is True,
        elapsed_seconds=elapsed,
    )
    response = JSONResponse(
        content={
            "grading": {
                "exercise_id": grading.exercise_id,
                "status": grading.status,
                "summary": grading.summary,
                "passed": grading.passed,
                "is_placeholder": grading.is_placeholder,
            },
            "progress": {
                "passed_count": progress.passed_count(),
                "total": len(TIMES_ARCHIVE_CATALOG.exercises),
            },
        }
    )
    attach_progress_cookie(response, progress)
    return response


def api_clear_progress() -> JSONResponse:
    response = JSONResponse(content={"ok": True})
    clear_progress_cookie(response)
    attach_progress_cookie(response, ProgressStore())
    return response
