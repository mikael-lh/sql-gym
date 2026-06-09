from __future__ import annotations

import os
from typing import Any

from itsdangerous import BadSignature, URLSafeSerializer
from starlette.requests import Request
from starlette.responses import Response

from app.domain.progress import ExerciseProgress, ProgressStore

COOKIE_NAME = "sql_gym_progress"
MAX_AGE_SECONDS = 5_184_000  # 60 days
SCHEMA_VERSION = 1


def _session_secret() -> str:
    return os.environ.get("SESSION_SECRET", "dev-only-session-secret-change-me")


def _serializer() -> URLSafeSerializer:
    return URLSafeSerializer(_session_secret(), salt="sql-gym-progress")


def _store_to_payload(store: ProgressStore) -> dict[str, Any]:
    exercises: dict[str, dict[str, Any]] = {}
    for exercise_id, record in store.exercises.items():
        payload: dict[str, Any] = {"status": record.status}
        if record.passed_at is not None:
            payload["passed_at"] = record.passed_at
        if record.elapsed_seconds is not None:
            payload["elapsed_seconds"] = record.elapsed_seconds
        exercises[exercise_id] = payload
    return {"v": store.version, "exercises": exercises}


def _payload_to_store(payload: dict[str, Any]) -> ProgressStore | None:
    version = payload.get("v")
    if version != SCHEMA_VERSION:
        return None
    raw_exercises = payload.get("exercises")
    if not isinstance(raw_exercises, dict):
        return None

    exercises: dict[str, ExerciseProgress] = {}
    for exercise_id, record in raw_exercises.items():
        if not isinstance(exercise_id, str) or not isinstance(record, dict):
            continue
        status = record.get("status")
        if status not in {"attempted", "passed"}:
            continue
        passed_at = record.get("passed_at")
        elapsed = record.get("elapsed_seconds")
        exercises[exercise_id] = ExerciseProgress(
            status=status,
            passed_at=passed_at if isinstance(passed_at, str) else None,
            elapsed_seconds=elapsed if isinstance(elapsed, int) else None,
        )
    return ProgressStore(version=SCHEMA_VERSION, exercises=exercises)


def dump_progress(store: ProgressStore) -> str:
    return _serializer().dumps(_store_to_payload(store))


def load_progress(request: Request) -> ProgressStore:
    raw = request.cookies.get(COOKIE_NAME)
    if not raw:
        return ProgressStore()
    try:
        payload = _serializer().loads(raw)
    except BadSignature:
        return ProgressStore()
    if not isinstance(payload, dict):
        return ProgressStore()
    store = _payload_to_store(payload)
    return store if store is not None else ProgressStore()


def attach_progress_cookie(response: Response, store: ProgressStore) -> None:
    response.set_cookie(
        key=COOKIE_NAME,
        value=dump_progress(store),
        max_age=MAX_AGE_SECONDS,
        httponly=True,
        samesite="lax",
        path="/",
    )


def clear_progress_cookie(response: Response) -> None:
    response.delete_cookie(key=COOKIE_NAME, path="/")
