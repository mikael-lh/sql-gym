from app.domain.progress import ProgressStore
from app.progress.navigation import continue_exercise_url, find_continue_exercise


def test_find_continue_uses_catalog_order() -> None:
    store = ProgressStore()
    store = store.apply_submit_outcome("times-archive-001", passed=True)
    exercise = find_continue_exercise(store)
    assert exercise is not None
    assert exercise.id == "times-archive-002"


def test_find_continue_respects_difficulty_filter() -> None:
    store = ProgressStore()
    for exercise_id in ("times-archive-001", "times-archive-002", "times-archive-003"):
        store = store.apply_submit_outcome(exercise_id, passed=True)
    exercise = find_continue_exercise(store, difficulty="Intermediate")
    assert exercise is not None
    assert exercise.difficulty == "Intermediate"


def test_continue_url_none_when_complete() -> None:
    store = ProgressStore()
    for index in range(1, 51):
        store = store.apply_submit_outcome(f"times-archive-{index:03d}", passed=True)
    assert find_continue_exercise(store) is None
    assert continue_exercise_url(None) is None
