"""Explain-on-fail: safe context pack + Ollama chat (TIM-93)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

from app.ai.ollama import chat, model_is_installed
from app.catalog.output_requirements import build_output_requirements_text
from app.domain.exercises import Exercise

logger = logging.getLogger(__name__)

MSG_NO_FAILED_ATTEMPT = (
    "There is no failed submit to explain. Submit an answer that does not pass grading first."
)
MSG_OLLAMA_UNREACHABLE = "AI unavailable: Ollama is not reachable on this machine."
MSG_MODEL_MISSING = "AI unavailable: the local model is not ready yet."
MSG_TIMEOUT = "AI unavailable: the local model timed out."
MSG_EMPTY = "AI unavailable: the local model returned an empty response."
MSG_GENERIC = "AI unavailable: could not get an explanation right now."

_SYSTEM_PROMPT = (
    "You are a concise SQL tutor for a practice gym. "
    "Explain why the learner's result did not match expectations and suggest what to try next. "
    "Do not provide a full correct SQL query. "
    "Do not invent expected row values. "
    "Keep the answer short (a few sentences)."
)


@dataclass(frozen=True)
class ExplainContext:
    title: str
    prompt: str
    difficulty: str
    output_requirements: str
    learner_sql: str
    grading_summary: str
    expected_column_names: tuple[str, ...]


@dataclass(frozen=True)
class ExplainSuccess:
    explanation: str


@dataclass(frozen=True)
class ExplainFailure:
    message: str
    status_code: int = 503


def build_explain_context(exercise: Exercise, attempt: dict[str, Any]) -> ExplainContext:
    sql = attempt.get("sql")
    grading = attempt.get("grading")
    summary = ""
    if isinstance(grading, dict):
        raw_summary = grading.get("summary")
        if isinstance(raw_summary, str):
            summary = raw_summary
    return ExplainContext(
        title=exercise.title,
        prompt=exercise.prompt,
        difficulty=exercise.difficulty,
        output_requirements=build_output_requirements_text(exercise),
        learner_sql=sql if isinstance(sql, str) else "",
        grading_summary=summary,
        expected_column_names=tuple(exercise.expected_result.column_names),
    )


def build_chat_messages(context: ExplainContext) -> list[dict[str, str]]:
    columns = ", ".join(context.expected_column_names) or "(none listed)"
    user = (
        f"Exercise title: {context.title}\n"
        f"Difficulty: {context.difficulty}\n"
        f"Prompt:\n{context.prompt}\n\n"
        f"Output requirements:\n{context.output_requirements}\n\n"
        f"Expected column names (order matters): {columns}\n\n"
        f"Learner SQL:\n{context.learner_sql}\n\n"
        f"Grading summary:\n{context.grading_summary}\n"
    )
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def packed_prompt_text(context: ExplainContext) -> str:
    """Flatten context into the user message text sent to the model."""
    return build_chat_messages(context)[1]["content"]


def explain_failed_attempt(
    exercise: Exercise,
    attempt: dict[str, Any],
) -> ExplainSuccess | ExplainFailure:
    """Produce an explanation for a failed submit attempt. Never raises."""
    context = build_explain_context(exercise, attempt)
    messages = build_chat_messages(context)
    try:
        if not model_is_installed():
            return ExplainFailure(message=MSG_MODEL_MISSING)
        text = chat(messages)
        if not text.strip():
            return ExplainFailure(message=MSG_EMPTY)
        return ExplainSuccess(explanation=text.strip())
    except httpx.ConnectError:
        logger.warning("Explain failed: Ollama unreachable", exc_info=True)
        return ExplainFailure(message=MSG_OLLAMA_UNREACHABLE)
    except httpx.TimeoutException:
        logger.warning("Explain failed: Ollama timeout", exc_info=True)
        return ExplainFailure(message=MSG_TIMEOUT)
    except Exception:
        logger.warning("Explain failed for exercise %s", exercise.id, exc_info=True)
        return ExplainFailure(message=MSG_GENERIC)
