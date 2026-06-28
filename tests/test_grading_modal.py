"""Regression tests for the grading modal hidden state and dismiss behavior."""

from __future__ import annotations

import re
import socket
import subprocess
import time
from collections.abc import Iterator
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CSS_PATH = REPO_ROOT / "static" / "styles.css"


def test_grading_modal_hidden_rule_uses_display_none_important() -> None:
    css = CSS_PATH.read_text()
    match = re.search(
        r"\.workspace-modal-backdrop\[hidden\]\s*\{([^}]+)\}",
        css,
        flags=re.DOTALL,
    )
    assert match is not None, "expected .workspace-modal-backdrop[hidden] rule"
    declarations = re.sub(r"\s+", " ", match.group(1))
    assert "display: none !important" in declarations


def test_grading_modal_backdrop_display_grid_needs_hidden_override() -> None:
    css = CSS_PATH.read_text()
    backdrop_block = re.search(
        r"\.workspace-modal-backdrop\s*\{([^}]+)\}",
        css,
        flags=re.DOTALL,
    )
    assert backdrop_block is not None
    declarations = re.sub(r"\s+", " ", backdrop_block.group(1))
    assert "display: grid" in declarations


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
def test_grading_modal_hidden_on_load_and_dismissible(workspace_server_url: str) -> None:
    modal_selector = "#workspace-grading-modal"
    url = f"{workspace_server_url}/practice/times-archive/times-archive-011"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'"
            )
            modal = page.locator(modal_selector)
            assert not modal.is_visible()

            page.click("#workspace-submit-sql")
            page.wait_for_function(
                "(sel) => document.querySelector(sel).hidden === false",
                arg=modal_selector,
            )
            assert page.locator("#workspace-grading-title").inner_text() == "Not yet correct"

            page.click("#workspace-grading-ok")
            assert not modal.is_visible()
            assert (
                page.evaluate("(sel) => document.querySelector(sel).hidden", modal_selector)
                is True
            )

            mobile = browser.new_context(**playwright.devices["iPhone 13"])
            mobile_page = mobile.new_page()
            mobile_page.goto(url, wait_until="domcontentloaded")
            mobile_page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'"
            )
            mobile_modal = mobile_page.locator(modal_selector)
            assert not mobile_modal.is_visible()
            mobile_page.click("#workspace-submit-sql")
            mobile_page.wait_for_function(
                "(sel) => document.querySelector(sel).hidden === false",
                arg=modal_selector,
            )
            mobile_page.locator("#workspace-grading-ok").tap()
            assert not mobile_modal.is_visible()
        finally:
            browser.close()
