from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from app.main import app
from app.progress.cookie import COOKIE_NAME, load_progress

EXPECTED_GRID = json.loads(
    Path("src/app/catalog/data/expected_grids/times-archive-001.json").read_text()
)


def _rows_from_grid() -> tuple[tuple[object, ...], ...]:
    return tuple(tuple(row) for row in EXPECTED_GRID["rows"])


@patch("app.api.practice.execute_query")
def test_submit_pass_sets_progress_cookie(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=tuple(EXPECTED_GRID["columns"]),
        rows=_rows_from_grid(),
        row_count=len(EXPECTED_GRID["rows"]),
        truncated=False,
    )

    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            return await client.post(
                "/api/practice/times-archive/times-archive-001/submit",
                json={"sql": "SELECT headline_main, pub_date FROM times_archive LIMIT 1"},
            )

    response = asyncio.run(_flow())
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert COOKIE_NAME in set_cookie

    cookie_value = set_cookie.split(f"{COOKIE_NAME}=")[1].split(";")[0]
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"cookie", f"{COOKIE_NAME}={cookie_value}".encode())],
    }
    from starlette.requests import Request

    store = load_progress(Request(scope))
    assert store.get_status("times-archive-001") == "passed"


@patch("app.api.practice.execute_query")
def test_submit_fail_sets_attempted(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=("wrong",),
        rows=(("x",),),
        row_count=1,
        truncated=False,
    )

    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            return await client.post(
                "/api/practice/times-archive/times-archive-001/submit",
                json={"sql": "SELECT 1 AS wrong"},
            )

    response = asyncio.run(_flow())
    set_cookie = response.headers.get("set-cookie", "")
    cookie_value = set_cookie.split(f"{COOKIE_NAME}=")[1].split(";")[0]
    from starlette.requests import Request

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"cookie", f"{COOKIE_NAME}={cookie_value}".encode())],
    }
    store = load_progress(Request(scope))
    assert store.get_status("times-archive-001") == "attempted"


@patch("app.api.practice.execute_query")
def test_wide_result_submit_still_renders_grading_panel(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    grid = json.loads(
        Path("src/app/catalog/data/expected_grids/times-archive-003.json").read_text()
    )
    wide_rows = tuple(tuple(row) for row in grid["rows"])
    mock_execute.return_value = QueryResult(
        columns=tuple(grid["columns"]),
        rows=wide_rows,
        row_count=len(wide_rows),
        truncated=False,
    )

    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post(
                "/api/practice/times-archive/times-archive-003/submit",
                json={
                    "sql": (
                        "SELECT section_name, COUNT(*) AS article_count "
                        "FROM times_archive GROUP BY 1"
                    ),
                },
            )
            return await client.get("/api/practice/times-archive/times-archive-003")

    response = asyncio.run(_flow())
    assert response.status_code == 200
    grading = response.json()["attempt"]["grading"]
    assert grading is not None
    assert grading["passed"] is True


@patch("app.api.practice.execute_query")
def test_run_does_not_set_progress_cookie(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=("n",),
        rows=((1,),),
        row_count=1,
        truncated=False,
    )

    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            return await client.post(
                "/api/practice/times-archive/times-archive-001/run",
                json={"sql": "SELECT 1 AS n"},
            )

    response = asyncio.run(_flow())
    set_cookie = response.headers.get("set-cookie", "")
    assert COOKIE_NAME not in set_cookie


@patch("app.api.practice.execute_query")
def test_fail_after_pass_keeps_passed(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    pass_result = QueryResult(
        columns=tuple(EXPECTED_GRID["columns"]),
        rows=_rows_from_grid(),
        row_count=len(EXPECTED_GRID["rows"]),
        truncated=False,
    )
    fail_result = QueryResult(columns=("wrong",), rows=(("x",),), row_count=1, truncated=False)
    mock_execute.side_effect = [pass_result, fail_result]

    async def _flow() -> str:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            first = await client.post(
                "/api/practice/times-archive/times-archive-001/submit",
                json={"sql": "pass"},
            )
            cookie = first.headers.get("set-cookie", "")
            cookie_pair = cookie.split(";")[0]
            client.cookies.set("sql_gym_progress", cookie_pair.split("=", 1)[1])
            second = await client.post(
                "/api/practice/times-archive/times-archive-001/submit",
                json={"sql": "fail"},
            )
            cookie_header = second.headers.get("set-cookie", "")
            return cookie_header if cookie_header is not None else ""

    set_cookie = asyncio.run(_flow())
    cookie_value = set_cookie.split(f"{COOKIE_NAME}=")[1].split(";")[0]
    from starlette.requests import Request

    store = load_progress(
        Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [(b"cookie", f"{COOKIE_NAME}={cookie_value}".encode())],
            }
        )
    )
    assert store.get_status("times-archive-001") == "passed"


@patch("app.api.practice.execute_query")
def test_timed_pass_stores_elapsed_seconds(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    grid = json.loads(
        Path("src/app/catalog/data/expected_grids/times-archive-005.json").read_text()
    )
    mock_execute.return_value = QueryResult(
        columns=tuple(grid["columns"]),
        rows=tuple(tuple(row) for row in grid["rows"]),
        row_count=len(grid["rows"]),
        truncated=False,
    )

    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            return await client.post(
                "/api/practice/times-archive/times-archive-005/submit",
                json={"sql": "SELECT 1", "elapsed_seconds": 420},
            )

    response = asyncio.run(_flow())
    cookie_value = response.headers.get("set-cookie", "").split(f"{COOKIE_NAME}=")[1].split(";")[0]
    from starlette.requests import Request

    store = load_progress(
        Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [(b"cookie", f"{COOKIE_NAME}={cookie_value}".encode())],
            }
        )
    )
    record = store.exercises.get("times-archive-005")
    assert record is not None
    assert record.elapsed_seconds == 420


@patch("app.api.practice.execute_query")
def test_timed_retry_updates_best_elapsed(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    grid = json.loads(
        Path("src/app/catalog/data/expected_grids/times-archive-005.json").read_text()
    )
    pass_result = QueryResult(
        columns=tuple(grid["columns"]),
        rows=tuple(tuple(row) for row in grid["rows"]),
        row_count=len(grid["rows"]),
        truncated=False,
    )
    mock_execute.return_value = pass_result

    async def _flow() -> str:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            first = await client.post(
                "/api/practice/times-archive/times-archive-005/submit",
                json={"sql": "pass", "elapsed_seconds": 600},
            )
            cookie = first.headers.get("set-cookie", "")
            client.cookies.set("sql_gym_progress", cookie.split("=", 1)[1].split(";")[0])
            second = await client.post(
                "/api/practice/times-archive/times-archive-005/submit",
                json={"sql": "pass", "elapsed_seconds": 300},
            )
            cookie_header = second.headers.get("set-cookie", "")
            return cookie_header if cookie_header is not None else ""

    set_cookie = asyncio.run(_flow())
    cookie_value = set_cookie.split(f"{COOKIE_NAME}=")[1].split(";")[0]
    from starlette.requests import Request

    store = load_progress(
        Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [(b"cookie", f"{COOKIE_NAME}={cookie_value}".encode())],
            }
        )
    )
    assert store.exercises["times-archive-005"].elapsed_seconds == 300


def test_clear_progress_wipes_cookie_store() -> None:
    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            return await client.post("/api/practice/progress/clear")

    response = asyncio.run(_flow())
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    set_cookie = response.headers.get("set-cookie", "")
    assert COOKIE_NAME in set_cookie
    cookie_value = set_cookie.split(f"{COOKIE_NAME}=")[1].split(";")[0]
    from starlette.requests import Request

    store = load_progress(
        Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/",
                "headers": [(b"cookie", f"{COOKIE_NAME}={cookie_value}".encode())],
            }
        )
    )
    assert store.passed_count() == 0
