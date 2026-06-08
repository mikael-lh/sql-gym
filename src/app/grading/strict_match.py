from app.domain.exercises import ExpectedGrid
from app.domain.grading import GradingOutcome
from app.execution.models import QueryResult


def _format_failure(summary: str) -> GradingOutcome:
    return GradingOutcome(passed=False, summary=summary)


def grade(result: QueryResult, expected_grid: ExpectedGrid) -> GradingOutcome:
    if result.columns != expected_grid.columns:
        if set(result.columns) == set(expected_grid.columns):
            return _format_failure("Column order does not match the expected result.")
        return _format_failure("Column names do not match the expected result.")

    if result.row_count != len(expected_grid.rows):
        return _format_failure("Row count does not match the expected result.")

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
