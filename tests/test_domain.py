import pytest
from pydantic import ValidationError

from app.domain.attempts import DEMO_ATTEMPT, Attempt
from app.domain.datasets import TIMES_ARCHIVE_DEMO_DATASET, Dataset
from app.domain.exercises import TIMES_ARCHIVE_PLACEHOLDER_EXERCISE, Exercise
from app.domain.grading import GRADING_PLACEHOLDER, GradingResult
from app.domain.progress import DEMO_PROGRESS, ProgressSummary


def test_domain_models_are_pydantic_models() -> None:
    for model in [Dataset, Exercise, Attempt, GradingResult, ProgressSummary]:
        assert hasattr(model, "model_validate")


def test_times_dataset_records_demo_provenance() -> None:
    dataset = TIMES_ARCHIVE_DEMO_DATASET

    assert dataset.name == "Times Archive demo"
    assert dataset.is_demo is True
    assert dataset.provenance.source_url == "https://github.com/mikael-lh/times-api"
    assert dataset.provenance.schema_reference == "times-api/schema/archive_articles.json"
    assert "not final production Times data" in dataset.provenance.note


def test_exercise_boundary_names_postgresql_without_execution() -> None:
    exercise = TIMES_ARCHIVE_PLACEHOLDER_EXERCISE

    assert exercise.dataset_id == TIMES_ARCHIVE_DEMO_DATASET.id
    assert exercise.target_dialect == "PostgreSQL"
    assert exercise.is_placeholder is True
    assert "SELECT section_name" in exercise.sample_sql


def test_attempt_grading_and_progress_stay_demo_only() -> None:
    assert DEMO_ATTEMPT.status == "not_started"
    assert DEMO_ATTEMPT.submitted_sql == ""
    assert GRADING_PLACEHOLDER.status == "not_available"
    assert GRADING_PLACEHOLDER.is_placeholder is True
    assert DEMO_PROGRESS.is_demo is True
    assert DEMO_PROGRESS.is_persisted is False


def test_domain_models_validate_input_and_are_immutable() -> None:
    with pytest.raises(ValidationError):
        Exercise.model_validate(
            {
                **TIMES_ARCHIVE_PLACEHOLDER_EXERCISE.model_dump(),
                "target_dialect": "SQLite",
            }
        )

    with pytest.raises(ValidationError):
        setattr(TIMES_ARCHIVE_DEMO_DATASET, "name", "Different name")
