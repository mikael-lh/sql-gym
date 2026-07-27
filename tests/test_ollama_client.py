"""Unit tests for native Ollama client and lifespan pull/cleanup (TIM-91)."""

from __future__ import annotations

import asyncio
from unittest.mock import patch

import httpx
import pytest
from httpx import Client as RealClient

from app.ai import ollama as ollama_mod
from app.ai.ollama import (
    chat,
    cleanup_model_on_shutdown,
    delete_model,
    ensure_model_pulled_on_startup,
    list_model_names,
    model_is_installed,
    pull_model,
    reset_ollama_lifecycle_state_for_tests,
)
from app.db.settings import (
    get_ollama_base_url,
    get_ollama_keep_model,
    get_ollama_model,
)


@pytest.fixture(autouse=True)
def _reset_lifecycle() -> None:
    reset_ollama_lifecycle_state_for_tests()
    yield
    reset_ollama_lifecycle_state_for_tests()


def test_ollama_settings_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_KEEP_MODEL", raising=False)
    assert get_ollama_base_url() == "http://127.0.0.1:11434"
    assert get_ollama_model() == "llama3.2:3b"
    assert get_ollama_keep_model() is False


def test_ollama_keep_model_truthy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_KEEP_MODEL", "true")
    assert get_ollama_keep_model() is True


def test_list_model_names_parses_tags() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={"models": [{"name": "llama3.2:3b"}, {"name": "other:latest"}]},
        )
    )
    with httpx.Client(transport=transport, base_url="http://ollama.test") as client:
        assert list_model_names(client=client) == ["llama3.2:3b", "other:latest"]


def test_model_is_installed() -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(200, json={"models": [{"name": "llama3.2:3b"}]})
    )
    with httpx.Client(transport=transport, base_url="http://ollama.test") as client:
        assert model_is_installed("llama3.2:3b", client=client) is True
        assert model_is_installed("missing:7b", client=client) is False


def test_pull_and_delete_and_chat() -> None:
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(f"{request.method} {request.url.path}")
        if request.url.path == "/api/pull":
            return httpx.Response(200, json={"status": "success"})
        if request.url.path == "/api/delete":
            return httpx.Response(200, json={"status": "success"})
        if request.url.path == "/api/chat":
            return httpx.Response(
                200,
                json={"message": {"role": "assistant", "content": "Try fixing the JOIN."}},
            )
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport, base_url="http://ollama.test") as client:
        pull_model("llama3.2:3b", client=client)
        delete_model("llama3.2:3b", client=client)
        text = chat(
            [{"role": "user", "content": "why failed?"}],
            model="llama3.2:3b",
            client=client,
        )
    assert text == "Try fixing the JOIN."
    assert "POST /api/pull" in calls
    assert "DELETE /api/delete" in calls
    assert "POST /api/chat" in calls


def test_ensure_model_pulled_skips_when_already_installed() -> None:
    with (
        patch("app.ai.ollama.get_ollama_model", return_value="llama3.2:3b"),
        patch("app.ai.ollama.get_ollama_base_url", return_value="http://ollama.test"),
        patch("app.ai.ollama.model_is_installed", return_value=True) as mock_installed,
        patch("app.ai.ollama.pull_model") as mock_pull,
    ):
        ensure_model_pulled_on_startup()
    mock_installed.assert_called_once()
    mock_pull.assert_not_called()
    assert ollama_mod.did_pull_model_this_process() is False


def test_ensure_model_pulled_marks_ownership_on_pull() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/tags":
            return httpx.Response(200, json={"models": []})
        if request.url.path == "/api/pull":
            return httpx.Response(200, json={"status": "success"})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    def fake_client(*_args: object, **_kwargs: object) -> httpx.Client:
        return RealClient(transport=transport, base_url="http://ollama.test")

    with (
        patch("app.ai.ollama.get_ollama_model", return_value="llama3.2:3b"),
        patch("app.ai.ollama.get_ollama_base_url", return_value="http://ollama.test"),
        patch("app.ai.ollama.httpx.Client", side_effect=fake_client),
    ):
        ensure_model_pulled_on_startup()
    assert ollama_mod.did_pull_model_this_process() is True


def test_ensure_model_pulled_swallows_errors() -> None:
    with (
        patch("app.ai.ollama.get_ollama_model", return_value="llama3.2:3b"),
        patch("app.ai.ollama.get_ollama_base_url", return_value="http://ollama.test"),
        patch(
            "app.ai.ollama.httpx.Client",
            side_effect=httpx.ConnectError("down"),
        ),
    ):
        ensure_model_pulled_on_startup()
    assert ollama_mod.did_pull_model_this_process() is False


def test_cleanup_skips_when_keep_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_KEEP_MODEL", "1")
    ollama_mod._mark_pulled()
    with patch("app.ai.ollama.delete_model") as mock_delete:
        cleanup_model_on_shutdown()
    mock_delete.assert_not_called()


def test_cleanup_skips_when_not_pulled() -> None:
    with patch("app.ai.ollama.delete_model") as mock_delete:
        cleanup_model_on_shutdown()
    mock_delete.assert_not_called()


def test_cleanup_deletes_when_pulled() -> None:
    ollama_mod._mark_pulled()

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/delete":
            return httpx.Response(200, json={"status": "success"})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)

    def fake_client(*_args: object, **_kwargs: object) -> httpx.Client:
        return RealClient(transport=transport, base_url="http://ollama.test")

    with (
        patch("app.ai.ollama.get_ollama_keep_model", return_value=False),
        patch("app.ai.ollama.get_ollama_model", return_value="llama3.2:3b"),
        patch("app.ai.ollama.get_ollama_base_url", return_value="http://ollama.test"),
        patch("app.ai.ollama.httpx.Client", side_effect=fake_client),
    ):
        cleanup_model_on_shutdown()
    assert ollama_mod.did_pull_model_this_process() is True


def test_create_app_lifespan_pulls_and_cleans() -> None:
    from app.main import create_app

    async def _run() -> None:
        order: list[str] = []

        def _open() -> None:
            order.append("open")

        def _pull() -> None:
            order.append("pull")

        def _close() -> None:
            order.append("close")

        def _cleanup() -> None:
            order.append("cleanup")

        with (
            patch("app.main.open_pool", side_effect=_open),
            patch("app.main.close_pool", side_effect=_close),
            patch("app.main.ensure_model_pulled_on_startup", side_effect=_pull),
            patch("app.main.cleanup_model_on_shutdown", side_effect=_cleanup),
        ):
            app = create_app()
            async with app.router.lifespan_context(app):
                assert order == ["open", "pull"]
            assert order == ["open", "pull", "close", "cleanup"]

    asyncio.run(_run())
