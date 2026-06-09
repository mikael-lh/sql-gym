from __future__ import annotations

from typing import cast

from starlette.requests import Request

from app.domain.exercises import DIFFICULTY_OPTIONS, Difficulty
from app.interview.queue import FIXED_QUEUE_LENGTHS, count_eligible_exercises
from app.interview.session import load_interview_session
from app.practice import lookup_exercise
from app.practice_session import get_attempt_state
from app.progress import format_elapsed_seconds, load_progress


def _parse_difficulty(value: str | None) -> Difficulty | None:
    if value in {"Beginner", "Intermediate", "Advanced"}:
        return cast(Difficulty, value)
    return None


def get_interview_start_context(
    request: Request,
    *,
    difficulty: str | None = None,
    queue_length: str | None = None,
) -> dict[str, object]:
    parsed_difficulty = _parse_difficulty(difficulty)
    eligible_count = count_eligible_exercises(parsed_difficulty)
    selected_length = queue_length if queue_length in {"3", "5", "8", "unlimited"} else "5"
    return {
        "page_title": "Start interview session - SQL Gym",
        "status_label": "Interview session",
        "difficulties": DIFFICULTY_OPTIONS,
        "queue_lengths": [
            {"value": str(length), "label": f"{length} questions"}
            for length in FIXED_QUEUE_LENGTHS
        ]
        + [{"value": "unlimited", "label": "Unlimited (all eligible exercises)"}],
        "selected_difficulty": parsed_difficulty or "",
        "selected_queue_length": selected_length,
        "eligible_count": eligible_count,
        "can_start": eligible_count > 0,
        "has_active_session": load_interview_session(request) is not None,
    }


def parse_interview_start_form(
    *,
    queue_length: str,
    difficulty: str | None = None,
) -> tuple[int | None, Difficulty | None] | None:
    parsed_difficulty = _parse_difficulty(difficulty)
    if queue_length == "unlimited":
        return None, parsed_difficulty
    if queue_length in {str(length) for length in FIXED_QUEUE_LENGTHS}:
        return int(queue_length), parsed_difficulty
    return None


def get_interview_exercise_context(
    request: Request,
    dataset_id: str,
    exercise_id: str,
) -> dict[str, object] | None:
    from app.practice import get_exercise_preview_context, lookup_dataset

    session = load_interview_session(request)
    if session is None or not session.is_active:
        return None

    current_id = session.current_exercise_id()
    if current_id != exercise_id:
        return None

    base_context = get_exercise_preview_context(request, dataset_id, exercise_id)
    if base_context is None:
        return None

    exercise = lookup_exercise(dataset_id, exercise_id)
    dataset = lookup_dataset(dataset_id)
    if exercise is None or dataset is None:
        return None

    attempt_state = get_attempt_state(request, exercise.id)
    question_number = session.current_index + 1
    queue_length = session.queue_length
    question_label = (
        f"Question {question_number} of {queue_length}"
        if session.queue_mode == "fixed"
        else f"Question {question_number}"
    )
    has_outcome = session.has_outcome_for_current()
    is_last = session.is_last_question()

    return {
        **base_context,
        "page_title": f"{exercise.title} - Interview - SQL Gym",
        "status_label": "Interview session",
        "interview": {
            "question_label": question_label,
            "question_number": question_number,
            "queue_length": queue_length,
            "queue_mode": session.queue_mode,
            "has_outcome": has_outcome,
            "is_last_question": is_last,
            "can_advance": has_outcome and not is_last,
            "can_end_early": has_outcome,
            "can_view_summary": has_outcome and is_last,
        },
        "dataset": base_context["dataset"],
        "sql": attempt_state["sql"] or f"-- Write PostgreSQL for: {exercise.title}\n",
        "query_result": attempt_state["query_result"],
        "execution_error": attempt_state["execution_error"],
        "grading": attempt_state["grading"],
    }


def get_interview_summary_context(request: Request) -> dict[str, object] | None:
    from app.interview.session import build_summary

    session = load_interview_session(request)
    if session is None:
        return None
    if session.status not in {"completed", "ended_early"}:
        return None
    summary = build_summary(session)
    return {
        "page_title": "Interview summary - SQL Gym",
        "status_label": "Interview session",
        "summary": summary,
        "items": summary.items,
        "passed_count": summary.passed_count,
        "queue_length": summary.queue_length,
        "total_elapsed_label": summary.total_elapsed_label,
        "ended_early": session.status == "ended_early",
    }


def format_best_elapsed(request: Request, exercise_id: str) -> str | None:
    store = load_progress(request)
    record = store.exercises.get(exercise_id)
    if record is None or record.elapsed_seconds is None:
        return None
    return format_elapsed_seconds(record.elapsed_seconds)
