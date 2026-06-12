import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from app.execution.models import QueryResult
from app.main import app


async def get(path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path)


async def post(path: str, data: dict[str, str]) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=False,
    ) as client:
        return await client.post(path, data=data)


async def get_follow(path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=True,
    ) as client:
        return await client.get(path)


def test_home_redirects_to_workspace_exercise() -> None:
    response = asyncio.run(get_follow("/"))

    assert response.status_code == 200
    assert response.url.path.startswith("/practice/times-archive/")
    assert 'data-workspace-shell' in response.text


def test_practice_redirects_to_workspace_exercise() -> None:
    response = asyncio.run(get_follow("/practice"))

    assert response.status_code == 200
    assert response.url.path.startswith("/practice/times-archive/")
    assert "exercise-card" not in response.text
    assert "Browse the practice catalog" not in response.text


def test_workspace_renders_editor_and_session_copy() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-001"))

    assert response.status_code == 200
    assert "Arts section headlines" in response.text
    assert "Learning objectives" in response.text
    assert "Show sample SQL" in response.text
    assert "Not started" in response.text
    assert "SQL editor" in response.text
    assert "Run SQL" in response.text
    assert "Submit for grading" in response.text
    assert "/static/vendor/codemirror/bundle.js" in response.text
    assert "/static/js/practice-editor.js" in response.text
    assert "/static/js/practice-workspace-entry.js" in response.text


def test_workspace_hides_sample_sql_in_collapsed_details() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-019"))

    assert response.status_code == 200
    assert "Show sample SQL (illustrative only)" in response.text
    assert 'id="workspace-sample-sql"' in response.text
    assert 'id="workspace-answer-sql"' in response.text
    assert "RANK() OVER" in response.text


def test_workspace_renders_reference_sql_answer_below_sample_sql() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-001"))

    assert response.status_code == 200
    assert 'id="workspace-answer-block"' in response.text
    assert "LIMIT 500" in response.text
    assert response.text.index("workspace-sample-sql") < response.text.index("workspace-answer-sql")


def test_practice_exercise_unknown_route_returns_friendly_404() -> None:
    response = asyncio.run(get("/practice/times-archive/missing-exercise"))

    assert response.status_code == 404
    assert "Page not found" in response.text
    assert "could not find that exercise" in response.text
    assert "Return to practice catalog" in response.text


def test_practice_exercise_unknown_dataset_returns_friendly_404() -> None:
    response = asyncio.run(get("/practice/missing-dataset/times-archive-001"))

    assert response.status_code == 404
    assert "could not find that exercise" in response.text


@patch("app.api.practice.execute_query")
def test_practice_run_sql_stores_attempt_in_session(mock_execute: MagicMock) -> None:
    mock_execute.return_value = QueryResult(
        columns=("n",),
        rows=((1,),),
        row_count=1,
        truncated=False,
    )

    async def _run_and_fetch_api() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post(
                "/api/practice/times-archive/times-archive-001/run",
                json={"sql": "SELECT 1 AS n"},
            )
            return await client.get("/api/practice/times-archive/times-archive-001")

    payload = asyncio.run(_run_and_fetch_api()).json()
    assert payload["attempt"]["query_result"]["row_count"] == 1


def test_timed_workspace_renders_timer_region() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-005"))

    assert response.status_code == 200
    assert "Start timed exercise" in response.text
    assert 'id="workspace-timer-region"' in response.text
    assert 'id="workspace-timer-region" hidden' not in response.text


def test_codemirror_assets_are_served() -> None:
    bundle = asyncio.run(get("/static/vendor/codemirror/bundle.js"))
    editor = asyncio.run(get("/static/js/practice-editor.js"))

    assert bundle.status_code == 200
    assert editor.status_code == 200
    assert "initPracticeEditor" in bundle.text or "PracticeEditorBundle" in bundle.text


def test_times_demo_fixture_records_provenance() -> None:
    fixture_path = Path("src/app/fixtures/times/archive_articles_demo.json")
    payload = json.loads(fixture_path.read_text())

    assert payload["provenance"]["source_repository"] == "https://github.com/mikael-lh/times-api"
    assert payload["provenance"]["schema_reference"] == "schema/archive_articles.json"
    assert "not the final production Times dataset" in payload["provenance"]["note"]
    assert len(payload["rows"]) == 2


def test_health_endpoint_reports_ok() -> None:
    response = asyncio.run(get("/health"))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_static_stylesheet_is_served() -> None:
    response = asyncio.run(get("/static/styles.css"))

    assert response.status_code == 200
    assert ".page-shell" in response.text
    assert ".result-table" in response.text
    assert ".workspace-console .result-table-wrap" in response.text
