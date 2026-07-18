from app.api.serializers import serialize_query_result
from app.execution.models import QueryResult
from app.practice_session import (
    SESSION_PREVIEW_ROW_LIMIT,
    get_attempt_state,
    slim_practice_attempts,
    store_run_result,
)


class _FakeSession(dict):
    pass


class _FakeRequest:
    def __init__(self) -> None:
        self.session: _FakeSession = _FakeSession()


def test_session_preview_uses_row_limit() -> None:
    rows = tuple((index,) for index in range(100))
    result = QueryResult(columns=("n",), rows=rows, row_count=100, truncated=False)
    payload = serialize_query_result(result, row_limit=SESSION_PREVIEW_ROW_LIMIT)
    assert len(payload["rows"]) == SESSION_PREVIEW_ROW_LIMIT
    assert payload["row_count"] == 100
    assert payload["truncated"] is True


def test_slim_practice_attempts_keeps_sql_drops_heavy_fields() -> None:
    request = _FakeRequest()
    request.session["practice_attempts"] = {
        "ex-a": {
            "sql": "SELECT 1",
            "query_result": {"columns": ["n"], "rows": [[1]], "row_count": 1, "truncated": False},
            "execution_error": None,
            "grading": {"passed": True},
            "status": "graded",
        },
        "ex-b": {
            "sql": "SELECT 2",
            "query_result": {"columns": ["n"], "rows": [[2]], "row_count": 1, "truncated": False},
            "status": "draft",
        },
    }

    slim_practice_attempts(request, keep_exercise_id="ex-b")

    kept = request.session["practice_attempts"]["ex-b"]
    slimmed = request.session["practice_attempts"]["ex-a"]
    assert kept["query_result"] is not None
    assert slimmed["sql"] == "SELECT 1"
    assert slimmed["query_result"] is None
    assert slimmed["grading"] is None


def test_store_run_result_slims_other_exercises() -> None:
    request = _FakeRequest()
    request.session["practice_attempts"] = {
        "ex-a": {
            "sql": "SELECT 1",
            "query_result": {"columns": ["n"], "rows": [[1]], "row_count": 1, "truncated": False},
            "status": "draft",
        }
    }
    rows = ((1,),)
    outcome = QueryResult(columns=("n",), rows=rows, row_count=1, truncated=False)
    store_run_result(request, "ex-b", "SELECT 2", outcome)

    assert get_attempt_state(request, "ex-a")["query_result"] is None
    assert get_attempt_state(request, "ex-b")["query_result"] is not None


def test_store_run_result_caps_preview_rows() -> None:
    request = _FakeRequest()
    rows = tuple((index,) for index in range(100))
    outcome = QueryResult(columns=("n",), rows=rows, row_count=100, truncated=False)
    store_run_result(request, "ex-a", "SELECT n", outcome)
    stored = get_attempt_state(request, "ex-a")["query_result"]
    assert stored is not None
    assert len(stored["rows"]) == SESSION_PREVIEW_ROW_LIMIT
    assert stored["truncated"] is True
