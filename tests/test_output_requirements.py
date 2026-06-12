from app.catalog import TIMES_ARCHIVE_CATALOG
from app.catalog.output_requirements import build_output_requirements_text
from app.practice import lookup_exercise


def test_output_requirements_lists_columns_in_order() -> None:
    exercise = lookup_exercise("times-archive", "times-archive-001")
    assert exercise is not None
    text = build_output_requirements_text(exercise)

    assert "`headline_main`, `pub_date`" in text
    assert "in this order" in text
    assert "pub_date DESC" in text
    assert "at most 500 row(s)" in text
    assert "not your SQL wording" in text


def test_output_requirements_for_scalar_count() -> None:
    exercise = lookup_exercise("times-archive", "times-archive-011")
    assert exercise is not None
    text = build_output_requirements_text(exercise)

    assert "`january_articles`" in text
    assert "Order rows by" not in text


def test_all_catalog_exercises_have_output_requirements() -> None:
    for exercise in TIMES_ARCHIVE_CATALOG.exercises:
        text = build_output_requirements_text(exercise)
        assert exercise.expected_result.column_names
        assert all(f"`{name}`" in text for name in exercise.expected_result.column_names)
