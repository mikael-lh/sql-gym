import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from app.main import app
from app.progress.cookie import COOKIE_NAME

EXPECTED_GRID = json.loads(
    Path("src/app/catalog/data/expected_grids/times-archive-011.json").read_text()
)


async def _get(path: str, *, cookies: dict[str, str] | None = None) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        cookies=cookies or {},
    ) as client:
        return await client.get(path)


async def _post_json(
    path: str,
    payload: dict[str, object],
    *,
    cookies: dict[str, str] | None = None,
) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        cookies=cookies or {},
    ) as client:
        return await client.post(path, json=payload)


def test_api_list_exercises_returns_filtered_catalog() -> None:
    response = asyncio.run(_get("/api/practice/exercises?difficulty=Advanced"))
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] > 0
    assert all(item["difficulty"] == "Advanced" for item in payload["exercises"])


def test_api_get_exercise_returns_workspace_payload() -> None:
    response = asyncio.run(
        _get("/api/practice/times-archive/times-archive-011")
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["exercise"]["id"] == "times-archive-011"
    assert "reference_sql" in payload["exercise"]
    assert payload["exercise"]["reference_sql"]
    assert "`january_articles`" in payload["exercise"]["output_requirements"]
    assert payload["schema"] is not None
    assert "navigation" in payload
    assert "attempt" in payload


def test_api_get_exercise_not_found() -> None:
    response = asyncio.run(
        _get("/api/practice/times-archive/times-archive-999")
    )
    assert response.status_code == 404


@patch("app.api.practice.execute_query")
def test_api_run_sql_returns_json_result(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=("headline_main",),
        rows=(("Example",),),
        row_count=1,
        truncated=False,
    )
    response = asyncio.run(
        _post_json(
            "/api/practice/times-archive/times-archive-011/run",
            {"sql": "SELECT headline_main FROM times_archive LIMIT 1"},
        )
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["columns"] == ["headline_main"]
    assert payload["rows"] == [["Example"]]


@patch("app.api.practice.execute_query")
def test_api_run_sql_returns_execution_error(mock_execute: MagicMock) -> None:
    from app.execution.models import ExecutionError

    mock_execute.return_value = ExecutionError(
        message="Only SELECT queries are allowed",
        code="validation_error",
    )
    response = asyncio.run(
        _post_json(
            "/api/practice/times-archive/times-archive-011/run",
            {"sql": "DELETE FROM times_archive"},
        )
    )
    assert response.status_code == 422
    assert "error" in response.json()


@patch("app.api.practice.execute_query")
def test_api_run_sql_returns_postgres_error_message(mock_execute: MagicMock) -> None:
    from app.execution.models import ExecutionError

    mock_execute.return_value = ExecutionError(
        message="The query could not be executed. Check your SQL and try again.",
        code="execution_error",
        postgres_message='column "missing_col" does not exist',
    )
    response = asyncio.run(
        _post_json(
            "/api/practice/times-archive/times-archive-011/run",
            {"sql": "SELECT missing_col FROM times_archive"},
        )
    )
    assert response.status_code == 422
    assert response.json()["error"]["message"] == 'column "missing_col" does not exist'


@patch("app.api.practice.execute_query")
def test_api_submit_sql_keeps_friendly_execution_error(mock_execute: MagicMock) -> None:
    from app.execution.models import ExecutionError

    mock_execute.return_value = ExecutionError(
        message="The query could not be executed. Check your SQL and try again.",
        code="execution_error",
        postgres_message='column "missing_col" does not exist',
    )
    response = asyncio.run(
        _post_json(
            "/api/practice/times-archive/times-archive-011/submit",
            {"sql": "SELECT missing_col FROM times_archive"},
        )
    )
    assert response.status_code == 422
    assert (
        response.json()["error"]["message"]
        == "The query could not be executed. Check your SQL and try again."
    )


@patch("app.api.practice.execute_query")
def test_api_submit_sql_sets_progress_cookie(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    rows = tuple(tuple(row) for row in EXPECTED_GRID["rows"])
    mock_execute.return_value = QueryResult(
        columns=tuple(EXPECTED_GRID["columns"]),
        rows=rows,
        row_count=len(rows),
        truncated=False,
    )
    response = asyncio.run(
        _post_json(
            "/api/practice/times-archive/times-archive-011/submit",
            {"sql": "SELECT headline_main, pub_date FROM times_archive LIMIT 1"},
        )
    )
    assert response.status_code == 200
    payload = response.json()
    assert "grading" in payload
    assert payload["progress"]["status"] == "passed"
    assert payload["progress"]["label"] == "Passed"
    assert COOKIE_NAME in response.headers.get("set-cookie", "")


def test_api_clear_progress() -> None:
    response = asyncio.run(_post_json("/api/practice/progress/clear", {}))
    assert response.status_code == 200
    assert response.json() == {
        "ok": True,
        "progress": {
            "passed_count": 0,
            "status": "not_started",
            "label": "Not started",
        },
    }


def test_api_list_and_get_include_progress_labels() -> None:
    list_response = asyncio.run(_get("/api/practice/exercises"))
    assert list_response.status_code == 200
    first = list_response.json()["exercises"][0]
    assert first["progress_label"] in {"Not started", "Attempted", "Passed"}

    get_response = asyncio.run(
        _get("/api/practice/times-archive/times-archive-011")
    )
    assert get_response.status_code == 200
    progress = get_response.json()["progress"]
    assert progress["label"] in {"Not started", "Attempted", "Passed"}
    assert progress["status"] in {"not_started", "attempted", "passed"}
