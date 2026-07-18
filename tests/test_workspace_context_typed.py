"""TIM-87: typed workspace context without duplicated top-level aliases."""

from __future__ import annotations

import asyncio

import httpx
from starlette.requests import Request

from app.main import app
from app.practice import PracticeFilters
from app.workspace.context import WorkspaceContext, get_workspace_context


def _request() -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "query_string": b"",
        "client": ("testclient", 50000),
        "server": ("testserver", 80),
        "scheme": "http",
        "session": {},
    }
    return Request(scope)


async def _get(path: str) -> httpx.Response:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as client:
        return await client.get(path)


def test_get_workspace_context_returns_typed_model() -> None:
    context = get_workspace_context(
        _request(),
        "times-archive",
        "times-archive-011",
        PracticeFilters(),
    )

    assert isinstance(context, WorkspaceContext)
    assert context.exercise.id == "times-archive-011"
    assert context.progress.status == "not_started"
    assert "`january_articles`" in context.exercise.output_requirements
    # No duplicated top-level aliases on the typed model.
    assert not hasattr(context, "progress_status")
    assert not hasattr(context, "sql")
    assert not hasattr(context, "output_requirements")


def test_template_mapping_has_no_legacy_top_level_aliases() -> None:
    context = get_workspace_context(
        _request(),
        "times-archive",
        "times-archive-011",
        PracticeFilters(),
    )
    assert context is not None
    mapping = context.as_template_context()

    assert "progress_status" not in mapping
    assert "progress_label" not in mapping
    assert "first_pass_elapsed" not in mapping
    assert "output_requirements" not in mapping
    assert "sql" not in mapping
    assert "query_result" not in mapping
    assert "attempt_status" not in mapping
    assert mapping["progress"]["status"] == "not_started"
    assert mapping["attempt"]["sql"] == ""
    assert mapping["exercise"]["output_requirements"] == context.exercise.output_requirements
    assert mapping["workspace_config"]["exercise_id"] == "times-archive-011"


def test_workspace_page_and_api_render_same_exercise_content() -> None:
    page = asyncio.run(_get("/practice/times-archive/times-archive-011"))
    api = asyncio.run(_get("/api/practice/times-archive/times-archive-011"))

    assert page.status_code == 200
    assert api.status_code == 200
    payload = api.json()
    assert payload["exercise"]["title"] in page.text
    assert payload["exercise"]["prompt"] in page.text
    assert payload["exercise"]["output_requirements"] in page.text
    assert "progress-badge-not_started" in page.text
    assert "Not started" in page.text
