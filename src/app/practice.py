from app.domain.attempts import DEMO_ATTEMPT
from app.domain.datasets import TIMES_ARCHIVE_DEMO_DATASET
from app.domain.exercises import (
    DIFFICULTY_OPTIONS,
    MODE_OPTIONS,
    TIMES_ARCHIVE_PLACEHOLDER_EXERCISE,
)
from app.domain.grading import GRADING_PLACEHOLDER
from app.domain.progress import DEMO_PROGRESS

PLACEHOLDER_AREAS = (
    {
        "title": "SQL editor",
        "description": "A disabled PostgreSQL-targeted editor placeholder; queries do not run yet.",
    },
    {
        "title": "Grading feedback",
        "description": GRADING_PLACEHOLDER.summary,
    },
    {
        "title": "Progress tracking",
        "description": "Static demo-only progress; no accounts or persistence are active.",
    },
)


def get_practice_context() -> dict[str, object]:
    dataset = TIMES_ARCHIVE_DEMO_DATASET
    exercise = TIMES_ARCHIVE_PLACEHOLDER_EXERCISE

    return {
        "page_title": "Practice - SQL Gym",
        "status_label": "Practice placeholders",
        "dataset": {
            "name": dataset.name,
            "source": dataset.provenance.source_name,
            "source_url": dataset.provenance.source_url,
            "schema_reference": dataset.provenance.schema_reference,
            "fixture_path": dataset.provenance.fixture_path,
            "note": dataset.provenance.note,
        },
        "difficulties": DIFFICULTY_OPTIONS,
        "modes": MODE_OPTIONS,
        "placeholder_areas": PLACEHOLDER_AREAS,
        "progress": DEMO_PROGRESS.metrics,
        "sample_sql": exercise.sample_sql,
        "attempt": DEMO_ATTEMPT,
        "grading": GRADING_PLACEHOLDER,
    }
