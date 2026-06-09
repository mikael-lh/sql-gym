from __future__ import annotations

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.exercises import Difficulty, Exercise
from app.domain.progress import ProgressStore


def find_continue_exercise(
    store: ProgressStore,
    *,
    difficulty: Difficulty | None = None,
) -> Exercise | None:
    for exercise in TIMES_ARCHIVE_CATALOG.exercises:
        if difficulty is not None and exercise.difficulty != difficulty:
            continue
        if store.get_status(exercise.id) != "passed":
            return exercise
    return None


def continue_exercise_url(exercise: Exercise | None) -> str | None:
    if exercise is None:
        return None
    return f"/practice/{exercise.dataset_id}/{exercise.id}"


def format_elapsed_seconds(seconds: int | None) -> str | None:
    if seconds is None:
        return None
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes}:{remainder:02d}"
