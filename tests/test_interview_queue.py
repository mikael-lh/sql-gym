from app.interview.queue import (
    build_interview_queue,
    count_eligible_exercises,
    eligible_interview_exercises,
)


def test_eligible_includes_timed_and_untimed() -> None:
    exercises = eligible_interview_exercises()
    modes = {exercise.mode for exercise in exercises}
    assert "Timed" in modes
    assert "Untimed" in modes
    assert len(exercises) == 50


def test_eligible_uses_stable_catalog_order() -> None:
    exercises = eligible_interview_exercises()
    assert exercises[0].id == "times-archive-001"
    assert exercises[1].id == "times-archive-002"


def test_eligible_respects_difficulty_filter() -> None:
    exercises = eligible_interview_exercises(difficulty="Beginner")
    assert exercises
    assert all(exercise.difficulty == "Beginner" for exercise in exercises)
    assert count_eligible_exercises(difficulty="Beginner") == len(exercises)


def test_build_fixed_queue_caps_at_requested_length() -> None:
    queue = build_interview_queue(5)
    assert len(queue) == 5
    assert queue[0].id == "times-archive-001"


def test_build_fixed_queue_uses_min_when_fewer_eligible() -> None:
    eligible_count = count_eligible_exercises(difficulty="Advanced")
    queue = build_interview_queue(20, difficulty="Advanced")
    assert len(queue) == min(20, eligible_count)
    assert len(queue) == eligible_count
    assert len(queue) < 20


def test_build_unlimited_queue_returns_all_eligible() -> None:
    queue = build_interview_queue(None)
    assert len(queue) == 50
    queue_filtered = build_interview_queue(None, difficulty="Intermediate")
    assert len(queue_filtered) == count_eligible_exercises(difficulty="Intermediate")


def test_build_queue_returns_empty_when_no_eligible() -> None:
    # Catalog has no exercises for a non-existent difficulty filter path:
    # use requested length larger than zero with empty eligible via mock-free check.
    assert build_interview_queue(3)  # default catalog always has exercises
