"""Regression tests for collapsible hint and schema panels in the workspace."""

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
def test_hint_and_schema_collapsed_by_default(workspace_server_url: str) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-001"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'",
            )

            hint_details = page.locator("#workspace-hint-details")
            schema_details = page.locator("#workspace-schema-details")
            assert hint_details.evaluate("el => el.open") is False
            assert schema_details.evaluate("el => el.open") is False
            assert not page.locator("#workspace-hint-text").is_visible()
            assert not page.locator("#workspace-schema-content").is_visible()

            hint_details.locator("summary").click()
            assert page.locator("#workspace-hint-text").is_visible()
            assert "section_name" in page.locator("#workspace-hint-text").inner_text()

            schema_details.locator("summary").click()
            assert page.locator("#workspace-schema-content").is_visible()
            assert "times_archive" in page.locator("#workspace-schema-content").inner_text()
        finally:
            browser.close()


@pytest.mark.integration
def test_schema_panel_follows_hint_in_dom(workspace_server_url: str) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-001"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'",
            )
            follows = page.evaluate(
                """() => {
                    const hint = document.getElementById('workspace-hint-details');
                    const schema = document.getElementById('workspace-schema-details');
                    return Boolean(
                      hint &&
                      schema &&
                      hint.compareDocumentPosition(schema) &
                        Node.DOCUMENT_POSITION_FOLLOWING
                    );
                }"""
            )
            assert follows is True
        finally:
            browser.close()


@pytest.mark.integration
def test_context_disclosures_collapse_on_footer_navigation(
    workspace_server_url: str,
) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-001"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'",
            )

            page.locator("#workspace-hint-details summary").click()
            page.locator("#workspace-schema-details summary").click()
            assert page.locator("#workspace-hint-details").evaluate("el => el.open") is True
            assert page.locator("#workspace-schema-details").evaluate("el => el.open") is True

            page.click("#workspace-next")
            page.wait_for_function(
                "() => window.location.pathname.endsWith('times-archive-002')",
                timeout=10_000,
            )
            assert page.locator("#workspace-hint-details").evaluate("el => el.open") is False
            assert page.locator("#workspace-schema-details").evaluate("el => el.open") is False
            assert not page.locator("#workspace-hint-text").is_visible()
        finally:
            browser.close()
