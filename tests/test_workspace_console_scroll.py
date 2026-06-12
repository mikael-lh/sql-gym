"""Browser regression: console results scroll in a fixed panel without growing the page."""

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
def test_console_results_scroll_without_page_growth(workspace_server_url: str) -> None:
    url = f"{workspace_server_url}/practice/times-archive/times-archive-001"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.goto(url, wait_until="domcontentloaded")
            page.wait_for_function(
                "() => document.documentElement.dataset.workspaceReady === 'submit'"
            )
            before = page.evaluate(
                """() => ({
                    doc: document.documentElement.scrollHeight,
                    panel: document.querySelector('.workspace-console-panel')?.offsetHeight ?? 0,
                })"""
            )
            page.evaluate(
                """() => {
                document.getElementById('practice-sql-input').value =
                  "SELECT headline_main, pub_date FROM times_archive WHERE section_name = 'Arts' ORDER BY pub_date DESC";
            }"""
            )
            page.click("#workspace-run-sql")
            page.wait_for_function(
                "() => document.querySelectorAll('.workspace-console-results tbody tr').length >= 100"
            )
            after = page.evaluate(
                """() => {
                const results = document.querySelector('.workspace-console-results');
                if (!results) {
                    return { error: 'missing results region' };
                }
                const beforeScroll = results.scrollTop;
                results.scrollTop = 300;
                return {
                    doc: document.documentElement.scrollHeight,
                    panel: document.querySelector('.workspace-console-panel')?.offsetHeight ?? 0,
                    rowCount: document.querySelectorAll('.workspace-console-results tbody tr').length,
                    canScroll: results.scrollHeight > results.clientHeight,
                    scrollTopAfter: results.scrollTop,
                    scrollTopBefore: beforeScroll,
                };
            }"""
            )
            assert "error" not in after
            assert after["rowCount"] >= 100
            assert after["canScroll"] is True
            assert after["scrollTopAfter"] > after["scrollTopBefore"]
            assert after["doc"] == before["doc"]
            assert after["panel"] == before["panel"]
        finally:
            browser.close()
