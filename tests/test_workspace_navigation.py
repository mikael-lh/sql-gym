from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.progress import ProgressStore
from app.practice import PracticeFilters
from app.workspace.navigation import (
    default_workspace_exercise,
    exercise_workspace_path,
    filtered_exercises,
    workspace_navigation,
)


def test_filtered_exercises_by_difficulty() -> None:
    filters = PracticeFilters(difficulty="Beginner")
    exercises = filtered_exercises(filters)
    assert exercises
    assert all(exercise.difficulty == "Beginner" for exercise in exercises)


def test_filtered_exercises_by_mode() -> None:
    filters = PracticeFilters(mode="Timed")
    exercises = filtered_exercises(filters)
    assert exercises
    assert all(exercise.mode == "Timed" for exercise in exercises)


def test_exercise_workspace_path_includes_query_params() -> None:
    exercise = TIMES_ARCHIVE_CATALOG.exercises[0]
    path = exercise_workspace_path(exercise, difficulty="Beginner", mode="Timed")
    assert path.startswith(f"/practice/{exercise.dataset_id}/{exercise.id}?")
    assert "difficulty=Beginner" in path
    assert "mode=Timed" in path


def test_workspace_navigation_prev_next() -> None:
    eligible = filtered_exercises(PracticeFilters())
    exercise = eligible[5]
    nav = workspace_navigation(exercise.id, PracticeFilters())
    assert nav["index"] == 5
    assert nav["total"] == len(eligible)
    assert nav["prev_url"] is not None
    assert nav["next_url"] is not None
    assert "Exercise 6 of" in str(nav["position_label"])


def test_workspace_navigation_first_exercise_has_no_prev() -> None:
    eligible = filtered_exercises(PracticeFilters())
    nav = workspace_navigation(eligible[0].id, PracticeFilters())
    assert nav["prev_url"] is None
    assert nav["next_url"] is not None


def test_default_workspace_exercise_uses_continue_semantics() -> None:
    store = ProgressStore()
    exercise = default_workspace_exercise(store, PracticeFilters())
    assert exercise is not None
    assert exercise.id == TIMES_ARCHIVE_CATALOG.exercises[0].id
