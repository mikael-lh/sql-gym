"""Shared Playwright helpers for responsive layout regression tests."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page

LAYOUT_ROW_TOLERANCE_PX = 8

LAYOUT_VIEWPORTS = {
    "desktop": {"width": 1280, "height": 800},
    "mobile": {"width": 390, "height": 844},
}


def assert_controls_on_one_row_js(
    element_ids: list[str],
    *,
    tolerance_px: int = LAYOUT_ROW_TOLERANCE_PX,
) -> str:
    """Return a Playwright ``page.evaluate`` snippet for a single-row layout check."""
    ids_json = json.dumps(element_ids)
    return f"""() => {{
        const ids = {ids_json};
        const centers = ids.map((id) => {{
            const rect = document.getElementById(id)?.getBoundingClientRect();
            return rect ? rect.top + rect.height / 2 : undefined;
        }});
        if (centers.some((center) => center === undefined)) return false;
        const minCenter = Math.min(...centers);
        const maxCenter = Math.max(...centers);
        return maxCenter - minCenter < {tolerance_px};
    }}"""


def assert_controls_on_one_row(
    page: Page,
    element_ids: list[str],
    *,
    tolerance_px: int = LAYOUT_ROW_TOLERANCE_PX,
) -> None:
    """Assert all element ids share one horizontal row within tolerance."""
    result = page.evaluate(assert_controls_on_one_row_js(element_ids, tolerance_px=tolerance_px))
    if not result:
        message = f"Expected controls on one row: {', '.join(element_ids)}"
        raise AssertionError(message)
