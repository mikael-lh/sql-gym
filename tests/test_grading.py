import json
from pathlib import Path

from app.domain.exercises import ExpectedGrid
from app.domain.grading import GradingOutcome
from app.execution.models import QueryResult
from app.grading import grade


def _grid(
    columns: tuple[str, ...],
    rows: tuple[tuple[object, ...], ...],
) -> ExpectedGrid:
    return ExpectedGrid(columns=columns, rows=rows)


def _result(
    columns: tuple[str, ...],
    rows: tuple[tuple[object, ...], ...],
    *,
    truncated: bool = False,
) -> QueryResult:
    return QueryResult(
        columns=columns,
        rows=rows,
        row_count=len(rows),
        truncated=truncated,
    )


def test_grade_passes_exact_match() -> None:
    expected = _grid(("section_name", "article_count"), (("Arts", 10), ("Sports", 5)))
    actual = _result(("section_name", "article_count"), (("Arts", 10), ("Sports", 5)))

    outcome = grade(actual, expected)

    assert outcome == GradingOutcome(
        passed=True,
        summary="Your result exactly matches the expected answer.",
    )


def test_grade_fails_wrong_cell_value() -> None:
    expected = _grid(("n",), ((1,),))
    actual = _result(("n",), ((2,),))

    outcome = grade(actual, expected)

    assert outcome.passed is False
    assert "do not match" in outcome.summary


def test_grade_fails_wrong_row_count() -> None:
    expected = _grid(("n",), ((1,), (2,)))
    actual = _result(("n",), ((1,),))

    outcome = grade(actual, expected)

    assert outcome.passed is False
    assert "Expected 2 rows" in outcome.summary


def test_grade_fails_wrong_column_order() -> None:
    expected = _grid(("a", "b"), ((1, 2),))
    actual = _result(("b", "a"), ((2, 1),))

    outcome = grade(actual, expected)

    assert outcome.passed is False
    assert "Expected order: a, b" in outcome.summary


def test_grade_fails_wrong_column_names() -> None:
    expected = _grid(("a",), ((1,),))
    actual = _result(("b",), ((1,),))

    outcome = grade(actual, expected)

    assert outcome.passed is False
    assert "Expected columns (in order): a" in outcome.summary


def test_grade_compares_null_vs_empty_string() -> None:
    expected = _grid(("value",), ((None,),))
    actual = _result(("value",), (("",),))

    outcome = grade(actual, expected)

    assert outcome.passed is False


def test_grade_passes_null_cells() -> None:
    expected = _grid(("value",), ((None,),))
    actual = _result(("value",), ((None,),))

    outcome = grade(actual, expected)

    assert outcome.passed is True


def test_grade_fails_when_result_truncated() -> None:
    expected = _grid(("n",), ((1,),))
    actual = _result(("n",), ((1,),), truncated=True)

    outcome = grade(actual, expected)

    assert outcome.passed is False
    assert "truncated" in outcome.summary.lower()


def test_grade_multiset_passes_reordered_rows() -> None:
    expected = _grid(("section_name", "article_count"), (("Arts", 10), ("Sports", 5)))
    actual = _result(("section_name", "article_count"), (("Sports", 5), ("Arts", 10)))

    outcome = grade(actual, expected, row_order="multiset")

    assert outcome.passed is True


def test_grade_multiset_fails_wrong_row_values() -> None:
    expected = _grid(("section_name", "article_count"), (("Arts", 10), ("Sports", 5)))
    actual = _result(("section_name", "article_count"), (("Arts", 11), ("Sports", 5)))

    outcome = grade(actual, expected, row_order="multiset")

    assert outcome.passed is False
    assert "row order is ignored" in outcome.summary


def test_grade_strict_fails_reordered_rows() -> None:
    expected = _grid(("section_name", "article_count"), (("Arts", 10), ("Sports", 5)))
    actual = _result(("section_name", "article_count"), (("Sports", 5), ("Arts", 10)))

    outcome = grade(actual, expected, row_order="strict")

    assert outcome.passed is False
    assert "cell values" in outcome.summary


def test_grade_multiset_passes_exercise_005_tied_row_reorder() -> None:
    grid_path = Path("src/app/catalog/data/expected_grids/times-archive-005.json")
    payload = json.loads(grid_path.read_text())
    rows = [tuple(row) for row in payload["rows"]]
    tied_index = next(
        index
        for index in range(len(rows) - 1)
        if rows[index][1] == rows[index + 1][1]
    )
    reordered = rows[:]
    reordered[tied_index], reordered[tied_index + 1] = (
        reordered[tied_index + 1],
        reordered[tied_index],
    )

    expected = ExpectedGrid(
        columns=tuple(payload["columns"]),
        rows=tuple(rows),
    )
    actual = _result(expected.columns, tuple(reordered))

    outcome = grade(actual, expected, row_order="multiset")

    assert outcome.passed is True
