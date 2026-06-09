#!/usr/bin/env python3
"""Record a browser walkthrough of Phase 2 SQL Gym features."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE_URL = "http://127.0.0.1:8000"
OUTPUT_DIR = Path("/opt/cursor/artifacts")
VIDEO_DIR = OUTPUT_DIR / "phase-2-demo-raw"
FINAL_VIDEO = OUTPUT_DIR / "phase-2-demo.webm"

PASS_SQL = (
    "SELECT section_name, COUNT(*) AS article_count "
    "FROM times_archive "
    "GROUP BY section_name "
    "ORDER BY article_count DESC "
    "LIMIT 500;"
)
FAIL_SQL = "SELECT 1 AS wrong_answer;"


def pause(page, ms: int = 2000) -> None:
    page.wait_for_timeout(ms)


def set_editor_sql(page: Page, sql: str) -> None:
    editor = page.locator("#editor-title")
    editor.scroll_into_view_if_needed()
    page.locator(".cm-content").click()
    page.keyboard.press("Control+A")
    page.keyboard.type(sql, delay=6)


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if VIDEO_DIR.exists():
        shutil.rmtree(VIDEO_DIR)
    VIDEO_DIR.mkdir(parents=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            record_video_dir=str(VIDEO_DIR),
            record_video_size={"width": 1280, "height": 800},
        )
        page = context.new_page()

        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("#page-title")
        pause(page, 3000)

        page.click('a[href="/practice"]')
        page.wait_for_selector("h1")
        pause(page, 3000)

        page.goto(f"{BASE_URL}/practice/times-archive/times-archive-003")
        page.wait_for_selector("#practice-editor-host .cm-editor")
        page.locator("#editor-title").scroll_into_view_if_needed()
        pause(page, 2000)

        set_editor_sql(page, PASS_SQL)
        pause(page, 1000)
        page.click('button[formaction$="/run"]')
        page.wait_for_selector("#result-title", timeout=60000)
        page.locator("#result-title").scroll_into_view_if_needed()
        pause(page, 3500)

        page.click('button[formaction$="/submit"]')
        page.wait_for_selector(".feedback", timeout=60000)
        page.locator(".feedback").first.scroll_into_view_if_needed()
        pause(page, 3500)

        set_editor_sql(page, FAIL_SQL)
        pause(page, 1000)
        page.click('button[formaction$="/submit"]')
        page.wait_for_selector(".feedback", timeout=60000)
        page.locator(".feedback").first.scroll_into_view_if_needed()
        pause(page, 3000)

        video_path = page.video.path() if page.video else None
        context.close()
        browser.close()

    if not video_path:
        print("No video recorded", file=sys.stderr)
        return 1

    recorded = Path(video_path)
    shutil.move(recorded, FINAL_VIDEO)
    print(f"Saved demo video to {FINAL_VIDEO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
