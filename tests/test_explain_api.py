"""Tests for explain-on-fail API and safe context pack (TIM-93)."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx

from app.ai.explain import (
    MSG_MODEL_MISSING,
    MSG_NO_FAILED_ATTEMPT,
    MSG_OLLAMA_UNREACHABLE,
    build_explain_context,
    packed_prompt_text,
)
from app.main import app
from app.practice import lookup_exercise
from app.progress.cookie import COOKIE_NAME

EXPECTED_GRID = json.loads(
    Path("src/app/catalog/data/expected_grids/times-archive-011.json").read_text()
)
EXPLAIN_PATH = "/api/practice/times-archive/times-archive-011/explain"
SUBMIT_PATH = "/api/practice/times-archive/times-archive-011/submit"


async def _client_flow(
    *posts: tuple[str, dict[str, object] | None],
) -> list[httpx.Response]:
    transport = httpx.ASGITransport(app=app)
    responses: list[httpx.Response] = []
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
        follow_redirects=False,
    ) as client:
        for path, payload in posts:
            if payload is None:
                responses.append(await client.post(path))
            else:
                responses.append(await client.post(path, json=payload))
    return responses


@patch("app.api.practice.execute_query")
@patch("app.ai.explain.chat")
@patch("app.ai.explain.model_is_installed", return_value=True)
def test_explain_after_failed_submit_returns_explanation(
    _mock_installed: MagicMock,
    mock_chat: MagicMock,
    mock_execute: MagicMock,
) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=("wrong",),
        rows=(("x",),),
        row_count=1,
        truncated=False,
    )
    mock_chat.return_value = "Your column names do not match. Check the required columns."

    submit, explain = asyncio.run(
        _client_flow(
            (SUBMIT_PATH, {"sql": "SELECT 1 AS wrong"}),
            (EXPLAIN_PATH, None),
        )
    )
    assert submit.status_code == 200
    assert submit.json()["grading"]["passed"] is False
    assert explain.status_code == 200
    payload = explain.json()
    assert payload == {
        "explanation": "Your column names do not match. Check the required columns."
    }
    assert "error" not in payload
    assert "reason" not in payload
    mock_chat.assert_called_once()


@patch("app.api.practice.execute_query")
@patch("app.ai.explain.chat")
@patch("app.ai.explain.model_is_installed", return_value=True)
def test_explain_rejects_passed_submit(
    _mock_installed: MagicMock,
    mock_chat: MagicMock,
    mock_execute: MagicMock,
) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=tuple(EXPECTED_GRID["columns"]),
        rows=tuple(tuple(row) for row in EXPECTED_GRID["rows"]),
        row_count=len(EXPECTED_GRID["rows"]),
        truncated=False,
    )

    submit, explain = asyncio.run(
        _client_flow(
            (
                SUBMIT_PATH,
                {"sql": "SELECT headline_main, pub_date FROM times_archive LIMIT 1"},
            ),
            (EXPLAIN_PATH, None),
        )
    )
    assert submit.status_code == 200
    assert submit.json()["grading"]["passed"] is True
    assert explain.status_code == 422
    assert explain.json() == {"error": {"message": MSG_NO_FAILED_ATTEMPT}}
    mock_chat.assert_not_called()


def test_explain_without_attempt_returns_422() -> None:
    response = asyncio.run(_client_flow((EXPLAIN_PATH, None)))[0]
    assert response.status_code == 422
    assert response.json() == {"error": {"message": MSG_NO_FAILED_ATTEMPT}}


def test_explain_unknown_exercise_returns_404() -> None:
    response = asyncio.run(
        _client_flow(
            ("/api/practice/times-archive/times-archive-999/explain", None),
        )
    )[0]
    assert response.status_code == 404


@patch("app.api.practice.execute_query")
@patch("app.ai.explain.model_is_installed", return_value=False)
def test_explain_model_missing_returns_unavailable(
    _mock_installed: MagicMock,
    mock_execute: MagicMock,
) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=("wrong",),
        rows=(("x",),),
        row_count=1,
        truncated=False,
    )

    submit, explain = asyncio.run(
        _client_flow(
            (SUBMIT_PATH, {"sql": "SELECT 1 AS wrong"}),
            (EXPLAIN_PATH, None),
        )
    )
    assert submit.status_code == 200
    assert explain.status_code == 503
    payload = explain.json()
    assert payload == {"error": {"message": MSG_MODEL_MISSING}}
    assert "reason" not in payload["error"]


@patch("app.api.practice.execute_query")
@patch("app.ai.explain.chat", side_effect=httpx.ConnectError("down"))
@patch("app.ai.explain.model_is_installed", return_value=True)
def test_explain_ollama_down_returns_unavailable(
    _mock_installed: MagicMock,
    _mock_chat: MagicMock,
    mock_execute: MagicMock,
) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=("wrong",),
        rows=(("x",),),
        row_count=1,
        truncated=False,
    )

    submit, explain = asyncio.run(
        _client_flow(
            (SUBMIT_PATH, {"sql": "SELECT 1 AS wrong"}),
            (EXPLAIN_PATH, None),
        )
    )
    assert explain.status_code == 503
    assert explain.json() == {"error": {"message": MSG_OLLAMA_UNREACHABLE}}


@patch("app.api.practice.execute_query")
@patch("app.ai.explain.chat", side_effect=httpx.TimeoutException("slow"))
@patch("app.ai.explain.model_is_installed", return_value=True)
def test_explain_timeout_returns_unavailable(
    _mock_installed: MagicMock,
    _mock_chat: MagicMock,
    mock_execute: MagicMock,
) -> None:
    from app.ai.explain import MSG_TIMEOUT
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=("wrong",),
        rows=(("x",),),
        row_count=1,
        truncated=False,
    )

    _submit, explain = asyncio.run(
        _client_flow(
            (SUBMIT_PATH, {"sql": "SELECT 1 AS wrong"}),
            (EXPLAIN_PATH, None),
        )
    )
    assert explain.status_code == 503
    assert explain.json() == {"error": {"message": MSG_TIMEOUT}}


@patch("app.api.practice.execute_query")
@patch("app.ai.explain.chat", return_value="Try aligning column names.")
@patch("app.ai.explain.model_is_installed", return_value=True)
def test_explain_does_not_change_progress_cookie(
    _mock_installed: MagicMock,
    _mock_chat: MagicMock,
    mock_execute: MagicMock,
) -> None:
    from app.execution.models import QueryResult

    mock_execute.return_value = QueryResult(
        columns=("wrong",),
        rows=(("x",),),
        row_count=1,
        truncated=False,
    )

    submit, explain = asyncio.run(
        _client_flow(
            (SUBMIT_PATH, {"sql": "SELECT 1 AS wrong"}),
            (EXPLAIN_PATH, None),
        )
    )
    assert submit.status_code == 200
    assert COOKIE_NAME in submit.headers.get("set-cookie", "")
    assert explain.status_code == 200
    assert COOKIE_NAME not in explain.headers.get("set-cookie", "").lower()
    # Progress from failed submit stays attempted, not rewritten by explain
    assert submit.json()["progress"]["status"] == "attempted"


def test_context_pack_excludes_reference_sql_and_expected_rows() -> None:
    exercise = lookup_exercise("times-archive", "times-archive-011")
    assert exercise is not None
    reference_sql = exercise.expected_result.reference_sql
    assert reference_sql

    attempt = {
        "sql": "SELECT 1 AS wrong",
        "grading": {
            "exercise_id": exercise.id,
            "status": "graded",
            "summary": "Column names do not match.",
            "passed": False,
            "is_placeholder": False,
        },
    }
    context = build_explain_context(exercise, attempt)
    packed = packed_prompt_text(context)

    assert reference_sql not in packed
    assert "reference_sql" not in packed.lower()
    # Expected grid cell values must not appear as spoiler content
    for row in EXPECTED_GRID["rows"]:
        for cell in row:
            cell_text = str(cell)
            if cell_text and cell_text not in attempt["sql"]:
                assert cell_text not in packed
    # Column names are allowed
    for col in exercise.expected_result.column_names:
        assert col in packed
