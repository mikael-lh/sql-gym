from typing import Literal

from pydantic import BaseModel, ConfigDict

Difficulty = Literal["Beginner", "Intermediate", "Advanced"]
PracticeMode = Literal["Untimed", "Timed"]
SqlDialect = Literal["PostgreSQL"]


class SelectionOption(BaseModel):
    model_config = ConfigDict(frozen=True)

    label: str
    description: str


class Exercise(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    dataset_id: str
    title: str
    prompt: str
    difficulty: Difficulty
    mode: PracticeMode
    target_dialect: SqlDialect
    sample_sql: str
    is_placeholder: bool = True


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
    sample_sql="""-- PostgreSQL target dialect
SELECT section_name, COUNT(*) AS article_count
FROM times_archive_demo
GROUP BY section_name
ORDER BY article_count DESC;""",
)
