from app.domain.exercises import ExpectedGrid
from app.domain.grading import GradingOutcome
from app.execution.models import QueryResult


def _format_failure(summary: str) -> GradingOutcome:
    return GradingOutcome(passed=False, summary=summary)


def _expected_columns_label(columns: tuple[str, ...]) -> str:
    return ", ".join(columns)


def grade(result: QueryResult, expected_grid: ExpectedGrid) -> GradingOutcome:
    expected_columns = _expected_columns_label(expected_grid.columns)
    if result.columns != expected_grid.columns:
        if set(result.columns) == set(expected_grid.columns):
            return _format_failure(
                f"Column order does not match. Expected order: {expected_columns}."
            )
        return _format_failure(
            f"Column names do not match. Expected columns (in order): {expected_columns}."
        )

    expected_rows = len(expected_grid.rows)
    if result.row_count != expected_rows:
        row_label = "row" if expected_rows == 1 else "rows"
        return _format_failure(
            f"Row count does not match. Expected {expected_rows} {row_label}."
        )

    for actual_row, expected_row in zip(result.rows, expected_grid.rows, strict=True):
        if len(actual_row) != len(expected_row):
            return _format_failure("Row shape does not match the expected result.")
        for actual_cell, expected_cell in zip(actual_row, expected_row, strict=True):
            if actual_cell != expected_cell:
                return _format_failure(
                    "One or more cell values do not match the expected result."
                )

    if result.truncated:
        return GradingOutcome(
            passed=False,
            summary=(
                "Your result was truncated to 500 rows. "
                "Try narrowing the query so the full result fits."
            ),
        )

    return GradingOutcome(passed=True, summary="Your result exactly matches the expected answer.")
