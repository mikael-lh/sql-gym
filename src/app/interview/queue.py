from __future__ import annotations

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.exercises import Difficulty, Exercise

FIXED_QUEUE_LENGTHS: tuple[int, ...] = (3, 5, 8)


def eligible_interview_exercises(
    difficulty: Difficulty | None = None,
) -> tuple[Exercise, ...]:
    exercises: list[Exercise] = []
    for exercise in TIMES_ARCHIVE_CATALOG.exercises:
        if difficulty is not None and exercise.difficulty != difficulty:
            continue
        exercises.append(exercise)
    return tuple(exercises)


def count_eligible_exercises(difficulty: Difficulty | None = None) -> int:
    return len(eligible_interview_exercises(difficulty))


def build_interview_queue(
    requested_length: int | None,
    difficulty: Difficulty | None = None,
) -> list[Exercise]:
    eligible = eligible_interview_exercises(difficulty)
    if not eligible:
        return []
    if requested_length is None:
        return list(eligible)
    return list(eligible[: min(requested_length, len(eligible))])
