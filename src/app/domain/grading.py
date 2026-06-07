from typing import Literal

from pydantic import BaseModel, ConfigDict

GradingStatus = Literal["not_available", "pending", "graded"]


class GradingResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    exercise_id: str
    status: GradingStatus
    summary: str
    is_placeholder: bool = True


GRADING_PLACEHOLDER = GradingResult(
    exercise_id="times-archive-section-count",
    status="not_available",
    summary="Exact-result and AI-assisted grading remain future work.",
)
