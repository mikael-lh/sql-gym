# UI layout review (sql-gym)

Use when a PR changes **layout or responsive behavior** (`templates/`, `static/styles.css`, workspace chrome). Complements [sql-gym-pre-review-reviewer](../.cursor/skills/sql-gym-pre-review-reviewer/SKILL.md) browser checks.

## Why

DOM structure tests and pairwise layout assertions (e.g. only comparing two of three controls) can pass while the page still looks wrong. Layout PRs need **viewport-matrix** checks and **all controls in a group** verified together.

## Implementer checklist (before opening PR)

1. List affected controls (e.g. `#workspace-prev`, `#workspace-nav-position`, `#workspace-next`).
2. Add or extend a Playwright test that asserts the group stays on **one row** at:
   - **desktop:** 1280×800
   - **mobile:** 390×844
3. Use [`tests/playwright_layout.py`](../tests/playwright_layout.py) — do not copy ad-hoc `offsetTop` snippets.
4. Run `uv run pytest tests/test_<relevant>.py -q` for the touched flows.
5. Leave pre-review boxes unchecked; run **`sql-gym-pre-review`** before merge (even when the user later says “merge”).

## Reviewer checklist (blocking if missing)

1. Confirm the PR diff touches layout/CSS — if yes, layout review is **not** N/A.
2. Run committed layout tests at **both** viewports (or ad-hoc Playwright using the shared helper).
3. Verify **every** control named in the issue/AC is included in the row assertion — not a subset.
4. For first-time layout for a flow, capture a **screenshot** at mobile width in review findings (path or artifact) when Playwright is available.
5. **Blocking** if:
   - Layout/CSS changed but no viewport-matrix test and no documented ad-hoc check;
   - Tests only cover desktop default viewport;
   - Row assertion omits any visible control in the group;
   - User merge request is used to skip pre-review on a UI PR.

## Test helper

```python
from playwright_layout import LAYOUT_VIEWPORTS, assert_controls_on_one_row

# Inside a Playwright test:
for name, viewport in LAYOUT_VIEWPORTS.items():
    page.set_viewport_size(viewport)
    page.goto(url, ...)
    assert_controls_on_one_row(page, ["workspace-prev", "workspace-nav-position", "workspace-next"])
```

## Examples

| Flow | Test file |
|------|-----------|
| Top prev/next nav | `tests/test_workspace_top_navigation.py` |
| Grading modal | `tests/test_grading_modal.py` |
| Console scroll | `tests/test_workspace_console_scroll.py` |
