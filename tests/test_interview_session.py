from starlette.requests import Request

from app.interview.session import (
    InterviewOutcome,
    InterviewSession,
    advance,
    build_summary,
    clear_interview_session,
    create_interview_session,
    current_exercise,
    current_exercise_url,
    end_session_early,
    load_interview_session,
    record_outcome,
    save_interview_session,
)


def _request() -> Request:
    return Request({"type": "http", "session": {}})


def test_create_interview_session_fixed_queue() -> None:
    session = create_interview_session(requested_length=3)
    assert session is not None
    assert session.queue_mode == "fixed"
    assert session.requested_length == 3
    assert len(session.queue) == 3
    assert session.status == "active"
    assert session.current_index == 0


def test_create_interview_session_unlimited_queue() -> None:
    session = create_interview_session(requested_length=None)
    assert session is not None
    assert session.queue_mode == "unlimited"
    assert session.requested_length is None
    assert len(session.queue) == 50


def test_session_roundtrip_via_request() -> None:
    request = _request()
    session = create_interview_session(requested_length=5, difficulty="Beginner")
    assert session is not None
    save_interview_session(request, session)
    loaded = load_interview_session(request)
    assert loaded == session


def test_record_outcome_persists() -> None:
    request = _request()
    session = create_interview_session(requested_length=3)
    assert session is not None
    save_interview_session(request, session)
    exercise_id = session.queue[0]
    updated = record_outcome(
        request,
        exercise_id,
        passed=True,
        elapsed_seconds=125,
    )
    assert updated is not None
    assert updated.outcomes[exercise_id].passed is True
    assert updated.outcomes[exercise_id].elapsed_seconds == 125


def test_current_exercise_and_url() -> None:
    session = create_interview_session(requested_length=3)
    assert session is not None
    exercise = current_exercise(session)
    assert exercise is not None
    assert exercise.id == session.queue[0]
    assert current_exercise_url(session) == (
        f"/practice/interview/{exercise.dataset_id}/{exercise.id}"
    )


def test_advance_moves_index_and_completes_at_end() -> None:
    session = create_interview_session(requested_length=2)
    assert session is not None
    advanced = advance(session)
    assert advanced.current_index == 1
    assert advanced.status == "active"
    completed = advance(advanced)
    assert completed.current_index == 2
    assert completed.status == "completed"


def test_end_session_early_sets_status() -> None:
    session = create_interview_session(requested_length=3)
    assert session is not None
    ended = end_session_early(session)
    assert ended.status == "ended_early"


def test_build_summary_aggregates_outcomes() -> None:
    session = create_interview_session(requested_length=2)
    assert session is not None
    session = session.model_copy(
        update={
            "outcomes": {
                session.queue[0]: InterviewOutcome(passed=True, elapsed_seconds=60),
                session.queue[1]: InterviewOutcome(passed=False, elapsed_seconds=30),
            }
        }
    )
    summary = build_summary(session)
    assert summary.passed_count == 1
    assert summary.queue_length == 2
    assert summary.total_elapsed_seconds == 90
    assert summary.total_elapsed_label == "1:30"
    assert len(summary.items) == 2


def test_clear_interview_session() -> None:
    request = _request()
    session = create_interview_session(requested_length=3)
    assert session is not None
    save_interview_session(request, session)
    clear_interview_session(request)
    assert load_interview_session(request) is None


def test_has_outcome_for_current() -> None:
    session = InterviewSession(
        queue=("times-archive-001", "times-archive-002"),
        queue_mode="fixed",
        requested_length=2,
        started_at="2026-06-09T00:00:00+00:00",
    )
    assert session.has_outcome_for_current() is False
    session = session.model_copy(
        update={
            "outcomes": {
                "times-archive-001": InterviewOutcome(passed=True),
            }
        }
    )
    assert session.has_outcome_for_current() is True
