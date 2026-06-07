from typing import TypedDict


class SelectionOption(TypedDict):
    label: str
    description: str


class PlaceholderCard(TypedDict):
    title: str
    description: str


class ProgressMetric(TypedDict):
    label: str
    value: str


DATASET = {
    "name": "Times Archive demo",
    "source": "times-api",
    "source_url": "https://github.com/mikael-lh/times-api",
    "schema_reference": "times-api/schema/archive_articles.json",
    "fixture_path": "src/app/fixtures/times/archive_articles_demo.json",
    "note": "Schema-aligned demo rows only; not final production Times data.",
}

DIFFICULTIES: list[SelectionOption] = [
    {
        "label": "Beginner",
        "description": "Start with filtering, sorting, and simple aggregations.",
    },
    {
        "label": "Intermediate",
        "description": "Practice grouping, joins, date logic, and CTEs.",
    },
    {
        "label": "Advanced",
        "description": "Reserved for window functions and deeper analytics prompts.",
    },
]

MODES: list[SelectionOption] = [
    {
        "label": "Untimed",
        "description": "Practice mode for careful exploration.",
    },
    {
        "label": "Timed",
        "description": "Interview-style mode reserved for a later milestone.",
    },
]

PLACEHOLDER_AREAS: list[PlaceholderCard] = [
    {
        "title": "SQL editor",
        "description": "A disabled PostgreSQL-targeted editor placeholder; queries do not run yet.",
    },
    {
        "title": "Grading feedback",
        "description": "Reserved for exact-result and AI-assisted feedback in later phases.",
    },
    {
        "title": "Progress tracking",
        "description": "Static demo-only progress; no accounts or persistence are active.",
    },
]

PROGRESS: list[ProgressMetric] = [
    {"label": "Completed exercises", "value": "0 demo"},
    {"label": "Current streak", "value": "0 demo"},
    {"label": "Skill progress", "value": "Demo only"},
]

SAMPLE_SQL = """-- PostgreSQL target dialect
SELECT section_name, COUNT(*) AS article_count
FROM times_archive_demo
GROUP BY section_name
ORDER BY article_count DESC;"""


def get_practice_context() -> dict[str, object]:
    return {
        "page_title": "Practice - SQL Gym",
        "status_label": "Practice placeholders",
        "dataset": DATASET,
        "difficulties": DIFFICULTIES,
        "modes": MODES,
        "placeholder_areas": PLACEHOLDER_AREAS,
        "progress": PROGRESS,
        "sample_sql": SAMPLE_SQL,
    }
