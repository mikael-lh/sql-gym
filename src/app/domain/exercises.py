from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Difficulty = Literal["Beginner", "Intermediate", "Advanced"]
PracticeMode = Literal["Untimed", "Timed"]
SqlDialect = Literal["PostgreSQL"]
AvailabilityStatus = Literal["available", "placeholder", "coming_soon"]


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


class Exercise(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    dataset_id: str
    title: str
    prompt: str
    difficulty: Difficulty
    mode: PracticeMode
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
        label="Beginner",
        description="Start with filtering, sorting, and simple aggregations.",
    ),
    SelectionOption(
        label="Intermediate",
        description="Practice grouping, joins, date logic, and CTEs.",
    ),
    SelectionOption(
        label="Advanced",
        description="Reserved for window functions and deeper analytics prompts.",
    ),
)

MODE_OPTIONS: tuple[SelectionOption, ...] = (
    SelectionOption(
        label="Untimed",
        description="Practice mode for careful exploration.",
    ),
    SelectionOption(
        label="Timed",
        description="Interview-style mode reserved for a later milestone.",
    ),
)

TIMES_ARCHIVE_PLACEHOLDER_EXERCISE = Exercise(
    id="times-archive-section-count",
    dataset_id="times-archive-demo",
    title="Count articles by section",
    prompt="Explore how many demo articles appear in each Times section.",
    difficulty="Beginner",
    mode="Untimed",
    target_dialect="PostgreSQL",
    concept_tags=("aggregation", "group-by"),
    estimated_time_minutes=10,
    learning_objectives=("Group rows by a categorical column.", "Count rows per group."),
    hint="Try grouping by section_name and counting rows.",
    sample_sql="""-- PostgreSQL target dialect
SELECT section_name, COUNT(*) AS article_count
FROM times_archive_demo
GROUP BY section_name
ORDER BY article_count DESC;""",
    expected_result=ExpectedResultSpec(
        description="One row per section with article counts.",
        column_names=("section_name", "article_count"),
    ),
)
