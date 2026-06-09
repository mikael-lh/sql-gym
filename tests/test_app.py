import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from app.execution.models import ExecutionError, QueryResult
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


def test_home_page_renders_scaffold() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert "SQL Gym" in response.text
    assert "Times Archive SQL exercises" in response.text
    assert "Phase 3 practice" in response.text
    assert "Browse catalog" in response.text
    assert "exercises passed" in response.text


def test_home_page_presents_core_loop_and_deferred_boundaries() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    for expected_step in [
        "Pick a dataset",
        "Pick a difficulty",
        "Choose timed or untimed practice",
        "Complete a SQL exercise",
        "Review grading feedback",
        "Move to the next exercise",
    ]:
        assert expected_step in response.text

    assert "Still deferred" in response.text
    assert "Future work" in response.text
    for expected_placeholder in [
        "Accounts and cross-device sync",
        "AI grading and explanations",
    ]:
        assert expected_placeholder in response.text
    assert "Timed-mode scoring" not in response.text


def test_practice_page_renders_catalog_backed_flow() -> None:
    response = asyncio.run(get("/practice"))

    assert response.status_code == 200
    assert "Browse the practice catalog" in response.text
    assert "Times Archive" in response.text
    assert "Production catalog" in response.text
    assert "times-api/schema/archive_articles.json" in response.text
    assert "Showing 50 of 50 catalog exercises" in response.text
    assert "Beginner" in response.text
    assert "Timed" in response.text
    assert "PostgreSQL" in response.text
    assert "Run SQL on exercise previews" in response.text
    assert "browser cookie" in response.text.lower()
    assert "Clear my progress" in response.text
    assert "Not started" in response.text
    assert "Show hint" in response.text
    assert "SELECT section_name" not in response.text


def test_practice_page_filters_exercises_inline() -> None:
    all_exercises = asyncio.run(get("/practice"))
    filtered = asyncio.run(get("/practice?difficulty=Beginner&mode=Untimed"))

    assert filtered.status_code == 200
    assert "No exercises match the current filters" not in filtered.text
    assert filtered.text.index("Showing ") < filtered.text.index(" of 50 catalog exercises")
    assert "Beginner" in filtered.text
    assert filtered.text.count("exercise-card") < all_exercises.text.count("exercise-card")


def test_practice_exercise_preview_renders_editor_and_session_copy() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-001"))

    assert response.status_code == 200
    assert "Exercise practice" in response.text
    assert "Arts section headlines" in response.text
    assert "Learning objectives" in response.text
    assert "Show sample SQL" in response.text
    assert "cookie" in response.text.lower()
    assert "Not started" in response.text
    assert "SQL editor" in response.text
    assert "Run SQL" in response.text
    assert "Submit for grading" in response.text
    assert "/static/vendor/codemirror/bundle.js" in response.text
    assert "/static/js/practice-editor.js" in response.text


def test_practice_exercise_preview_hides_sample_sql_by_default() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-019"))

    assert response.status_code == 200
    assert "Show sample SQL (illustrative only)" in response.text
    assert '<pre class="sample-sql">' in response.text
    assert "RANK() OVER" in response.text


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


def test_practice_page_links_to_exercise_preview() -> None:
    response = asyncio.run(get("/practice"))

    assert response.status_code == 200
    assert 'href="/practice/times-archive/times-archive-001"' in response.text


def test_practice_page_shows_empty_state_for_no_matches() -> None:
    response = asyncio.run(get("/practice?dataset=missing-dataset"))

    assert response.status_code == 200
    assert "No exercises match the current filters" in response.text
    assert "Showing 0 of 50 catalog exercises" in response.text


@patch("app.main.execute_query")
def test_practice_run_sql_redirects_and_shows_result(mock_execute: MagicMock) -> None:
    mock_execute.return_value = QueryResult(
        columns=("n",),
        rows=((1,),),
        row_count=1,
        truncated=False,
    )

    async def _run_and_follow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
            follow_redirects=True,
        ) as client:
            await client.post(
                "/practice/times-archive/times-archive-001/run",
                data={"sql": "SELECT 1 AS n"},
            )
            return await client.get("/practice/times-archive/times-archive-001")

    page = asyncio.run(_run_and_follow())
    assert page.status_code == 200
    assert "Query result" in page.text
    assert "1 row returned" in page.text


@patch("app.main.execute_query")
def test_practice_submit_sql_shows_grading_feedback(mock_execute: MagicMock) -> None:
    mock_execute.return_value = QueryResult(
        columns=("headline_main", "pub_date"),
        rows=(("Example", "2020-01-01"),),
        row_count=1,
        truncated=False,
    )

    run_client = httpx.ASGITransport(app=app)

    async def _submit_and_follow() -> httpx.Response:
        async with httpx.AsyncClient(transport=run_client, base_url="http://testserver") as client:
            await client.post(
                "/practice/times-archive/times-archive-001/submit",
                data={"sql": "SELECT headline_main, pub_date FROM times_archive LIMIT 1"},
            )
            return await client.get("/practice/times-archive/times-archive-001")

    page = asyncio.run(_submit_and_follow())
    assert page.status_code == 200
    assert "Grading" in page.text
    assert "Not yet correct" in page.text or "Passed" in page.text


@patch("app.main.execute_query")
def test_practice_run_sql_surfaces_execution_error(mock_execute: MagicMock) -> None:
    mock_execute.return_value = ExecutionError(
        message="Only SELECT queries are allowed in the practice database.",
        code="not_select",
    )

    async def _run_and_follow() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            await client.post(
                "/practice/times-archive/times-archive-001/run",
                data={"sql": "DELETE FROM times_archive"},
            )
            return await client.get("/practice/times-archive/times-archive-001")

    page = asyncio.run(_run_and_follow())
    assert "Could not run query" in page.text
    assert "Only SELECT queries are allowed" in page.text


def test_timed_exercise_preview_renders_timer_ui() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-005"))

    assert response.status_code == 200
    assert "Timed exercise" in response.text
    assert "Start timed exercise" in response.text
    assert "practice-timer.js" in response.text


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
