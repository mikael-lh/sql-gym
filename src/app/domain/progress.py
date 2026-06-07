from pydantic import BaseModel, ConfigDict


class ProgressMetric(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    value: str


class ProgressSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    user_label: str
    metrics: tuple[ProgressMetric, ...]
    is_demo: bool = True
    is_persisted: bool = False


DEMO_PROGRESS = ProgressSummary(
    user_label="Demo learner",
    metrics=(
        ProgressMetric(label="Completed exercises", value="0 demo"),
        ProgressMetric(label="Current streak", value="0 demo"),
        ProgressMetric(label="Skill progress", value="Demo only"),
    ),
)
