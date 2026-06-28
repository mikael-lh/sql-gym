from dataclasses import dataclass

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.datasets import Dataset
from app.domain.exercises import Difficulty, Exercise


@dataclass(frozen=True)
class PracticeFilters:
    dataset_id: str | None = None
    difficulty: Difficulty | None = None


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


def get_not_found_context(resource_label: str) -> dict[str, object]:
    return {
        "page_title": "Not found - SQL Gym",
        "status_label": "Not found",
        "resource_label": resource_label,
        "message": f"We could not find that {resource_label} in the practice catalog.",
    }
