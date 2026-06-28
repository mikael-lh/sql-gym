"""Regression tests for the auto-start elapsed stopwatch."""

from __future__ import annotations

import json
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def workspace_server_url() -> Iterator[str]:
    port = _free_port()
    host = "127.0.0.1"
    base_url = f"http://{host}:{port}"
    proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--host", host, "--port", str(port)],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if proc.poll() is not None:
            pytest.fail("uvicorn exited before becoming ready")
        try:
            with socket.create_connection((host, port), timeout=0.5):
                break
        except OSError:
            time.sleep(0.1)
    else:
        proc.terminate()
        pytest.fail("timed out waiting for uvicorn")

    try:
        yield base_url
    finally:
        proc.terminate()
        proc.wait(timeout=5)


sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright


@pytest.mark.integration
def test_stopwatch_ticks_and_submits_elapsed_seconds(workspace_server_url: str) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-011"
    captured: dict[str, object] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()

            def capture_submit(route, request):  # type: ignore[no-untyped-def]
                if request.method != "POST" or not request.url.endswith("/submit"):
                    route.continue_()
                    return
                captured["body"] = request.post_data_json
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(
                        {
                            "grading": {
                                "exercise_id": "times-archive-011",
                                "status": "passed",
                                "summary": "Result matches expected output.",
                                "passed": True,
                                "is_placeholder": False,
                            },
                            "progress": {"passed_count": 1, "total": 60},
                        }
                    ),
                )

            page.route("**/api/practice/**/submit", capture_submit)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'",
            )
            assert page.locator("#timer-display").inner_text() == "0:00"
            page.wait_for_timeout(1100)
            first_tick = page.locator("#timer-display").inner_text()
            assert first_tick != "0:00"

            page.locator(".cm-content").click()
            page.keyboard.type("SELECT 1;", delay=2)
            page.click("#workspace-submit-sql")
            page.wait_for_selector("#workspace-grading-modal:not([hidden])")

            body = captured.get("body")
            assert isinstance(body, dict)
            elapsed = body.get("elapsed_seconds")
            assert isinstance(elapsed, int)
            assert elapsed >= 1

            frozen = page.locator("#timer-display").inner_text()
            page.wait_for_timeout(1100)
            assert page.locator("#timer-display").inner_text() == frozen
        finally:
            browser.close()
