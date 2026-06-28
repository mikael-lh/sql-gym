from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.progress import ProgressStore
from app.progress.navigation import continue_exercise_url, find_continue_exercise


def test_find_continue_uses_catalog_order() -> None:
    store = ProgressStore()
    store = store.apply_submit_outcome("times-archive-011", passed=True)
    exercise = find_continue_exercise(store)
    assert exercise is not None
    assert exercise.id == "times-archive-012"


def test_find_continue_respects_difficulty_filter() -> None:
    store = ProgressStore()
    for exercise_id in ("times-archive-011", "times-archive-012", "times-archive-013"):
        store = store.apply_submit_outcome(exercise_id, passed=True)
    exercise = find_continue_exercise(store, difficulty="Intermediate")
    assert exercise is not None
    assert exercise.difficulty == "Intermediate"


def test_continue_url_none_when_complete() -> None:
    store = ProgressStore()
    for exercise in TIMES_ARCHIVE_CATALOG.exercises:
        store = store.apply_submit_outcome(exercise.id, passed=True)
    assert find_continue_exercise(store) is None
    assert continue_exercise_url(None) is None
