from __future__ import annotations

from starlette.requests import Request
from starlette.responses import Response

from app.catalog import TIMES_ARCHIVE_CATALOG
from app.domain.progress import ProgressStore
from app.progress.cookie import (
    COOKIE_NAME,
    MAX_AGE_SECONDS,
    attach_progress_cookie,
    dump_progress,
    load_progress,
)


def _request_with_cookie(value: str) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"cookie", f"{COOKIE_NAME}={value}".encode())],
    }
    return Request(scope)


def test_roundtrip_signed_progress_cookie() -> None:
    store = ProgressStore().apply_submit_outcome(
        "times-archive-001",
        passed=True,
        elapsed_seconds=120,
    )
    request = _request_with_cookie(dump_progress(store))
    loaded = load_progress(request)
    assert loaded.get_status("times-archive-001") == "passed"
    assert loaded.exercises["times-archive-001"].elapsed_seconds == 120


def test_tampered_cookie_returns_empty_store() -> None:
    request = _request_with_cookie("not-a-valid-signature")
    assert load_progress(request).passed_count() == 0


def test_unknown_schema_version_returns_empty_store() -> None:
    from app.progress import cookie as cookie_module

    payload = {"v": 99, "exercises": {}}
    bad = cookie_module._serializer().dumps(payload)
    request = _request_with_cookie(bad)
    assert load_progress(request).passed_count() == 0


def test_attach_progress_cookie_sets_max_age() -> None:
    response = Response()
    attach_progress_cookie(response, ProgressStore())
    set_cookie = response.headers.get("set-cookie", "")
    assert COOKIE_NAME in set_cookie
    assert f"Max-Age={MAX_AGE_SECONDS}" in set_cookie
    assert "HttpOnly" in set_cookie


def test_apply_submit_outcome_pass_sticky_and_best_time() -> None:
    store = ProgressStore()
    store = store.apply_submit_outcome("ex-1", passed=False)
    assert store.get_status("ex-1") == "attempted"
    store = store.apply_submit_outcome("ex-1", passed=True, elapsed_seconds=300)
    assert store.get_status("ex-1") == "passed"
    store = store.apply_submit_outcome("ex-1", passed=False)
    assert store.get_status("ex-1") == "passed"
    store = store.apply_submit_outcome("ex-1", passed=True, elapsed_seconds=200)
    assert store.exercises["ex-1"].elapsed_seconds == 200
    store = store.apply_submit_outcome("ex-1", passed=True, elapsed_seconds=250)
    assert store.exercises["ex-1"].elapsed_seconds == 200


def test_progress_payload_stays_under_typical_cookie_budget() -> None:
    store = ProgressStore()
    for exercise in TIMES_ARCHIVE_CATALOG.exercises:
        store = store.apply_submit_outcome(
            exercise.id,
            passed=True,
            elapsed_seconds=600,
        )
    assert len(dump_progress(store).encode()) < 4096
