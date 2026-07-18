from __future__ import annotations

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.exercises import Difficulty, Exercise
from app.domain.progress import ProgressStore
from app.practice import PracticeFilters
from app.progress.navigation import find_continue_exercise


def filtered_exercises(filters: PracticeFilters) -> tuple[Exercise, ...]:
    exercises = TIMES_ARCHIVE_CATALOG.exercises
    if filters.dataset_id:
        exercises = tuple(
            exercise for exercise in exercises if exercise.dataset_id == filters.dataset_id
        )
    if filters.difficulty:
        exercises = tuple(
            exercise for exercise in exercises if exercise.difficulty == filters.difficulty
        )
    return exercises


def exercise_workspace_path(
    exercise: Exercise,
    *,
    difficulty: Difficulty | None = None,
) -> str:
    path = f"/practice/{exercise.dataset_id}/{exercise.id}"
    if difficulty is not None:
        return f"{path}?difficulty={difficulty}"
    return path


def default_workspace_exercise(
    store: ProgressStore,
    filters: PracticeFilters,
) -> Exercise | None:
    eligible = filtered_exercises(filters)
    if not eligible:
        return None
    continue_exercise = find_continue_exercise(store, difficulty=filters.difficulty)
    eligible_ids = {exercise.id for exercise in eligible}
    if continue_exercise is not None and continue_exercise.id in eligible_ids:
        return continue_exercise
    for exercise in eligible:
        if filters.dataset_id and exercise.dataset_id != filters.dataset_id:
            continue
        return exercise
    return eligible[0]


def workspace_navigation(
    exercise_id: str,
    filters: PracticeFilters,
) -> dict[str, object]:
    eligible = filtered_exercises(filters)
    total = len(eligible)
    index = next((i for i, ex in enumerate(eligible) if ex.id == exercise_id), None)
    if index is None or total == 0:
        return {
            "index": None,
            "total": total,
            "position_label": None,
            "prev_url": None,
            "next_url": None,
        }

    position = index + 1
    prev_url = None
    next_url = None
    if index > 0:
        prev_exercise = eligible[index - 1]
        prev_url = exercise_workspace_path(
            prev_exercise,
            difficulty=filters.difficulty,
        )
    if index < total - 1:
        next_exercise = eligible[index + 1]
        next_url = exercise_workspace_path(
            next_exercise,
            difficulty=filters.difficulty,
        )

    return {
        "index": index,
        "total": total,
        "position_label": f"Exercise {position} of {total}",
        "prev_url": prev_url,
        "next_url": next_url,
    }

