# Browser flow audit — 2026-06-12

Manual browser verification of sql-gym practice workspace flows (Phase 5), using Playwright against a local server with Postgres and full Times Archive import (~11.8M rows).

**Environment:** `uv run uvicorn app.main:app --host 127.0.0.1 --port 8000` with `DATABASE_URL` set.

## Flows verified (passing)

| Flow | Result |
|------|--------|
| `GET /` → `/practice` → first exercise | Pass |
| Direct exercise URL (`/practice/times-archive/times-archive-014`) | Pass |
| Legacy interview URL redirect (`/practice/interview/start`) | Pass |
| Unknown exercise 404 | Pass |
| Run SQL (no full page reload) | Pass |
| Session restore (SQL + last run output after refresh) | Pass |
| Submit incorrect SQL → grading modal → OK dismiss | Pass |
| Submit correct SQL → **Passed** modal | Pass |
| Escape dismisses grading modal | Pass |
| Timed exercise: start timer, countdown, manual submit | Pass |
| Drawer: open, list 50 exercises, badges, select exercise (URL updates) | Pass |
| Filters: difficulty/mode → redirect to eligible exercise with query params | Pass |
| Progress: pass increments header count; Clear progress resets count and badge | Pass |
| Empty SQL validation (run + submit) | Pass |
| DML rejection on run | Pass |
| `/health` | Pass |
| Mobile viewport (390×844): drawer, modal dismiss | Pass |

## Bugs

### BUG-1 — Previous/Next buttons inert on first page load

**Severity:** High  
**Flow:** Footer navigation (§5 manual test plan)

On initial workspace load, `#workspace-prev` and `#workspace-next` are enabled in HTML but lack `data-target-url`. The click handler in `practice-workspace.js` returns early when `button.dataset.targetUrl` is empty. `updateNavigationButtons()` is only called from `applyExercisePayload()` (client-side exercise switches), not during `initPracticeWorkspace()`.

**Repro:**

1. Open `/practice/times-archive/times-archive-001`.
2. Inspect `#workspace-next` — `data-target-url` is absent.
3. Click **Next** — URL and title stay on exercise 001.

**Expected:** Navigation uses `workspace_config.navigation` from the server-rendered JSON on init.

**Fix hint:** Call `updateNavigationButtons(workspaceConfig.navigation)` at the end of `initPracticeWorkspace()`.

---

### BUG-2 — Previous/Next update content but not the browser URL

**Severity:** High  
**Flow:** Footer navigation, browser history

After `data-target-url` is set (e.g. via drawer navigation or manual init), **Next** loads the next exercise in-place but leaves `window.location` on the original exercise.

**Repro:**

1. Open `/practice/times-archive/times-archive-002`.
2. Set `data-target-url` on **Next** (or navigate via drawer first).
3. Click **Next** twice.
4. Title changes (`Business desk articles` → `Count by section` → `Newest articles`) but URL remains `.../times-archive-002`.

**Root cause:** `wireNavButton` calls `navigateByPath()`, which invokes `loadExercise(..., { push: false })`. That path is correct for `popstate` but wrong for explicit footer clicks, which should use `push: true` and `history.pushState`.

**Impact:** Broken deep links after footer navigation, broken share/bookmark of current exercise, broken browser Back/Forward expectations.

---

### BUG-3 — Reference (answer) SQL visible to learners

**Severity:** Medium (product / cheating)  
**Flow:** Sample SQL disclosure

Expanding **Show sample SQL** reveals an **Answer** block with full `reference_sql` (grading canonical query). Phase 4 PRD states `reference_sql` is *not shown to learners*.

**Repro:** Open any exercise → expand sample SQL → **Answer** shows e.g. `SELECT headline_main, pub_date FROM times_archive WHERE section_name = 'Arts' ... LIMIT 500;`

**Evidence:** `docs/audit-artifacts/answer-sql-exposed.png`

---

## Issues (UX / polish)

### ISSUE-1 — Exercise drawer flashes empty before list loads

**Severity:** Low  
**Flow:** Drawer (§5)

Opening the drawer shows an empty list until `/api/practice/exercises` returns. On a fast connection this is ~0–500ms of blank UI.

**Evidence:** `docs/audit-artifacts/drawer-empty-flash.png`

**Fix hint:** Loading skeleton, server-render initial list, or open drawer only after fetch completes.

---

### ISSUE-2 — No favicon

**Severity:** Low  
**Flow:** All pages

`GET /favicon.ico` returns 404. Harmless but produces console noise in some browsers.

---

## Notes (not bugs)

- **Filter eyebrow casing:** Filtered exercise eyebrow text is uppercased via CSS (`BEGINNER` vs `Beginner`); behavior is correct.
- **Content drift (011, 014):** Prompts now reference 1920 dates; prior Phase 4 drift appears resolved.
- **Drawer navigation** correctly updates URL via `loadExercise(..., { push: true })`.
- **Timed auto-submit on expiry** not exercised end-to-end (would require waiting full timer duration); manual submit during timed mode works.

## Test artifacts

- Playwright audit script: `/tmp/browser_flow_audit.py` (ephemeral VM path)
- Screenshots: `docs/audit-artifacts/`
- JSON report: `/tmp/sql-gym-audit/audit_report.json`

## Recommended follow-up

1. Fix BUG-1 and BUG-2 together in `static/js/practice-workspace.js` (init nav targets + `push: true` for footer buttons).
2. Add a Playwright regression test for footer Prev/Next URL sync (complements existing `test_grading_modal.py`).
3. Remove or gate **Answer** block behind a dev-only flag per PRD (BUG-3).
4. Track ISSUE-1/2 in Linear if desired.
