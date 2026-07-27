from __future__ import annotations

from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.ai.explain import (
    MSG_NO_FAILED_ATTEMPT,
    ExplainFailure,
    ExplainSuccess,
    explain_failed_attempt,
)
from app.api.serializers import (
    serialize_execution_error,
    serialize_grading,
    serialize_query_result,
)
from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.exercises import Exercise
from app.domain.progress import ProgressStore, progress_label_for_status
from app.execution import execute_query
from app.execution.models import ExecutionError
from app.practice import PracticeFilters, lookup_exercise
from app.practice_session import (
    get_failed_submit_attempt,
    store_run_result,
    store_submit_result,
)
from app.progress import attach_progress_cookie, clear_progress_cookie, load_progress
from app.workspace.context import get_workspace_context, parse_workspace_filters
from app.workspace.navigation import filtered_exercises


class RunRequest(BaseModel):
    sql: str


class SubmitRequest(BaseModel):
    sql: str
    elapsed_seconds: int | None = None


def _exercise_list_item(exercise: Exercise, request: Request) -> dict[str, Any]:
    store = load_progress(request)
    status = store.get_status(exercise.id)
    return {
        "id": exercise.id,
        "dataset_id": exercise.dataset_id,
        "title": exercise.title,
        "difficulty": exercise.difficulty,
        "progress_status": status,
        "progress_label": progress_label_for_status(status),
        "url": f"/practice/{exercise.dataset_id}/{exercise.id}",
    }


def _parse_elapsed_seconds(elapsed_seconds: int | None) -> int | None:
    if elapsed_seconds is not None and elapsed_seconds > 0:
        return elapsed_seconds
    return None


def api_list_exercises(
    request: Request,
    dataset: str | None = None,
    difficulty: str | None = None,
) -> dict[str, Any]:
    filters = parse_workspace_filters(difficulty=difficulty)
    if dataset:
        filters = PracticeFilters(
            dataset_id=dataset,
            difficulty=filters.difficulty,
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
) -> dict[str, Any]:
    filters = parse_workspace_filters(difficulty=difficulty)
    context = get_workspace_context(request, dataset_id, exercise_id, filters)
    if context is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return {
        "exercise": context.exercise.model_dump(),
        "dataset": context.dataset.model_dump(),
        "schema": (
            context.dataset_schema.model_dump() if context.dataset_schema is not None else None
        ),
        "attempt": {
            "sql": context.attempt.sql,
            "query_result": context.attempt.query_result,
            "execution_error": context.attempt.execution_error,
            "grading": context.attempt.grading,
            "status": context.attempt.status,
        },
        "progress": {
            "status": context.progress.status,
            "label": context.progress.label,
            "first_pass_elapsed": context.progress.first_pass_elapsed,
        },
        "navigation": context.navigation.model_dump(),
        "filters": context.filters.model_dump(),
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
            content={"error": serialize_execution_error(outcome, for_run=True)},
        )
    return JSONResponse(content=serialize_query_result(outcome))


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
                content={"error": serialize_execution_error(outcome)},
            )
        return JSONResponse(
            status_code=422,
            content={"error": {"message": "Grading unavailable", "code": "grading_unavailable"}},
        )

    elapsed = _parse_elapsed_seconds(body.elapsed_seconds)
    progress = load_progress(request).apply_submit_outcome(
        exercise.id,
        passed=grading.passed is True,
        elapsed_seconds=elapsed,
    )
    status = progress.get_status(exercise.id)
    response = JSONResponse(
        content={
            "grading": serialize_grading(grading),
            "progress": {
                "passed_count": progress.passed_count(),
                "total": len(TIMES_ARCHIVE_CATALOG.exercises),
                "status": status,
                "label": progress_label_for_status(status),
            },
        }
    )
    attach_progress_cookie(response, progress)
    return response


def api_explain_failed_attempt(
    request: Request,
    dataset_id: str,
    exercise_id: str,
) -> JSONResponse:
    exercise = lookup_exercise(dataset_id, exercise_id)
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")

    attempt = get_failed_submit_attempt(request, exercise.id)
    if attempt is None:
        return JSONResponse(
            status_code=422,
            content={"error": {"message": MSG_NO_FAILED_ATTEMPT}},
        )

    result = explain_failed_attempt(exercise, attempt)
    if isinstance(result, ExplainSuccess):
        return JSONResponse(content={"explanation": result.explanation})
    assert isinstance(result, ExplainFailure)
    return JSONResponse(
        status_code=result.status_code,
        content={"error": {"message": result.message}},
    )


def api_clear_progress() -> JSONResponse:
    cleared = ProgressStore()
    response = JSONResponse(
        content={
            "ok": True,
            "progress": {
                "passed_count": 0,
                "status": "not_started",
                "label": progress_label_for_status("not_started"),
            },
        }
    )
    clear_progress_cookie(response)
    attach_progress_cookie(response, cleared)
    return response
