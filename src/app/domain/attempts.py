from typing import Literal

from pydantic import BaseModel, ConfigDict

AttemptStatus = Literal["not_started", "draft", "submitted"]


class Attempt(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    exercise_id: str
    submitted_sql: str
    status: AttemptStatus
    is_demo: bool = True


DEMO_ATTEMPT = Attempt(
    id="demo-attempt",
    exercise_id="times-archive-section-count",
    submitted_sql="",
    status="not_started",
)
