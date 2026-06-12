import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from app.main import app
from app.progress.cookie import COOKIE_NAME

EXPECTED_GRID = json.loads(
    Path("src/app/catalog/data/expected_grids/times-archive-001.json").read_text()
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
    response = asyncio.run(_get("/api/practice/exercises?difficulty=Beginner"))
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] > 0
    assert all(item["difficulty"] == "Beginner" for item in payload["exercises"])


def test_api_get_exercise_returns_workspace_payload() -> None:
    response = asyncio.run(
        _get("/api/practice/times-archive/times-archive-001")
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["exercise"]["id"] == "times-archive-001"
    assert "reference_sql" not in payload["exercise"]
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
            "/api/practice/times-archive/times-archive-001/run",
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
            "/api/practice/times-archive/times-archive-001/run",
            {"sql": "DELETE FROM times_archive"},
        )
    )
    assert response.status_code == 422
    assert "error" in response.json()


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
            "/api/practice/times-archive/times-archive-001/submit",
            {"sql": "SELECT headline_main, pub_date FROM times_archive LIMIT 1"},
        )
    )
    assert response.status_code == 200
    payload = response.json()
    assert "grading" in payload
    assert "progress" in payload
    assert COOKIE_NAME in response.headers.get("set-cookie", "")


def test_api_clear_progress() -> None:
    response = asyncio.run(_post_json("/api/practice/progress/clear", {}))
    assert response.status_code == 200
    assert response.json() == {"ok": True}
