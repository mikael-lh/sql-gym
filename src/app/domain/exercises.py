from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Difficulty = Literal["Intermediate", "Advanced"]
SqlDialect = Literal["PostgreSQL"]
AvailabilityStatus = Literal["available", "placeholder", "coming_soon"]
GradingRowOrder = Literal["strict", "multiset"]


class SelectionOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    description: str


class ExpectedGrid(BaseModel):
    model_config = ConfigDict(frozen=True)

    columns: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]


class ExpectedResultSpec(BaseModel):
    model_config = ConfigDict(frozen=True)

    description: str | None = None
    column_names: tuple[str, ...] = ()
    reference_sql: str | None = None
    expected_grid: ExpectedGrid | None = None
    grading_row_order: GradingRowOrder = "multiset"


class Exercise(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    dataset_id: str
    title: str
    prompt: str
    difficulty: Difficulty
    target_dialect: SqlDialect
    concept_tags: tuple[str, ...]
    estimated_time_minutes: int = Field(gt=0)
    learning_objectives: tuple[str, ...]
    hint: str
    sample_sql: str
    availability_status: AvailabilityStatus = "placeholder"
    expected_result: ExpectedResultSpec = Field(default_factory=ExpectedResultSpec)


DIFFICULTY_OPTIONS: tuple[SelectionOption, ...] = (
    SelectionOption(
        label="Intermediate",
        description="Practice grouping, joins, date logic, and CTEs.",
    ),
    SelectionOption(
        label="Advanced",
        description="Window functions, analytics, and deeper SQL patterns.",
    ),
)
