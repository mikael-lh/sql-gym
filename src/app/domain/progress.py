from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

ExerciseProgressStatus = Literal["not_started", "attempted", "passed"]


class ExerciseProgress(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: Literal["attempted", "passed"]
    passed_at: str | None = None
    elapsed_seconds: int | None = None


class ProgressStore(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: int = 1
    exercises: dict[str, ExerciseProgress] = Field(default_factory=dict)

    def get_status(self, exercise_id: str) -> ExerciseProgressStatus:
        record = self.exercises.get(exercise_id)
        if record is None:
            return "not_started"
        return record.status

    def passed_count(self) -> int:
        return sum(1 for record in self.exercises.values() if record.status == "passed")

    def apply_submit_outcome(
        self,
        exercise_id: str,
        *,
        passed: bool,
        elapsed_seconds: int | None = None,
    ) -> ProgressStore:
        current = self.exercises.get(exercise_id)
        if passed:
            if current is not None and current.status == "passed":
                passed_at = current.passed_at
                stored_elapsed = current.elapsed_seconds
            else:
                passed_at = datetime.now(UTC).replace(microsecond=0).isoformat()
                stored_elapsed = elapsed_seconds
            updated = dict(self.exercises)
            updated[exercise_id] = ExerciseProgress(
                status="passed",
                passed_at=passed_at,
                elapsed_seconds=stored_elapsed,
            )
            return self.model_copy(update={"exercises": updated})

        if current is not None and current.status == "passed":
            return self

        updated = dict(self.exercises)
        updated[exercise_id] = ExerciseProgress(status="attempted")
        return self.model_copy(update={"exercises": updated})


class ProgressMetric(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    value: str


class ProgressSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_label: str
    metrics: tuple[ProgressMetric, ...]
    is_demo: bool = False
    is_persisted: bool = True


def build_progress_summary(store: ProgressStore, total_exercises: int) -> ProgressSummary:
    passed = store.passed_count()
    return ProgressSummary(
        user_label="Your progress",
        metrics=(
            ProgressMetric(label="Completed exercises", value=f"{passed} / {total_exercises}"),
        ),
        is_demo=False,
        is_persisted=True,
    )


DEMO_PROGRESS = ProgressSummary(
    user_label="Demo learner",
    metrics=(
        ProgressMetric(label="Completed exercises", value="0 demo"),
        ProgressMetric(label="Current streak", value="0 demo"),
        ProgressMetric(label="Skill progress", value="Demo only"),
    ),
    is_demo=True,
    is_persisted=False,
)
