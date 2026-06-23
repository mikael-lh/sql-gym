"""Regression tests for top prev/next navigation and pass-modal Next exercise."""

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
def test_prev_next_controls_live_in_top_header(workspace_server_url: str) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-001"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'",
            )

            top_nav = page.locator(".workspace-top-nav")
            assert top_nav.is_visible()
            assert page.locator(".workspace-footer").count() == 0
            assert top_nav.locator("#workspace-prev").is_visible()
            assert top_nav.locator("#workspace-next").is_visible()
            assert page.locator("#workspace-nav-position").is_visible()

            in_header = page.evaluate(
                """() => {
                    const header = document.querySelector('.workspace-top');
                    const next = document.getElementById('workspace-next');
                    return Boolean(header && next && header.contains(next));
                }"""
            )
            assert in_header is True
        finally:
            browser.close()


@pytest.mark.integration
def test_pass_modal_next_exercise_navigates_without_ok(workspace_server_url: str) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-001"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()

            def fulfill_pass_submit(route, request):  # type: ignore[no-untyped-def]
                if request.method != "POST" or not request.url.endswith("/submit"):
                    route.continue_()
                    return
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps(
                        {
                            "grading": {
                                "exercise_id": "times-archive-001",
                                "status": "passed",
                                "summary": "Result matches expected output.",
                                "passed": True,
                                "is_placeholder": False,
                            },
                            "progress": {"passed_count": 1, "total": 50},
                        }
                    ),
                )

            page.route("**/api/practice/**/submit", fulfill_pass_submit)
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'",
            )

            page.locator(".cm-content").click()
            page.keyboard.type("SELECT 1;", delay=2)
            page.click("#workspace-submit-sql")
            page.wait_for_selector("#workspace-grading-modal:not([hidden])")
            assert page.locator("#workspace-grading-title").inner_text() == "Passed"

            next_button = page.locator("#workspace-grading-next")
            assert next_button.is_visible()
            next_button.click()

            page.wait_for_function(
                "() => window.location.pathname.endsWith('times-archive-002')",
                timeout=10_000,
            )
            assert page.locator("#workspace-grading-modal").evaluate("el => el.hidden") is True
            assert "Business desk articles" in page.locator("#workspace-exercise-title").inner_text()
        finally:
            browser.close()


@pytest.mark.integration
def test_fail_modal_hides_next_exercise_button(workspace_server_url: str) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-001"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'",
            )

            page.locator(".cm-content").click()
            page.keyboard.type("SELECT 1;", delay=2)
            page.click("#workspace-submit-sql")
            page.wait_for_selector("#workspace-grading-modal:not([hidden])")
            assert page.locator("#workspace-grading-title").inner_text() == "Not yet correct"
            assert not page.locator("#workspace-grading-next").is_visible()
        finally:
            browser.close()
