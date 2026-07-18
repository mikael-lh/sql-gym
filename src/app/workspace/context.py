from __future__ import annotations

from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field
from starlette.requests import Request

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.catalog.output_requirements import build_output_requirements_text
from app.catalog.schema import DatasetSchema, get_dataset_schema
from app.domain.exercises import DIFFICULTY_OPTIONS, Difficulty, SelectionOption
from app.domain.progress import ExerciseProgressStatus, progress_label_for_status
from app.practice import PracticeFilters, lookup_dataset, lookup_exercise
from app.practice_session import get_attempt_state
from app.progress import format_elapsed_seconds, load_progress
from app.workspace.navigation import (
    default_workspace_exercise,
    exercise_workspace_path,
    filtered_exercises,
    workspace_navigation,
)


class WorkspaceDatasetView(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    description: str


class WorkspaceExerciseView(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    dataset_id: str
    title: str
    prompt: str
    output_requirements: str
    difficulty: Difficulty
    target_dialect: str
    concept_tags: tuple[str, ...]
    estimated_time_minutes: int
    learning_objectives: tuple[str, ...]
    availability_status: str
    hint: str
    sample_sql: str
    reference_sql: str | None


class WorkspaceAttemptView(BaseModel):
    model_config = ConfigDict(frozen=True)

    sql: str
    query_result: object | None
    execution_error: object | None
    grading: object | None
    status: str


class WorkspaceProgressView(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: ExerciseProgressStatus
    label: str
    first_pass_elapsed: str | None


class WorkspaceFiltersView(BaseModel):
    model_config = ConfigDict(frozen=True)

    difficulty: str


class WorkspaceNavigationView(BaseModel):
    model_config = ConfigDict(frozen=True)

    index: int | None
    total: int
    position_label: str | None
    prev_url: str | None
    next_url: str | None


class WorkspaceContext(BaseModel):
    """Typed workspace page/API payload without duplicated top-level aliases."""

    model_config = ConfigDict(frozen=True)

    page_title: str
    status_label: str
    dataset: WorkspaceDatasetView
    # Named dataset_schema to avoid shadowing BaseModel.schema / mypy conflict.
    dataset_schema: DatasetSchema | None = Field(validation_alias="schema")
    exercise: WorkspaceExerciseView
    attempt: WorkspaceAttemptView
    progress: WorkspaceProgressView
    navigation: WorkspaceNavigationView
    filters: WorkspaceFiltersView
    difficulties: tuple[SelectionOption, ...]
    passed_count: int
    total_exercise_count: int
    filtered_exercise_count: int

    def workspace_config(self) -> dict[str, object]:
        return {
            "dataset_id": self.dataset.id,
            "exercise_id": self.exercise.id,
            "filters": self.filters.model_dump(),
            "navigation": self.navigation.model_dump(),
            "attempt": {
                "query_result": self.attempt.query_result,
                "execution_error": self.attempt.execution_error,
            },
            "progress": {
                "status": self.progress.status,
                "first_pass_elapsed": self.progress.first_pass_elapsed,
            },
        }

    def as_template_context(self) -> dict[str, Any]:
        """Jinja mapping: nested fields only (no duplicated top-level aliases)."""
        return {
            "page_title": self.page_title,
            "status_label": self.status_label,
            "dataset": self.dataset.model_dump(),
            "schema": (
                self.dataset_schema.model_dump() if self.dataset_schema is not None else None
            ),
            "exercise": self.exercise.model_dump(),
            "attempt": self.attempt.model_dump(),
            "progress": self.progress.model_dump(),
            "navigation": self.navigation.model_dump(),
            "filters": self.filters.model_dump(),
            "difficulties": [item.model_dump() for item in self.difficulties],
            "passed_count": self.passed_count,
            "total_exercise_count": self.total_exercise_count,
            "filtered_exercise_count": self.filtered_exercise_count,
            "workspace_config": self.workspace_config(),
        }


def parse_workspace_filters(
    *,
    difficulty: str | None = None,
) -> PracticeFilters:
    parsed_difficulty = (
        cast(Difficulty, difficulty) if difficulty in {"Intermediate", "Advanced"} else None
    )
    return PracticeFilters(difficulty=parsed_difficulty)


def get_workspace_context(
    request: Request,
    dataset_id: str,
    exercise_id: str,
    filters: PracticeFilters,
) -> WorkspaceContext | None:
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
    navigation = WorkspaceNavigationView.model_validate(workspace_navigation(exercise.id, filters))
    output_requirements = build_output_requirements_text(exercise)

    return WorkspaceContext.model_validate(
        {
            "page_title": f"{exercise.title} - SQL Gym",
            "status_label": "Practice workspace",
            "dataset": {
                "id": dataset.id,
                "name": dataset.name,
                "description": dataset.description,
            },
            "schema": schema,
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
            "attempt": {
                "sql": attempt_state["sql"],
                "query_result": attempt_state["query_result"],
                "execution_error": attempt_state["execution_error"],
                "grading": attempt_state["grading"],
                "status": attempt_state["status"],
            },
            "progress": {
                "status": status,
                "label": progress_label_for_status(status),
                "first_pass_elapsed": first_pass_elapsed,
            },
            "navigation": navigation,
            "filters": {
                "difficulty": filters.difficulty or "",
            },
            "difficulties": DIFFICULTY_OPTIONS,
            "passed_count": store.passed_count(),
            "total_exercise_count": len(TIMES_ARCHIVE_CATALOG.exercises),
            "filtered_exercise_count": len(eligible),
        }
    )


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
