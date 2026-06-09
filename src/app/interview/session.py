from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from starlette.requests import Request

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.exercises import Difficulty, Exercise
from app.interview.queue import build_interview_queue

SESSION_KEY = "interview_session"
SCHEMA_VERSION = 1

InterviewSessionStatus = Literal["active", "ended_early", "completed"]
QueueMode = Literal["fixed", "unlimited"]


class InterviewOutcome(BaseModel):
    model_config = ConfigDict(frozen=True)

    passed: bool
    elapsed_seconds: int | None = None


class InterviewSession(BaseModel):
    model_config = ConfigDict(frozen=True)

    v: int = SCHEMA_VERSION
    queue: tuple[str, ...]
    current_index: int = 0
    queue_mode: QueueMode
    requested_length: int | None
    difficulty: Difficulty | None = None
    started_at: str
    outcomes: dict[str, InterviewOutcome] = Field(default_factory=dict)
    status: InterviewSessionStatus = "active"

    @property
    def is_active(self) -> bool:
        return self.status == "active"

    @property
    def queue_length(self) -> int:
        return len(self.queue)

    def current_exercise_id(self) -> str | None:
        if not self.is_active or self.current_index >= len(self.queue):
            return None
        return self.queue[self.current_index]

    def has_outcome_for_current(self) -> bool:
        exercise_id = self.current_exercise_id()
        return exercise_id is not None and exercise_id in self.outcomes

    def is_last_question(self) -> bool:
        if not self.queue:
            return True
        return self.current_index >= len(self.queue) - 1


class InterviewSummaryItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    exercise_id: str
    title: str
    dataset_id: str
    passed: bool | None
    elapsed_seconds: int | None
    elapsed_label: str | None


class InterviewSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: tuple[InterviewSummaryItem, ...]
    passed_count: int
    queue_length: int
    total_elapsed_seconds: int
    total_elapsed_label: str
    status: InterviewSessionStatus


def _lookup_exercise(exercise_id: str) -> Exercise | None:
    for exercise in TIMES_ARCHIVE_CATALOG.exercises:
        if exercise.id == exercise_id:
            return exercise
    return None


def _format_elapsed(seconds: int) -> str:
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes}:{remainder:02d}"


def load_interview_session(request: Request) -> InterviewSession | None:
    payload = request.session.get(SESSION_KEY)
    if not isinstance(payload, dict):
        return None
    try:
        return InterviewSession.model_validate(payload)
    except ValueError:
        return None


def save_interview_session(request: Request, session: InterviewSession) -> None:
    request.session[SESSION_KEY] = session.model_dump()


def clear_interview_session(request: Request) -> None:
    request.session.pop(SESSION_KEY, None)


def create_interview_session(
    *,
    requested_length: int | None,
    difficulty: Difficulty | None = None,
) -> InterviewSession | None:
    queue_exercises = build_interview_queue(requested_length, difficulty)
    if not queue_exercises:
        return None
    queue_mode: QueueMode = "unlimited" if requested_length is None else "fixed"
    return InterviewSession(
        queue=tuple(exercise.id for exercise in queue_exercises),
        queue_mode=queue_mode,
        requested_length=requested_length,
        difficulty=difficulty,
        started_at=datetime.now(UTC).replace(microsecond=0).isoformat(),
    )


def record_outcome(
    request: Request,
    exercise_id: str,
    *,
    passed: bool,
    elapsed_seconds: int | None = None,
) -> InterviewSession | None:
    session = load_interview_session(request)
    if session is None:
        return None
    updated_outcomes = dict(session.outcomes)
    updated_outcomes[exercise_id] = InterviewOutcome(
        passed=passed,
        elapsed_seconds=elapsed_seconds,
    )
    updated = session.model_copy(update={"outcomes": updated_outcomes})
    save_interview_session(request, updated)
    return updated


def current_exercise(session: InterviewSession | None) -> Exercise | None:
    if session is None:
        return None
    exercise_id = session.current_exercise_id()
    if exercise_id is None:
        return None
    return _lookup_exercise(exercise_id)


def current_exercise_url(session: InterviewSession | None) -> str | None:
    exercise = current_exercise(session)
    if exercise is None:
        return None
    return f"/practice/interview/{exercise.dataset_id}/{exercise.id}"


def advance(session: InterviewSession) -> InterviewSession:
    next_index = min(session.current_index + 1, len(session.queue))
    status: InterviewSessionStatus = session.status
    if next_index >= len(session.queue) and status == "active":
        status = "completed"
    return session.model_copy(update={"current_index": next_index, "status": status})


def end_session_early(session: InterviewSession) -> InterviewSession:
    return session.model_copy(update={"status": "ended_early"})


def interview_resume_context(request: Request) -> dict[str, str | None]:
    session = load_interview_session(request)
    if session is None or not session.is_active:
        return {"resume_interview_url": None, "resume_interview_label": None}
    resume_url = current_exercise_url(session)
    if resume_url is None:
        return {"resume_interview_url": None, "resume_interview_label": None}
    question_number = session.current_index + 1
    return {
        "resume_interview_url": resume_url,
        "resume_interview_label": f"Resume interview (question {question_number})",
    }


def build_summary(session: InterviewSession) -> InterviewSummary:
    items: list[InterviewSummaryItem] = []
    total_elapsed = 0
    passed_count = 0
    for exercise_id in session.queue:
        exercise = _lookup_exercise(exercise_id)
        outcome = session.outcomes.get(exercise_id)
        elapsed = outcome.elapsed_seconds if outcome is not None else None
        passed = outcome.passed if outcome is not None else None
        if passed is True:
            passed_count += 1
        if elapsed is not None:
            total_elapsed += elapsed
        items.append(
            InterviewSummaryItem(
                exercise_id=exercise_id,
                title=exercise.title if exercise is not None else exercise_id,
                dataset_id=exercise.dataset_id if exercise is not None else "",
                passed=passed,
                elapsed_seconds=elapsed,
                elapsed_label=_format_elapsed(elapsed) if elapsed is not None else None,
            )
        )
    return InterviewSummary(
        items=tuple(items),
        passed_count=passed_count,
        queue_length=len(session.queue),
        total_elapsed_seconds=total_elapsed,
        total_elapsed_label=_format_elapsed(total_elapsed),
        status=session.status,
    )
