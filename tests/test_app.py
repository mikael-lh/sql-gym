import asyncio
import json
from pathlib import Path

import httpx

from app.main import app


async def get(path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(path)


def test_home_page_renders_scaffold() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 200
    assert "SQL Gym" in response.text
    assert "Practice realistic SQL questions on curated datasets" in response.text
    assert "Phase 0 app shell" in response.text


def test_home_page_presents_core_loop_and_placeholders() -> None:
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

    assert "Placeholders, not live features" in response.text
    assert "Future work" in response.text
    for expected_placeholder in [
        "Dataset selection",
        "Difficulty selection",
        "Practice mode",
        "SQL editor",
        "Grading feedback",
        "Progress tracking",
    ]:
        assert expected_placeholder in response.text
    assert "Start practice - coming soon" in response.text
    assert "disabled" in response.text


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
    assert "SQL editor placeholder" in response.text
    assert "Grading feedback" in response.text
    assert "Progress tracking placeholder" in response.text
    assert "Demo-only progress" in response.text
    assert "No SQL is executed" in response.text
    assert "disabled" in response.text
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


def test_practice_exercise_preview_renders_metadata_and_hidden_sample_sql() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-001"))

    assert response.status_code == 200
    assert "Exercise preview" in response.text
    assert "Arts section headlines" in response.text
    assert "Learning objectives" in response.text
    assert "Show sample SQL" in response.text
    assert "No SQL is executed" in response.text
    assert "SQL editor placeholder" in response.text


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
