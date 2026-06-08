from typing import Literal

from pydantic import BaseModel, ConfigDict

GradingStatus = Literal["not_available", "pending", "graded"]


class GradingOutcome(BaseModel):
    model_config = ConfigDict(frozen=True)

    passed: bool
    summary: str
    status: GradingStatus = "graded"


class GradingResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    exercise_id: str
    status: GradingStatus
    summary: str
    passed: bool | None = None
    is_placeholder: bool = False


GRADING_PLACEHOLDER = GradingResult(
    exercise_id="times-archive-section-count",
    status="not_available",
    summary="Exact-result and AI-assisted grading remain future work.",
    is_placeholder=True,
)


def grading_result_from_outcome(exercise_id: str, outcome: GradingOutcome) -> GradingResult:
    return GradingResult(
        exercise_id=exercise_id,
        status=outcome.status,
        summary=outcome.summary,
        passed=outcome.passed,
        is_placeholder=False,
    )
