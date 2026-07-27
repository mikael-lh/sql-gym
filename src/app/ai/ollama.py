"""Local Ollama HTTP client and app-lifespan pull/cleanup.

Assumes a single uvicorn worker for local development. Concurrent
multi-worker pull/delete races are out of Phase 7 scope.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.db.settings import (
    get_ollama_base_url,
    get_ollama_keep_model,
    get_ollama_model,
    get_ollama_pull_timeout_seconds,
    get_ollama_request_timeout_seconds,
)

logger = logging.getLogger(__name__)

# True only when this process successfully pulled the configured model.
_pulled_model_this_process = False


def reset_ollama_lifecycle_state_for_tests() -> None:
    global _pulled_model_this_process
    _pulled_model_this_process = False


def did_pull_model_this_process() -> bool:
    return _pulled_model_this_process


def _mark_pulled() -> None:
    global _pulled_model_this_process
    _pulled_model_this_process = True


def list_model_names(
    *,
    client: httpx.Client | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> list[str]:
    """Return installed model names from GET /api/tags."""
    owns_client = client is None
    http = client or httpx.Client(
        base_url=base_url or get_ollama_base_url(),
        timeout=timeout if timeout is not None else get_ollama_request_timeout_seconds(),
    )
    try:
        response = http.get("/api/tags")
        response.raise_for_status()
        payload = response.json()
        models = payload.get("models") if isinstance(payload, dict) else None
        if not isinstance(models, list):
            return []
        names: list[str] = []
        for item in models:
            if isinstance(item, dict):
                name = item.get("name")
                if isinstance(name, str) and name:
                    names.append(name)
        return names
    finally:
        if owns_client:
            http.close()


def model_is_installed(
    model: str | None = None,
    *,
    client: httpx.Client | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> bool:
    target = model or get_ollama_model()
    names = list_model_names(client=client, base_url=base_url, timeout=timeout)
    return target in names


def pull_model(
    model: str | None = None,
    *,
    client: httpx.Client | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> None:
    """Pull a model via POST /api/pull with stream disabled."""
    target = model or get_ollama_model()
    owns_client = client is None
    http = client or httpx.Client(
        base_url=base_url or get_ollama_base_url(),
        timeout=timeout if timeout is not None else get_ollama_pull_timeout_seconds(),
    )
    try:
        response = http.post("/api/pull", json={"name": target, "stream": False})
        response.raise_for_status()
    finally:
        if owns_client:
            http.close()


def delete_model(
    model: str | None = None,
    *,
    client: httpx.Client | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> None:
    """Delete a model via DELETE /api/delete."""
    target = model or get_ollama_model()
    owns_client = client is None
    http = client or httpx.Client(
        base_url=base_url or get_ollama_base_url(),
        timeout=timeout if timeout is not None else get_ollama_request_timeout_seconds(),
    )
    try:
        response = http.request("DELETE", "/api/delete", json={"name": target})
        response.raise_for_status()
    finally:
        if owns_client:
            http.close()


def chat(
    messages: list[dict[str, str]],
    *,
    model: str | None = None,
    client: httpx.Client | None = None,
    base_url: str | None = None,
    timeout: float | None = None,
) -> str:
    """Run a non-streaming chat completion; return assistant message content."""
    target = model or get_ollama_model()
    owns_client = client is None
    http = client or httpx.Client(
        base_url=base_url or get_ollama_base_url(),
        timeout=timeout if timeout is not None else get_ollama_request_timeout_seconds(),
    )
    try:
        response = http.post(
            "/api/chat",
            json={"model": target, "messages": messages, "stream": False},
        )
        response.raise_for_status()
        payload: Any = response.json()
        message = payload.get("message") if isinstance(payload, dict) else None
        if not isinstance(message, dict):
            raise ValueError("Ollama chat response missing message object")
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Ollama chat response missing content")
        return content
    finally:
        if owns_client:
            http.close()


def ensure_model_pulled_on_startup() -> None:
    """Best-effort pull of the configured model. Never raises."""
    model = get_ollama_model()
    base_url = get_ollama_base_url()
    try:
        with httpx.Client(
            base_url=base_url,
            timeout=get_ollama_request_timeout_seconds(),
        ) as client:
            if model_is_installed(model, client=client):
                logger.info("Ollama model %s already installed; skip pull", model)
                return
        with httpx.Client(
            base_url=base_url,
            timeout=get_ollama_pull_timeout_seconds(),
        ) as client:
            logger.info("Pulling Ollama model %s from %s", model, base_url)
            pull_model(model, client=client)
            _mark_pulled()
            logger.info("Pulled Ollama model %s", model)
    except Exception:
        logger.warning(
            "Ollama launch pull failed for model %s at %s; continuing without AI",
            model,
            base_url,
            exc_info=True,
        )


def cleanup_model_on_shutdown() -> None:
    """Best-effort delete of a model this process pulled. Never raises."""
    if get_ollama_keep_model():
        logger.info("OLLAMA_KEEP_MODEL set; skipping model cleanup")
        return
    if not did_pull_model_this_process():
        logger.info("No Ollama model pulled by this process; skipping cleanup")
        return
    model = get_ollama_model()
    base_url = get_ollama_base_url()
    try:
        with httpx.Client(
            base_url=base_url,
            timeout=get_ollama_request_timeout_seconds(),
        ) as client:
            delete_model(model, client=client)
            logger.info("Deleted Ollama model %s on shutdown", model)
    except Exception:
        logger.warning(
            "Ollama shutdown cleanup failed for model %s at %s",
            model,
            base_url,
            exc_info=True,
        )
