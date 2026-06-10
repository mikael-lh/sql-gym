import asyncio
import json
import re

import httpx

from app.main import app


async def get(path: str, *, follow_redirects: bool = False) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=follow_redirects,
    ) as client:
        return await client.get(path)


def test_home_redirects_to_practice() -> None:
    response = asyncio.run(get("/"))

    assert response.status_code == 303
    assert response.headers["location"] == "/practice"


def test_practice_redirects_to_first_exercise() -> None:
    response = asyncio.run(get("/practice"))

    assert response.status_code == 303
    assert response.headers["location"].startswith("/practice/times-archive/")


def test_practice_redirect_preserves_filters() -> None:
    response = asyncio.run(get("/practice?difficulty=Beginner&mode=Untimed"))

    assert response.status_code == 303
    location = response.headers["location"]
    assert location.startswith("/practice/times-archive/")
    assert "difficulty=Beginner" in location
    assert "mode=Untimed" in location


def test_workspace_renders_shell_without_catalog_cards() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-001"))

    assert response.status_code == 200
    assert 'data-workspace-shell' in response.text
    assert "Browse the practice catalog" not in response.text
    assert "Arts section headlines" in response.text
    assert "Schema" in response.text
    assert "article_id" in response.text
    assert "Learning objectives" in response.text
    assert "Show sample SQL" in response.text
    assert "Output console" in response.text
    assert 'id="workspace-config"' in response.text
    assert "exercise-card" not in response.text
    assert "Browse the practice catalog" not in response.text
    assert "catalog-card" not in response.text


def test_workspace_renders_editor_and_actions() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-001"))

    assert response.status_code == 200
    assert "SQL editor" in response.text
    assert 'id="workspace-run-sql"' in response.text
    assert 'id="workspace-submit-sql"' in response.text
    assert "/static/js/practice-workspace-entry.js" in response.text
    assert 'id="workspace-run-sql"' in response.text
    assert 'id="workspace-console"' in response.text


def test_workspace_exercise_outside_filter_redirects() -> None:
    response = asyncio.run(
        get("/practice/times-archive/times-archive-005?difficulty=Beginner&mode=Untimed")
    )

    assert response.status_code == 303
    assert "difficulty=Beginner" in response.headers["location"]
    assert "mode=Untimed" in response.headers["location"]


def test_workspace_config_includes_attempt_restore_payload() -> None:
    response = asyncio.run(get("/practice/times-archive/times-archive-001"))

    assert response.status_code == 200
    match = re.search(
        r'<script type="application/json" id="workspace-config">(.*?)</script>',
        response.text,
        re.DOTALL,
    )
    assert match is not None
    config = json.loads(match.group(1))
    assert config["dataset_id"] == "times-archive"
    assert config["exercise_id"] == "times-archive-001"
    assert "attempt" in config
    assert "query_result" in config["attempt"]
    assert "execution_error" in config["attempt"]


def test_workspace_unknown_exercise_returns_404() -> None:
    response = asyncio.run(get("/practice/times-archive/missing-exercise"))

    assert response.status_code == 404
    assert "could not find that exercise" in response.text
