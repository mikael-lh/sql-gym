from app.catalog import TIMES_ARCHIVE_CATALOG
from app.catalog.output_requirements import build_output_requirements_text
from app.practice import lookup_exercise


def test_output_requirements_lists_columns_in_order() -> None:
    exercise = lookup_exercise("times-archive", "times-archive-018")
    assert exercise is not None
    text = build_output_requirements_text(exercise)

    assert "`headline_main`, `section_name`, `news_desk`" in text
    assert "in this order" in text
    assert "row order does not matter" in text
    assert "Order rows by" not in text
    assert "at most 500 row(s)" in text
    assert "not your SQL wording" in text


def test_output_requirements_multiset_omits_sort_copy() -> None:
    exercise = lookup_exercise("times-archive", "times-archive-013")
    assert exercise is not None
    text = build_output_requirements_text(exercise)

    assert "Order rows by" not in text
    assert "row order does not matter" in text


def test_output_requirements_for_scalar_count() -> None:
    exercise = lookup_exercise("times-archive", "times-archive-011")
    assert exercise is not None
    text = build_output_requirements_text(exercise)

    assert "`january_articles`" in text
    assert "Order rows by" not in text


def test_catalog_grading_row_order_defaults_to_multiset() -> None:
    by_id = {exercise.id: exercise for exercise in TIMES_ARCHIVE_CATALOG.exercises}
    assert by_id["times-archive-019"].expected_result.grading_row_order == "multiset"
    assert by_id["times-archive-011"].expected_result.grading_row_order == "multiset"
    assert all(
        exercise.expected_result.grading_row_order == "multiset"
        for exercise in TIMES_ARCHIVE_CATALOG.exercises
    )


def test_all_catalog_exercises_have_output_requirements() -> None:
    for exercise in TIMES_ARCHIVE_CATALOG.exercises:
        text = build_output_requirements_text(exercise)
        assert exercise.expected_result.column_names
        assert all(f"`{name}`" in text for name in exercise.expected_result.column_names)
