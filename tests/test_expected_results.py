from app.catalog import TIMES_ARCHIVE_CATALOG, load_times_exercises
from app.domain.datasets import TIMES_ARCHIVE_CATALOG_DATASET


def test_all_exercises_have_reference_sql() -> None:
    for exercise in load_times_exercises():
        assert exercise.expected_result.reference_sql
        assert exercise.expected_result.reference_sql.strip()


def test_all_exercises_have_expected_grids() -> None:
    for exercise in load_times_exercises():
        grid = exercise.expected_result.expected_grid
        assert grid is not None, exercise.id
        assert grid.columns
        assert grid.rows
        assert len(grid.rows) <= 500


def test_expected_grid_columns_match_metadata() -> None:
    for exercise in load_times_exercises():
        grid = exercise.expected_result.expected_grid
        assert grid is not None
        if exercise.expected_result.column_names:
            assert grid.columns == exercise.expected_result.column_names


def test_catalog_loads_with_expected_results() -> None:
    assert len(TIMES_ARCHIVE_CATALOG.exercises) == 50
    assert TIMES_ARCHIVE_CATALOG.datasets[0].id == TIMES_ARCHIVE_CATALOG_DATASET.id
