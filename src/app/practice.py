from dataclasses import dataclass
from typing import cast

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
from app.domain.progress import DEMO_PROGRESS

PLACEHOLDER_AREAS = (
    {
        "title": "SQL editor",
        "description": "A disabled PostgreSQL-targeted editor placeholder; queries do not run yet.",
    },
    {
        "title": "Grading feedback",
        "description": GRADING_PLACEHOLDER.summary,
    },
    {
        "title": "Progress tracking",
        "description": "Static demo-only progress; no accounts or persistence are active.",
    },
)


@dataclass(frozen=True)
class PracticeFilters:
    dataset_id: str | None = None
    difficulty: Difficulty | None = None
    mode: PracticeMode | None = None


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


def _exercise_summary(exercise: Exercise) -> dict[str, object]:
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


def get_practice_context(
    dataset_id: str | None = None,
    difficulty: str | None = None,
    mode: str | None = None,
) -> dict[str, object]:
    catalog = TIMES_ARCHIVE_CATALOG
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
        difficulty.label: [] for difficulty in DIFFICULTY_OPTIONS
    }
    for exercise in exercises:
        grouped_exercises[exercise.difficulty].append(_exercise_summary(exercise))
    grouped_exercises = {
        difficulty: items for difficulty, items in grouped_exercises.items() if items
    }

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
        "exercises": [_exercise_summary(exercise) for exercise in exercises],
        "grouped_exercises": grouped_exercises,
        "exercise_count": len(exercises),
        "total_exercise_count": len(catalog.exercises),
        "placeholder_areas": PLACEHOLDER_AREAS,
        "progress": DEMO_PROGRESS.metrics,
        "attempt": DEMO_ATTEMPT,
        "grading": GRADING_PLACEHOLDER,
    }
