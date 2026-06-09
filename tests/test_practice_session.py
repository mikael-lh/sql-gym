from app.execution.models import QueryResult
from app.practice_session import SESSION_PREVIEW_ROW_LIMIT, _serialize_query_result


def test_serialize_query_result_caps_preview_rows() -> None:
    rows = tuple((index,) for index in range(100))
    result = QueryResult(columns=("n",), rows=rows, row_count=100, truncated=False)
    payload = _serialize_query_result(result)
    assert len(payload["rows"]) == SESSION_PREVIEW_ROW_LIMIT
    assert payload["row_count"] == 100
    assert payload["truncated"] is True


def test_serialize_query_result_preserves_small_results() -> None:
    rows = ((1,), (2,))
    result = QueryResult(columns=("n",), rows=rows, row_count=2, truncated=False)
    payload = _serialize_query_result(result)
    assert payload["rows"] == [[1], [2]]
    assert payload["row_count"] == 2
    assert payload["truncated"] is False


def test_serialize_query_result_keeps_execution_truncated_flag() -> None:
    rows = tuple((index,) for index in range(SESSION_PREVIEW_ROW_LIMIT))
    result = QueryResult(
        columns=("n",),
        rows=rows,
        row_count=500,
        truncated=True,
    )
    payload = _serialize_query_result(result)
    assert len(payload["rows"]) == SESSION_PREVIEW_ROW_LIMIT
    assert payload["row_count"] == 500
    assert payload["truncated"] is True
