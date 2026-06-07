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


def test_practice_page_renders_placeholder_flow() -> None:
    response = asyncio.run(get("/practice"))

    assert response.status_code == 200
    assert "Times Archive demo" in response.text
    assert "times-api/schema/archive_articles.json" in response.text
    assert "not final production Times data" in response.text
    assert "Beginner" in response.text
    assert "Timed" in response.text
    assert "PostgreSQL target dialect" in response.text
    assert "SQL editor placeholder" in response.text
    assert "Grading feedback" in response.text
    assert "Progress tracking placeholder" in response.text
    assert "Demo-only progress" in response.text
    assert "No SQL is executed" in response.text
    assert "disabled" in response.text


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
