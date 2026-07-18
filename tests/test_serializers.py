from app.api.serializers import (
    serialize_execution_error,
    serialize_grading,
    serialize_query_result,
)
from app.domain.grading import GradingResult
from app.execution.models import ExecutionError, QueryResult


def test_serialize_query_result_full_rows() -> None:
    result = QueryResult(
        columns=("n",),
        rows=tuple((index,) for index in range(30)),
        row_count=30,
        truncated=False,
    )
    payload = serialize_query_result(result)
    assert len(payload["rows"]) == 30
    assert payload["truncated"] is False


def test_serialize_query_result_respects_row_limit() -> None:
    result = QueryResult(
        columns=("n",),
        rows=tuple((index,) for index in range(30)),
        row_count=30,
        truncated=False,
    )
    payload = serialize_query_result(result, row_limit=25)
    assert len(payload["rows"]) == 25
    assert payload["row_count"] == 30
    assert payload["truncated"] is True


def test_serialize_execution_error_for_run_prefers_postgres_message() -> None:
    error = ExecutionError(
        message="friendly",
        code="execution_error",
        postgres_message="column missing",
    )
    assert serialize_execution_error(error, for_run=True) == {
        "message": "column missing",
        "code": "execution_error",
    }
    assert serialize_execution_error(error) == {
        "message": "friendly",
        "code": "execution_error",
    }


def test_serialize_grading() -> None:
    grading = GradingResult(
        exercise_id="ex-1",
        status="graded",
        summary="ok",
        passed=True,
        is_placeholder=False,
    )
    assert serialize_grading(grading)["passed"] is True
