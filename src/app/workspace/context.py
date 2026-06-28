from __future__ import annotations

from typing import cast

from starlette.requests import Request

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.catalog.output_requirements import build_output_requirements_text
from app.catalog.schema import DatasetSchema, get_dataset_schema
from app.domain.exercises import DIFFICULTY_OPTIONS, Difficulty
from app.practice import PracticeFilters, lookup_dataset, lookup_exercise
from app.practice_session import get_attempt_state
from app.progress import format_elapsed_seconds, load_progress
from app.workspace.navigation import (
    default_workspace_exercise,
    exercise_workspace_path,
    filtered_exercises,
    workspace_navigation,
)

_PROGRESS_LABELS = {
    "not_started": "Not started",
    "attempted": "Attempted",
    "passed": "Passed",
}


def parse_workspace_filters(
    *,
    difficulty: str | None = None,
) -> PracticeFilters:
    parsed_difficulty = (
        cast(Difficulty, difficulty)
        if difficulty in {"Intermediate", "Advanced"}
        else None
    )
    return PracticeFilters(difficulty=parsed_difficulty)


def _schema_payload(schema: DatasetSchema | None) -> dict[str, object] | None:
    if schema is None:
        return None
    return schema.model_dump()


def get_workspace_context(
    request: Request,
    dataset_id: str,
    exercise_id: str,
    filters: PracticeFilters,
) -> dict[str, object] | None:
    dataset = lookup_dataset(dataset_id)
    exercise = lookup_exercise(dataset_id, exercise_id)
    if dataset is None or exercise is None:
        return None

    eligible = filtered_exercises(filters)
    eligible_ids = {item.id for item in eligible}
    if exercise.id not in eligible_ids:
        return None

    store = load_progress(request)
    attempt_state = get_attempt_state(request, exercise.id)
    status = store.get_status(exercise.id)
    record = store.exercises.get(exercise.id)
    first_pass_elapsed = (
        format_elapsed_seconds(record.elapsed_seconds)
        if record is not None and record.elapsed_seconds is not None
        else None
    )
    schema = get_dataset_schema(dataset_id)
    navigation = workspace_navigation(exercise.id, filters)
    output_requirements = build_output_requirements_text(exercise)
    workspace_config = {
        "dataset_id": dataset_id,
        "exercise_id": exercise_id,
        "filters": {
            "difficulty": filters.difficulty or "",
        },
        "navigation": navigation,
        "attempt": {
            "query_result": attempt_state["query_result"],
            "execution_error": attempt_state["execution_error"],
        },
        "progress": {
            "status": status,
            "first_pass_elapsed": first_pass_elapsed,
        },
    }

    return {
        "page_title": f"{exercise.title} - SQL Gym",
        "status_label": "Practice workspace",
        "dataset": {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
        },
        "schema": _schema_payload(schema),
        "output_requirements": output_requirements,
        "exercise": {
            "id": exercise.id,
            "dataset_id": exercise.dataset_id,
            "title": exercise.title,
            "prompt": exercise.prompt,
            "output_requirements": output_requirements,
            "difficulty": exercise.difficulty,
            "target_dialect": exercise.target_dialect,
            "concept_tags": exercise.concept_tags,
            "estimated_time_minutes": exercise.estimated_time_minutes,
            "learning_objectives": exercise.learning_objectives,
            "availability_status": exercise.availability_status,
            "hint": exercise.hint,
            "sample_sql": exercise.sample_sql,
            "reference_sql": exercise.expected_result.reference_sql,
        },
        "sql": attempt_state["sql"],
        "query_result": attempt_state["query_result"],
        "execution_error": attempt_state["execution_error"],
        "grading": attempt_state["grading"],
        "attempt_status": attempt_state["status"],
        "progress_status": status,
        "progress_label": _PROGRESS_LABELS[status],
        "first_pass_elapsed": first_pass_elapsed,
        "navigation": navigation,
        "filters": {
            "difficulty": filters.difficulty or "",
        },
        "difficulties": DIFFICULTY_OPTIONS,
        "passed_count": store.passed_count(),
        "total_exercise_count": len(TIMES_ARCHIVE_CATALOG.exercises),
        "filtered_exercise_count": len(eligible),
        "workspace_config": workspace_config,
    }


def get_default_workspace_redirect_url(
    request: Request,
    filters: PracticeFilters,
) -> str | None:
    store = load_progress(request)
    exercise = default_workspace_exercise(store, filters)
    if exercise is None:
        return None
    return exercise_workspace_path(
        exercise,
        difficulty=filters.difficulty,
    )
