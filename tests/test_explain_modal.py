"""Playwright coverage for Explain with AI on the failed grading modal (TIM-94)."""

from __future__ import annotations

import os
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from playwright_layout import LAYOUT_VIEWPORTS, assert_controls_on_one_row

REPO_ROOT = Path(__file__).resolve().parents[1]
EXERCISE_PATH = "/practice/times-archive/times-archive-011"
MODAL_SELECTOR = "#workspace-grading-modal"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def workspace_server_url() -> Iterator[str]:
    port = _free_port()
    host = "127.0.0.1"
    base_url = f"http://{host}:{port}"
    env = os.environ.copy()
    env["OLLAMA_BASE_URL"] = "http://127.0.0.1:9"
    proc = subprocess.Popen(
        ["uv", "run", "uvicorn", "app.main:app", "--host", host, "--port", str(port)],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env=env,
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


def _stub_failed_submit(page: object) -> None:
    page.route(  # type: ignore[attr-defined]
        "**/api/practice/*/*/submit",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=(
                '{"grading":{"exercise_id":"times-archive-011","status":"graded",'
                '"summary":"Column names do not match.","passed":false,'
                '"is_placeholder":false},'
                '"progress":{"passed_count":0,"total":20,"status":"attempted",'
                '"label":"Attempted"}}'
            ),
        ),
    )


def _stub_passed_submit(page: object) -> None:
    page.route(  # type: ignore[attr-defined]
        "**/api/practice/*/*/submit",
        lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=(
                '{"grading":{"exercise_id":"times-archive-011","status":"graded",'
                '"summary":"Correct.","passed":true,"is_placeholder":false},'
                '"progress":{"passed_count":1,"total":20,"status":"passed",'
                '"label":"Passed"}}'
            ),
        ),
    )


def _open_submit_modal(page: object, base_url: str) -> None:
    page.goto(f"{base_url}{EXERCISE_PATH}", wait_until="domcontentloaded")  # type: ignore[attr-defined]
    page.wait_for_function(  # type: ignore[attr-defined]
        "() => document.documentElement.dataset.workspaceReady === 'submit'"
    )
    page.evaluate(  # type: ignore[attr-defined]
        """() => {
          if (typeof globalThis.resetPracticeEditor === 'function') {
            globalThis.resetPracticeEditor(
              'practice-editor-host',
              'practice-sql-input',
              'SELECT 1 AS wrong',
            );
          } else {
            const input = document.getElementById('practice-sql-input');
            if (input) input.value = 'SELECT 1 AS wrong';
          }
        }"""
    )
    # Ensure submit reads non-empty SQL from the synced hidden input.
    page.wait_for_function(  # type: ignore[attr-defined]
        "() => (document.getElementById('practice-sql-input')?.value || '').trim().length > 0"
    )
    page.click("#workspace-submit-sql")  # type: ignore[attr-defined]
    page.wait_for_function(  # type: ignore[attr-defined]
        "(sel) => document.querySelector(sel).hidden === false",
        arg=MODAL_SELECTOR,
    )


@pytest.mark.integration
def test_fail_modal_shows_explain_and_loads_text(workspace_server_url: str) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            _stub_failed_submit(page)
            page.route(
                "**/explain",
                lambda route: route.fulfill(
                    status=200,
                    content_type="application/json",
                    body='{"explanation":"Check your column names against the requirements."}',
                ),
            )
            _open_submit_modal(page, workspace_server_url)
            explain = page.locator("#workspace-explain-ai")
            assert explain.is_visible()
            assert page.locator("#workspace-grading-next").is_hidden()

            for _name, viewport in LAYOUT_VIEWPORTS.items():
                page.set_viewport_size(viewport)
                assert_controls_on_one_row(
                    page,
                    ["workspace-explain-ai", "workspace-grading-ok"],
                )

            explain.click()
            page.wait_for_selector("#workspace-explain-text:not([hidden])")
            assert (
                page.locator("#workspace-explain-text").inner_text()
                == "Check your column names against the requirements."
            )
        finally:
            browser.close()


UNAVAILABLE_EXPLAIN_BODY = (
    '{"error":{"message":'
    '"AI unavailable: Ollama is not reachable on this machine."}}'
)


@pytest.mark.integration
def test_fail_modal_explain_shows_server_unavailable_message(
    workspace_server_url: str,
) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            _stub_failed_submit(page)
            page.route(
                "**/explain",
                lambda route: route.fulfill(
                    status=503,
                    content_type="application/json",
                    body=UNAVAILABLE_EXPLAIN_BODY,
                ),
            )
            _open_submit_modal(page, workspace_server_url)
            page.click("#workspace-explain-ai")
            page.wait_for_selector("#workspace-explain-text:not([hidden])")
            assert (
                page.locator("#workspace-explain-text").inner_text()
                == "AI unavailable: Ollama is not reachable on this machine."
            )
        finally:
            browser.close()


@pytest.mark.integration
def test_pass_modal_hides_explain(workspace_server_url: str) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            _stub_passed_submit(page)
            _open_submit_modal(page, workspace_server_url)
            assert page.locator("#workspace-grading-title").inner_text() == "Passed"
            assert page.locator("#workspace-explain-ai").is_hidden()
        finally:
            browser.close()
