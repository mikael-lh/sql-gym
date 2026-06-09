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


async def _post(
    path: str,
    data: dict[str, str],
    *,
    cookies: dict[str, str] | None = None,
    follow_redirects: bool = False,
) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        cookies=cookies or {},
        follow_redirects=follow_redirects,
    ) as client:
        return await client.post(path, data=data)


def test_interview_start_page_renders() -> None:
    response = asyncio.run(_get("/practice/interview/start"))
    assert response.status_code == 200
    assert "Start an interview session" in response.text
    assert "Start interview session" in response.text
    assert "Unlimited" in response.text


def test_interview_start_post_creates_session_and_redirects() -> None:
    response = asyncio.run(
        _post(
            "/practice/interview/start",
            {"queue_length": "3", "difficulty": ""},
            follow_redirects=False,
        )
    )
    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/practice/interview/times-archive/times-archive-")

    assert location.endswith("times-archive-001")


def test_interview_exercise_page_renders_after_start() -> None:
    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            start = await client.post(
                "/practice/interview/start",
                data={"queue_length": "3", "difficulty": ""},
            )
            assert start.status_code == 303
            return await client.get(start.headers["location"], follow_redirects=True)

    response = asyncio.run(_flow())
    assert response.status_code == 200
    assert "Question 1 of 3" in response.text
    assert "Interview session" in response.text


def test_interview_wrong_exercise_redirects_to_current() -> None:
    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            start = await client.post(
                "/practice/interview/start",
                data={"queue_length": "3", "difficulty": ""},
            )
            await client.get(start.headers["location"])
            return await client.get(
                "/practice/interview/times-archive/times-archive-099",
                follow_redirects=False,
            )

    response = asyncio.run(_flow())
    assert response.status_code == 303
    assert response.headers["location"].endswith("times-archive-001")


@patch("app.main.execute_query")
def test_interview_submit_records_outcome_and_shows_grading(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    rows = tuple(tuple(row) for row in EXPECTED_GRID["rows"])
    mock_execute.return_value = QueryResult(
        columns=tuple(EXPECTED_GRID["columns"]),
        rows=rows,
        row_count=len(rows),
        truncated=False,
    )

    async def _flow() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            start = await client.post(
                "/practice/interview/start",
                data={"queue_length": "3", "difficulty": ""},
            )
            await client.get(start.headers["location"], follow_redirects=True)
            submit = await client.post(
                "/practice/interview/times-archive/times-archive-001/submit",
                data={
                    "sql": "SELECT headline_main, pub_date FROM times_archive LIMIT 1",
                },
                follow_redirects=False,
            )
            page = await client.get(submit.headers["location"], follow_redirects=True)
            return submit, page

    submit_response, page = asyncio.run(_flow())
    assert submit_response.status_code == 303
    assert COOKIE_NAME in submit_response.headers.get("set-cookie", "")
    assert page.status_code == 200
    assert 'id="grading-title"' in page.text
    assert "Next question" in page.text


@patch("app.main.execute_query")
def test_interview_next_advances_to_second_question(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    rows = tuple(tuple(row) for row in EXPECTED_GRID["rows"])
    mock_execute.return_value = QueryResult(
        columns=tuple(EXPECTED_GRID["columns"]),
        rows=rows,
        row_count=len(rows),
        truncated=False,
    )

    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=True,
        ) as client:
            await client.post(
                "/practice/interview/start",
                data={"queue_length": "3", "difficulty": ""},
            )
            await client.post(
                "/practice/interview/times-archive/times-archive-001/submit",
                data={
                    "sql": "SELECT headline_main, pub_date FROM times_archive LIMIT 1",
                },
            )
            return await client.post("/practice/interview/next")

    response = asyncio.run(_flow())
    assert response.status_code == 200
    assert "Question 2 of 3" in response.text
    assert "times-archive-002" in str(response.url)


@patch("app.main.execute_query")
def test_interview_end_early_shows_summary(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    rows = tuple(tuple(row) for row in EXPECTED_GRID["rows"])
    mock_execute.return_value = QueryResult(
        columns=tuple(EXPECTED_GRID["columns"]),
        rows=rows,
        row_count=len(rows),
        truncated=False,
    )

    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=True,
        ) as client:
            await client.post(
                "/practice/interview/start",
                data={"queue_length": "3", "difficulty": ""},
            )
            await client.post(
                "/practice/interview/times-archive/times-archive-001/submit",
                data={
                    "sql": "SELECT headline_main, pub_date FROM times_archive LIMIT 1",
                },
            )
            return await client.post("/practice/interview/end")

    response = asyncio.run(_flow())
    assert response.status_code == 200
    assert "Interview session summary" in response.text
    assert "1 of 3 passed" in response.text


def test_interview_abandon_clears_session_and_returns_to_practice() -> None:
    async def _flow() -> tuple[httpx.Response, httpx.Response]:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=False,
        ) as client:
            await client.post(
                "/practice/interview/start",
                data={"queue_length": "3", "difficulty": ""},
            )
            abandon = await client.post("/practice/interview/abandon")
            practice = await client.get("/practice", follow_redirects=True)
            return abandon, practice

    abandon_response, practice_response = asyncio.run(_flow())
    assert abandon_response.status_code == 303
    assert abandon_response.headers["location"] == "/practice"
    assert practice_response.status_code == 200
    assert "Start interview session" in practice_response.text


@patch("app.main.execute_query")
def test_resume_banner_shown_on_practice(mock_execute: MagicMock) -> None:
    from app.execution.models import QueryResult

    rows = tuple(tuple(row) for row in EXPECTED_GRID["rows"])
    mock_execute.return_value = QueryResult(
        columns=tuple(EXPECTED_GRID["columns"]),
        rows=rows,
        row_count=len(rows),
        truncated=False,
    )

    async def _flow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=True,
        ) as client:
            await client.post(
                "/practice/interview/start",
                data={"queue_length": "3", "difficulty": ""},
            )
            return await client.get("/practice")

    response = asyncio.run(_flow())
    assert response.status_code == 200
    assert "Resume interview" in response.text
