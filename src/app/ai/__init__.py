"""Local LLM helpers (Phase 7 — Ollama)."""

from app.ai.ollama import (
    cleanup_model_on_shutdown,
    ensure_model_pulled_on_startup,
)

__all__ = [
    "cleanup_model_on_shutdown",
    "ensure_model_pulled_on_startup",
]
