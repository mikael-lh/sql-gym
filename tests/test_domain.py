import pytest
from pydantic import ValidationError

from app.catalog import TIMES_ARCHIVE_CATALOG, load_times_exercises
from app.domain.attempts import DEMO_ATTEMPT, Attempt
from app.domain.catalog import Catalog, build_catalog
from app.domain.datasets import (
    TIMES_ARCHIVE_CATALOG_DATASET,
    TIMES_ARCHIVE_DEMO_DATASET,
    Dataset,
)
from app.domain.exercises import TIMES_ARCHIVE_PLACEHOLDER_EXERCISE, Exercise
from app.domain.grading import GRADING_PLACEHOLDER, GradingResult
from app.domain.progress import DEMO_PROGRESS, ProgressSummary


def test_domain_models_are_pydantic_models() -> None:
    for model in [Dataset, Exercise, Attempt, GradingResult, ProgressSummary, Catalog]:
        assert hasattr(model, "model_validate")


def test_times_dataset_records_demo_provenance() -> None:
    dataset = TIMES_ARCHIVE_DEMO_DATASET

    assert dataset.name == "Times Archive demo"
    assert dataset.is_demo is True
    assert dataset.provenance.source_url == "https://github.com/mikael-lh/times-api"
    assert dataset.provenance.schema_reference == "times-api/schema/archive_articles.json"
    assert "not final production Times data" in dataset.provenance.note


def test_times_catalog_dataset_is_production_ready() -> None:
    dataset = TIMES_ARCHIVE_CATALOG_DATASET

    assert dataset.id == "times-archive"
    assert dataset.is_demo is False
    assert dataset.provenance.source_name == "times-api"
    assert "docs/times-data-setup.md" in dataset.provenance.note
    assert "import-times-from-times-api.sh" in dataset.provenance.note


def test_exercise_metadata_supports_catalog_fields() -> None:
    exercise = TIMES_ARCHIVE_PLACEHOLDER_EXERCISE

    assert exercise.dataset_id == TIMES_ARCHIVE_DEMO_DATASET.id
    assert exercise.target_dialect == "PostgreSQL"
    assert exercise.availability_status == "placeholder"
    assert exercise.concept_tags == ("aggregation", "group-by")
    assert exercise.estimated_time_minutes == 10
    assert exercise.learning_objectives
    assert exercise.hint
    assert "SELECT section_name" in exercise.sample_sql
    assert exercise.expected_result.column_names == ("section_name", "article_count")


def test_catalog_rejects_exercises_with_unknown_dataset() -> None:
    orphan_exercise = Exercise(
        id="orphan-exercise",
        dataset_id="missing-dataset",
        title="Orphan exercise",
        prompt="This exercise references a dataset that is not in the catalog.",
        difficulty="Intermediate",
        target_dialect="PostgreSQL",
        concept_tags=("filtering",),
        estimated_time_minutes=5,
        learning_objectives=("Validate catalog references.",),
        hint="This should fail validation.",
        sample_sql="SELECT 1;",
    )

    with pytest.raises(ValueError, match="unknown dataset"):
        build_catalog([TIMES_ARCHIVE_CATALOG_DATASET], [orphan_exercise])


def test_catalog_accepts_valid_dataset_and_exercise_pairs() -> None:
    catalog = build_catalog(
        [TIMES_ARCHIVE_CATALOG_DATASET],
        [
            Exercise(
                id="times-archive-valid",
                dataset_id=TIMES_ARCHIVE_CATALOG_DATASET.id,
                title="Valid catalog exercise",
                prompt="Count rows in the Times Archive catalog.",
                difficulty="Intermediate",
                target_dialect="PostgreSQL",
                concept_tags=("counting",),
                estimated_time_minutes=8,
                learning_objectives=("Count rows in a table.",),
                hint="Use COUNT(*).",
                sample_sql="SELECT COUNT(*) FROM times_archive;",
            )
        ],
    )

    assert len(catalog.datasets) == 1
    assert len(catalog.exercises) == 1


def test_times_archive_catalog_has_sixty_exercises() -> None:
    exercises = load_times_exercises()

    assert len(exercises) == 60
    assert len({exercise.id for exercise in exercises}) == 60
    assert len({exercise.prompt for exercise in exercises}) == 60


def test_times_archive_catalog_entries_include_required_metadata() -> None:
    for exercise in load_times_exercises():
        assert exercise.dataset_id == TIMES_ARCHIVE_CATALOG_DATASET.id
        assert exercise.target_dialect == "PostgreSQL"
        assert exercise.concept_tags
        assert exercise.estimated_time_minutes > 0
        assert exercise.learning_objectives
        assert exercise.hint
        assert exercise.sample_sql
        assert exercise.expected_result.reference_sql
        assert exercise.expected_result.expected_grid is not None
        assert exercise.availability_status in {"available", "placeholder", "coming_soon"}
        assert exercise.hint != exercise.sample_sql


def test_times_archive_catalog_is_consistent() -> None:
    catalog = TIMES_ARCHIVE_CATALOG

    assert len(catalog.datasets) == 1
    assert catalog.datasets[0].id == TIMES_ARCHIVE_CATALOG_DATASET.id
    assert len(catalog.exercises) == 60


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
        Exercise.model_validate(
            {
                **TIMES_ARCHIVE_PLACEHOLDER_EXERCISE.model_dump(),
                "difficulty": "Expert",
            }
        )

    with pytest.raises(ValidationError):
        Exercise.model_validate(
            {
                **TIMES_ARCHIVE_PLACEHOLDER_EXERCISE.model_dump(),
                "estimated_time_minutes": 0,
            }
        )

    with pytest.raises(ValidationError):
        setattr(TIMES_ARCHIVE_DEMO_DATASET, "name", "Different name")
