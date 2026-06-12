"""Regression tests for footer Prev/Next navigation URL sync."""

from __future__ import annotations

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
def test_footer_next_sets_target_url_on_load_and_updates_location(
    workspace_server_url: str,
) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-001"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'"
            )

            next_button = page.locator("#workspace-next")
            assert next_button.is_enabled()
            target = next_button.get_attribute("data-target-url")
            assert target is not None
            assert "times-archive-002" in target

            next_button.click()
            page.wait_for_function(
                "() => window.location.pathname.endsWith('times-archive-002')",
                timeout=10_000,
            )
            title = page.locator("#workspace-exercise-title").inner_text()
            assert "Business desk articles" in title
        finally:
            browser.close()


@pytest.mark.integration
def test_footer_prev_next_and_back_navigation(workspace_server_url: str) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-002"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'"
            )

            page.click("#workspace-next")
            page.wait_for_function(
                "() => window.location.pathname.endsWith('times-archive-003')",
                timeout=10_000,
            )
            title_after_next = page.locator("#workspace-exercise-title").inner_text()

            page.go_back()
            page.wait_for_function(
                "() => window.location.pathname.endsWith('times-archive-002')",
                timeout=10_000,
            )
            page.wait_for_function(
                """(title) => {
                    const el = document.getElementById('workspace-exercise-title');
                    return el && el.innerText.includes(title);
                }""",
                arg="Business desk",
                timeout=10_000,
            )

            page.click("#workspace-prev")
            page.wait_for_function(
                "() => window.location.pathname.endsWith('times-archive-001')",
                timeout=10_000,
            )
            title = page.locator("#workspace-exercise-title").inner_text()
            assert "Arts section headlines" in title
            assert title_after_next  # used by back navigation above
        finally:
            browser.close()
