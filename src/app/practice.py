from dataclasses import dataclass
from typing import cast

from starlette.requests import Request

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.attempts import DEMO_ATTEMPT
from app.domain.datasets import Dataset
from app.domain.exercises import (
    DIFFICULTY_OPTIONS,
    MODE_OPTIONS,
    Difficulty,
    Exercise,
    PracticeMode,
)
from app.domain.grading import GRADING_PLACEHOLDER
from app.domain.progress import ExerciseProgressStatus, ProgressStore, build_progress_summary
from app.interview.session import interview_resume_context
from app.practice_session import get_attempt_state
from app.progress import (
    continue_exercise_url,
    find_continue_exercise,
    format_elapsed_seconds,
    load_progress,
)

PLACEHOLDER_AREAS = (
    {
        "title": "AI grading",
        "description": "AI explanations and partial credit remain future work.",
    },
)

_PROGRESS_LABELS: dict[ExerciseProgressStatus, str] = {
    "not_started": "Not started",
    "attempted": "Attempted",
    "passed": "Passed",
}


@dataclass(frozen=True)
class PracticeFilters:
    dataset_id: str | None = None
    difficulty: Difficulty | None = None
    mode: PracticeMode | None = None


def _progress_label(status: ExerciseProgressStatus) -> str:
    return _PROGRESS_LABELS[status]


def _dataset_summary(dataset: Dataset) -> dict[str, object]:
    status_label = "Demo data" if dataset.is_demo else "Production catalog"
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "status_label": status_label,
        "source": dataset.provenance.source_name,
        "source_url": dataset.provenance.source_url,
        "schema_reference": dataset.provenance.schema_reference,
        "fixture_path": dataset.provenance.fixture_path,
        "note": dataset.provenance.note,
    }


def _exercise_summary(exercise: Exercise, store: ProgressStore) -> dict[str, object]:
    status = store.get_status(exercise.id)
    record = store.exercises.get(exercise.id)
    best_time = (
        format_elapsed_seconds(record.elapsed_seconds)
        if record is not None and record.elapsed_seconds is not None
        else None
    )
    return {
        "id": exercise.id,
        "dataset_id": exercise.dataset_id,
        "title": exercise.title,
        "prompt": exercise.prompt,
        "difficulty": exercise.difficulty,
        "mode": exercise.mode,
        "target_dialect": exercise.target_dialect,
        "concept_tags": exercise.concept_tags,
        "estimated_time_minutes": exercise.estimated_time_minutes,
        "availability_status": exercise.availability_status,
        "hint": exercise.hint,
        "preview_url": f"/practice/{exercise.dataset_id}/{exercise.id}",
        "progress_status": status,
        "progress_label": _progress_label(status),
        "best_elapsed": best_time,
    }


def _filter_exercises(
    exercises: tuple[Exercise, ...],
    filters: PracticeFilters,
) -> tuple[Exercise, ...]:
    filtered = exercises
    if filters.dataset_id:
        filtered = tuple(
            exercise for exercise in filtered if exercise.dataset_id == filters.dataset_id
        )
    if filters.difficulty:
        filtered = tuple(
            exercise for exercise in filtered if exercise.difficulty == filters.difficulty
        )
    if filters.mode:
        filtered = tuple(exercise for exercise in filtered if exercise.mode == filters.mode)
    return filtered


def _continue_context(store: ProgressStore, difficulty: Difficulty | None) -> dict[str, object]:
    continue_exercise = find_continue_exercise(store, difficulty=difficulty)
    continue_url = continue_exercise_url(continue_exercise)
    if continue_url is None:
        return {
            "continue_url": None,
            "continue_label": "All exercises passed — browse catalog",
        }
    assert continue_exercise is not None
    return {
        "continue_url": continue_url,
        "continue_label": f"Continue practicing: {continue_exercise.title}",
    }


def lookup_dataset(dataset_id: str) -> Dataset | None:
    for dataset in TIMES_ARCHIVE_CATALOG.datasets:
        if dataset.id == dataset_id:
            return dataset
    return None


def lookup_exercise(dataset_id: str, exercise_id: str) -> Exercise | None:
    for exercise in TIMES_ARCHIVE_CATALOG.exercises:
        if exercise.dataset_id == dataset_id and exercise.id == exercise_id:
            return exercise
    return None


def get_home_context(request: Request) -> dict[str, object]:
    store = load_progress(request)
    total = len(TIMES_ARCHIVE_CATALOG.exercises)
    summary = build_progress_summary(store, total)
    continue_info = _continue_context(store, difficulty=None)
    return {
        "progress_summary": summary,
        "passed_count": store.passed_count(),
        "total_exercise_count": total,
        **continue_info,
        **interview_resume_context(request),
    }


def get_exercise_preview_context(
    request: Request,
    dataset_id: str,
    exercise_id: str,
) -> dict[str, object] | None:
    dataset = lookup_dataset(dataset_id)
    exercise = lookup_exercise(dataset_id, exercise_id)
    if dataset is None or exercise is None:
        return None

    store = load_progress(request)
    attempt_state = get_attempt_state(request, exercise.id)
    sql = attempt_state["sql"] or f"-- Write PostgreSQL for: {exercise.title}\n"
    status = store.get_status(exercise.id)
    record = store.exercises.get(exercise.id)
    best_elapsed = (
        format_elapsed_seconds(record.elapsed_seconds)
        if record is not None and record.elapsed_seconds is not None
        else None
    )

    return {
        "page_title": f"{exercise.title} - Practice - SQL Gym",
        "status_label": "Exercise practice",
        "dataset": _dataset_summary(dataset),
        "exercise": {
            "id": exercise.id,
            "title": exercise.title,
            "prompt": exercise.prompt,
            "difficulty": exercise.difficulty,
            "mode": exercise.mode,
            "target_dialect": exercise.target_dialect,
            "concept_tags": exercise.concept_tags,
            "estimated_time_minutes": exercise.estimated_time_minutes,
            "learning_objectives": exercise.learning_objectives,
            "availability_status": exercise.availability_status,
            "hint": exercise.hint,
            "sample_sql": exercise.sample_sql,
        },
        "sql": sql,
        "query_result": attempt_state["query_result"],
        "execution_error": attempt_state["execution_error"],
        "grading": attempt_state["grading"],
        "attempt_status": attempt_state["status"],
        "progress_status": status,
        "progress_label": _progress_label(status),
        "best_elapsed": best_elapsed,
        "placeholder_areas": PLACEHOLDER_AREAS,
    }


def get_not_found_context(resource_label: str) -> dict[str, object]:
    return {
        "page_title": "Not found - SQL Gym",
        "status_label": "Not found",
        "resource_label": resource_label,
        "message": f"We could not find that {resource_label} in the practice catalog.",
    }


def get_practice_context(
    request: Request,
    dataset_id: str | None = None,
    difficulty: str | None = None,
    mode: str | None = None,
) -> dict[str, object]:
    catalog = TIMES_ARCHIVE_CATALOG
    store = load_progress(request)
    parsed_difficulty = (
        cast(Difficulty, difficulty)
        if difficulty in {"Beginner", "Intermediate", "Advanced"}
        else None
    )
    parsed_mode = cast(PracticeMode, mode) if mode in {"Untimed", "Timed"} else None
    filters = PracticeFilters(
        dataset_id=dataset_id or None,
        difficulty=parsed_difficulty,
        mode=parsed_mode,
    )
    datasets = [_dataset_summary(dataset) for dataset in catalog.datasets]
    exercises = _filter_exercises(catalog.exercises, filters)
    grouped_exercises: dict[str, list[dict[str, object]]] = {
        difficulty_option.label: [] for difficulty_option in DIFFICULTY_OPTIONS
    }
    for exercise in exercises:
        grouped_exercises[exercise.difficulty].append(_exercise_summary(exercise, store))
    grouped_exercises = {
        difficulty_key: items for difficulty_key, items in grouped_exercises.items() if items
    }
    summary = build_progress_summary(store, len(catalog.exercises))

    return {
        "page_title": "Practice - SQL Gym",
        "status_label": "Practice catalog",
        "datasets": datasets,
        "difficulties": DIFFICULTY_OPTIONS,
        "modes": MODE_OPTIONS,
        "filters": {
            "dataset_id": filters.dataset_id or "",
            "difficulty": filters.difficulty or "",
            "mode": filters.mode or "",
        },
        "exercises": [_exercise_summary(exercise, store) for exercise in exercises],
        "grouped_exercises": grouped_exercises,
        "exercise_count": len(exercises),
        "total_exercise_count": len(catalog.exercises),
        "placeholder_areas": PLACEHOLDER_AREAS,
        "progress": summary.metrics,
        "passed_count": store.passed_count(),
        "attempt": DEMO_ATTEMPT,
        "grading": GRADING_PLACEHOLDER,
        "execution_available": True,
        **_continue_context(store, parsed_difficulty),
        **interview_resume_context(request),
    }
