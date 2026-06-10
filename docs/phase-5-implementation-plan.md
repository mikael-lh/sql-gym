# Phase 5 implementation plan

## Status

**Approved and implemented** (2026-06-10) — Phase 5 shipped (TIM-56 epic, TIM-57–TIM-64).

## Source

- PRD: `prd/phase-5-console-workspace.md` (approved via product review)
- Proposed Linear epic: **TIM-56** _(create after plan approval)_
- Proposed child issues: **TIM-57** → **TIM-64** (implementation order below)

## Planning decisions

### Routes (target state)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Redirect → `/practice` (see below) |
| GET | `/practice` | Redirect → first eligible exercise path |
| GET | `/practice/{dataset_id}/{exercise_id}` | Workspace shell (SSR initial load) |
| GET | `/api/practice/exercises` | Filtered exercise list for drawer (JSON) |
| GET | `/api/practice/{dataset_id}/{exercise_id}` | Exercise payload + session attempt state (JSON) |
| POST | `/api/practice/{dataset_id}/{exercise_id}/run` | Execute SQL → JSON grid or error |
| POST | `/api/practice/{dataset_id}/{exercise_id}/submit` | Grade → JSON + `Set-Cookie` progress |
| POST | `/api/practice/progress/clear` | Clear progress cookie → JSON `{ "ok": true }` |
| GET | `/practice/interview/*` | **Removed** → redirect to `/practice` |
| POST | `/practice/{dataset_id}/{exercise_id}/run` | **Removed** (replaced by API) |
| POST | `/practice/{dataset_id}/{exercise_id}/submit` | **Removed** |
| POST | `/practice/progress/clear` | **Removed** or redirect to API from form in workspace |

Query params on workspace path: `?difficulty=Beginner&mode=Timed` (dataset implied by path segment).

### Redirect rules

- `GET /` → `303` → `/practice`.
- `GET /practice` → `303` → `/practice/{dataset}/{exercise}` using `find_continue_exercise` when progress exists, else first catalog exercise matching optional query filters.
- `GET /practice/interview/...` → `303` → `/practice` (or first exercise) until interview package deleted.

### API JSON shapes (v1)

**Run success (200):**

```json
{
  "columns": ["headline_main"],
  "rows": [["Example"]],
  "row_count": 1,
  "truncated": false
}
```

**Run error (400/422):**

```json
{ "error": { "message": "...", "code": "validation_error" } }
```

**Submit success (200):**

```json
{
  "grading": {
    "passed": true,
    "status": "passed",
    "summary": "...",
    "is_placeholder": false
  },
  "progress": { "passed_count": 12, "total": 50 }
}
```

Progress cookie attached via `Set-Cookie` on submit response (reuse `attach_progress_cookie`).

**Exercise payload (200):**

```json
{
  "exercise": { "id", "title", "prompt", "hint", "difficulty", "mode", ... },
  "dataset": { "id", "name" },
  "schema": { "tables": [{ "name", "columns": [{ "name", "type", "description" }] }] },
  "attempt": { "sql", "query_result", "execution_error", "grading" },
  "progress": { "status", "label", "best_elapsed" },
  "navigation": { "index": 11, "total": 50, "prev_url", "next_url" }
}
```

### Client architecture

- **Vanilla ES module** `static/js/practice-workspace.js` (no new bundler; CodeMirror stays on existing bundle).
- **Initial load:** SSR workspace template embeds config JSON (`#workspace-config`) for first exercise.
- **In-place switch:** `fetch` exercise API → patch left panel, editor, console, footer nav → `history.pushState` to canonical path.
- **Filters:** changing filter controls navigates with `window.location` to new path + query (full load acceptable; filters are infrequent).
- **Run/submit:** `fetch` only; no `location` change.
- **Grading:** modal overlay (`role="dialog"`), focus trap, **OK** dismisses, focus returns to Submit; switching exercise dismisses open modal.
- **Console restore:** render `attempt.query_result` or `execution_error` from API on load/switch; run output not duplicated in session beyond existing `practice_attempts` slimming.

### Schema fixture

- New file: `src/app/catalog/data/times_archive_schema.json`
- Columns derived from `docker/postgres/init/01-schema.sql` with short **description** strings per column (hand-authored in PR).
- Loader: `src/app/catalog/schema.py` — `get_dataset_schema(dataset_id) -> SchemaDocument`.
- No live `INFORMATION_SCHEMA` queries in v1.

### Session and progress

- Reuse `practice_session.py` (`store_run_result`, `store_submit_result`, `slim_practice_attempts`).
- Grading stored in session for restore metadata; **modal not auto-shown** on exercise switch (badges reflect pass/attempt).
- Phase 4.1 session slimming retained.

### Templates (target)

| Keep / create | Remove |
|---------------|--------|
| `templates/workspace.html` | `templates/practice.html` |
| `templates/base.html` | `templates/practice_exercise.html` |
| `templates/404.html` | `templates/interview_*.html` |
| `templates/index.html` → redirect only or delete in favor of `/` redirect | |

`index.html` may become unnecessary if `/` redirects in `main.py`; remove home template content in docs milestone.

### Non-goals (explicit)

- Accounts, AI grading, WebSockets, mobile-first layout, interview queues, catalog card grid, htmx, live schema introspection.

---

## Milestones

### 1. TIM-57 — Schema fixture and workspace context helpers

**Goal:** Checked-in schema with descriptions and server helpers for workspace left panel.

**Files to create or modify:**

- `src/app/catalog/data/times_archive_schema.json` — `times_archive` columns (name, type, description).
- `src/app/catalog/schema.py` — load schema by `dataset_id`.
- `src/app/workspace/context.py` _(new)_ — `get_workspace_context(request, dataset_id, exercise_id, filters)` assembling exercise, schema, attempt, progress, navigation.
- `src/app/workspace/navigation.py` _(new)_ — filtered exercise list, prev/next URLs, position index (extend `progress/navigation.py` patterns; include `mode` filter).
- `tests/test_workspace_schema.py` _(new)_
- `tests/test_workspace_navigation.py` _(new)_

**Implementation notes:**

- Navigation uses stable catalog tuple order; filters match `PracticeFilters` semantics today.
- `get_workspace_context` calls `get_attempt_state`, `lookup_exercise`, `load_progress`.

**Acceptance criteria covered:** R3 (partial), R6/R7 (server-side nav data).

**Checks:** `uv run pytest tests/test_workspace_*.py`, ruff, mypy.

**Risks:** Descriptions are hand-written; keep concise.

---

### 2. TIM-58 — JSON API (run, submit, exercise, list)

**Goal:** Backend APIs consumed by workspace client; no UI change yet.

**Files to create or modify:**

- `src/app/api/__init__.py`, `src/app/api/practice.py` — route handlers or register in `main.py` under `/api/practice/...`.
- `src/app/main.py` — mount API routes; Pydantic request/response models or typed dicts.
- Reuse `execute_query`, `store_run_result`, `store_submit_result`, `load_progress`, `attach_progress_cookie`.
- `tests/test_practice_api.py` _(new)_ — run happy/error, submit pass/fail + cookie, exercise payload, exercise list filters.

**Implementation notes:**

- Submit API returns JSON body **and** `Set-Cookie` for progress (mirror `_redirect_with_progress` behavior).
- Run/submit accept `Content-Type: application/json`.
- CSRF: same-origin `fetch` with session cookie only (no separate CSRF token in v1).
- Errors: 404 for unknown exercise; 422 for validation.

**Acceptance criteria covered:** R2 (API), R4 (API), R9 (partial).

**Checks:** `uv run pytest tests/test_practice_api.py`, ruff, mypy.

**Risks:** Medium — ensure submit progress cookie path tested without redirect.

---

### 3. TIM-59 — Workspace shell template, routes, and layout CSS

**Goal:** Single workspace page replaces catalog grid and per-exercise template on GET.

**Files to create or modify:**

- `templates/workspace.html` — top filters, left panel placeholders, editor host, console host, drawer, footer nav, modal skeleton (hidden).
- `static/styles.css` — `.workspace-*` grid layout; remove or deprecate `.interview-*` later.
- `src/app/main.py` — `GET /` → `/practice`; `GET /practice` → first exercise; `GET /practice/{dataset}/{exercise}` → `workspace.html`.
- `static/js/practice-workspace-entry.js` — minimal boot (load module).
- Remove render path for `practice.html` / `practice_exercise.html` on GET (delete templates in TIM-63).

**Implementation notes:**

- SSR renders full left panel (schema, prompt, hint, objectives, sample SQL `<details>`).
- Embed `workspace-config` JSON for initial `dataset_id`, `exercise_id`, filter query params.
- Console and modal empty until client wired (TIM-60–61).

**Acceptance criteria covered:** R1 (partial), R3 (render), left panel content (R3, sample SQL, objectives).

**Checks:** route tests assert workspace template; no card grid in response.

**Risks:** Large template — keep logic in context helper, not Jinja.

---

### 4. TIM-60 — Client: editor, Run SQL, output console

**Goal:** Run SQL without document reload.

**Files to create or modify:**

- `static/js/practice-workspace.js` — editor init (reuse `initPracticeEditor`), run `fetch`, render console table/error, sync SQL to session via run API side effect.
- `templates/workspace.html` — wire Run button, console region, `noscript` fallback message.
- `tests/test_practice_api.py` — extend if needed.
- Optional: `tests/test_workspace_browser.py` with Playwright — assert no navigation on run.

**Implementation notes:**

- Disable Run while request in flight.
- Console shows truncated row note when `truncated: true`.
- Preserve editor on run (no form submit).

**Acceptance criteria covered:** R2 (UI), phase AC run without reload.

**Checks:** pytest + manual smoke; Playwright optional.

**Risks:** CodeMirror sync — sync hidden field or read from editor view on run.

---

### 5. TIM-61 — Client: submit modal, timer, progress refresh

**Goal:** Submit shows dismissible pass/fail notification; timed mode works in workspace.

**Files to create or modify:**

- `static/js/practice-workspace.js` — submit `fetch`, modal show/hide, OK handler, drawer badge refresh from response `progress`.
- `static/js/practice-timer.js` — adapt to call submit API instead of form POST (or thin adapter in workspace).
- `templates/workspace.html` — modal markup (`role="dialog"`, `aria-modal`, focus trap).
- `static/styles.css` — modal styles.

**Implementation notes:**

- Timeout submit uses same submit API path.
- Dismiss modal on exercise switch (TIM-62).
- Do not auto-open modal on exercise restore.
- Keyboard: OK button and Escape dismiss.

**Acceptance criteria covered:** R4 (all), R10 (all), R9 (clear progress wired to API).

**Checks:** `tests/test_practice_api.py` submit cookie; timer unit/manual for timed exercise.

**Risks:** Double submit guard from Phase 3 retained.

---

### 6. TIM-62 — Drawer, filters, Previous / Next (in-place)

**Goal:** Exercise switching without full document reload.

**Files to create or modify:**

- `static/js/practice-workspace.js` — drawer toggle, list render from `/api/practice/exercises`, selection handler, prev/next handlers, `pushState` + `popstate`.
- `src/app/api/practice.py` — ensure list endpoint returns badge fields.
- `templates/workspace.html` — drawer panel, footer buttons.

**Implementation notes:**

- Selection: `fetch` exercise API → update DOM regions → `pushState` canonical path (preserve filter query string).
- Restore attempt console + editor SQL from API `attempt` payload.
- Filters: `<select>` change sets `window.location` to recalculated first eligible exercise URL (simpler than client-side filter recompute).
- If current exercise outside new filter, server redirect on full navigation (R6).

**Acceptance criteria covered:** R5, R6, R7, session restore.

**Checks:** API tests + Playwright flow: open drawer, switch exercise, prev/next without `performance.navigation.type === reload` between switches.

**Risks:** Medium complexity — largest client milestone; keep PR focused on navigation only.

---

### 7. TIM-63 — Remove interview mode and legacy practice pages

**Goal:** Delete Phase 4 interview product surface and form-POST run/submit routes.

**Files to create or modify:**

- **Delete:** `src/app/interview/`, `templates/interview_*.html`, `templates/practice.html`, `templates/practice_exercise.html`.
- `src/app/main.py` — remove interview routes and form POST run/submit; interview URLs redirect to `/practice`.
- `src/app/practice.py` — remove `get_practice_context` card grid, `interview_resume_context` usage.
- `tests/` — delete `test_interview_*.py`; update `test_app.py`, `test_developer_workflow.py`.
- `static/styles.css` — remove unused `.interview-*` rules.
- `scripts/record_phase4_demo.py`, `scripts/debug_interview_start.py`, `scripts/validate_phase41_fixes.py` — delete or archive.

**Acceptance criteria covered:** R8, R1 (legacy removal), phase AC no interview/catalog.

**Checks:** full `uv run pytest`, grep for `interview_session` / `interview/start` in src/templates.

**Risks:** Large deletion PR — run after workspace is functional (TIM-59–62 merged).

---

### 8. TIM-64 — Docs, manual test plan, validation, PRD closeout

**Goal:** Document Phase 5; update repo gates.

**Files to create or modify:**

- `README.md` — workspace console model; remove interview/catalog references.
- `docs/phase-5-manual-test-plan.md` _(new)_
- `docs/session-state.md` — API + workspace; remove interview session.
- `docs/progress.md` — cross-links.
- `tests/test_developer_workflow.py` — Phase 5 assertions.
- `scripts/validate-env.sh` — phase banner.
- `prd/README.md` — mark Phase 5 complete after ship.
- `prd/phase-5-console-workspace.md` — status → Complete.

**Acceptance criteria covered:** R11, all phase-level AC checklist.

**Checks:** `./scripts/validate-env.sh`, full pytest, ruff, mypy.

**Risks:** None significant.

---

## Requirement coverage

| PRD requirement | Milestone(s) |
|-----------------|--------------|
| R1. Workspace route and URL shape | TIM-59, TIM-63 |
| R2. Console run (no reload) | TIM-58, TIM-60 |
| R3. Schema panel | TIM-57, TIM-59 |
| R4. Submit grading notification | TIM-58, TIM-61 |
| R5. Exercise drawer and in-place switch | TIM-62 |
| R6. Filters | TIM-57, TIM-59, TIM-62 |
| R7. Previous / Next | TIM-57, TIM-62 |
| R8. Remove interview | TIM-63 |
| R9. Progress and session | TIM-58, TIM-61, TIM-62 |
| R10. Timed mode | TIM-61 |
| R11. Docs and validation | TIM-64 |

## Out of scope (explicit)

- Accounts, OAuth, server-side learner DB, AI grading.
- Mobile-first responsive design.
- WebSockets, query history tabs, htmx.
- Live Postgres schema introspection.
- Re-introducing interview or catalog card grid.
- `index.html` marketing content (home is redirect-only).

## Engineering principles check

| Principle | Assessment |
|-----------|------------|
| Minimal scope per PR | Eight milestones; delete interview only after workspace works. |
| Design fit | APIs beside existing execution/grading; workspace context module mirrors `interview/views` pattern without session queue. |
| Simplicity | Vanilla `fetch`; SSR shell + client patch for switches; filters use full navigation. |
| DRY | Reuse `practice_session`, `execute_query`, `grade`, progress cookie helpers. |
| Tests | API tests per endpoint; navigation unit tests; optional Playwright for no-reload. |
| Small CLs | TIM-62 is largest client PR; TIM-63 is delete-heavy but mechanical. |

**Non-blocking trade-offs:**

- Filter changes use full page load; acceptable per planning decision.
- Grading modal not re-shown on exercise switch (badges + session store suffice).
- `/practice` bare path always redirects (no workspace without exercise id).
- Optional Playwright tests may be deferred within TIM-60/62 if API tests are strong.

## Suggested implementation order

```text
TIM-57 → TIM-58 → TIM-59 → TIM-60 → TIM-61 → TIM-62 → TIM-63 → TIM-64
```

TIM-58 can start in parallel with TIM-57 after schema types are defined; TIM-59 depends on TIM-57 context helpers.

## Approval

- [x] User approves this implementation plan.
- [x] Create Linear epic **TIM-56** and child issues **TIM-57**–**TIM-64**.
- [x] Application code merged via autonomous phase run.
