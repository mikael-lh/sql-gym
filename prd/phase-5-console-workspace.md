# Phase 5 console workspace PRD

## Status

**Draft for review** — open questions resolved (2026-06-09). Not an active implementation phase until you explicitly approve scope and an `implement-from-prd` plan.

## Source context

Follows `prd/00-product-vision.md`. Supersedes the Phase 4 catalog + interview navigation model.

**Today:** `/practice` card grid; per-exercise pages with form POST run/submit (full reload); `/practice/interview/...` queues; CodeMirror + progress cookie + timed mode.

**Direction:** One workspace — filters on top; schema/prompt/hint/objectives left; editor + console right; exercise drawer with badges; prev/next; no interview mode; no card grid.

## Problem

Run/submit reload the whole page. Practice is split across catalog, exercise, and interview routes. Interview queues duplicate what prev/next + filters already provide.

## Goals

- Single practice workspace as the main surface.
- Run SQL updates the output console without navigation.
- Submit shows a **dismissible pass/fail notification** (not a full grading panel).
- Remove catalog cards and interview session product surface (routes + UI + state).
- Keep execution, strict grading, progress cookie, timed mode, draft SQL.

## Non-goals

Accounts; AI grading; new datasets; mobile-first; WebSockets; interview queues under another name.

## Resolved product decisions (2026-06-09)

| Topic | Decision |
|-------|----------|
| **Home** | `/` redirects straight to `/practice`. |
| **Grading UX** | Temporary notification (modal/toast) with pass/fail status and summary; user clicks **OK** to dismiss, then may retry or switch exercises. No persistent grading panel in the console. |
| **Exercise switch** | Restore that exercise's last run output and last grading outcome from session when available. |
| **Schema panel** | Column names, types, and descriptions when available in the schema fixture. |
| **Sample SQL** | Keep collapsible `<details>` on the left panel. |
| **Learning objectives** | Show on the left panel. |
| **Canonical URL** | Path-style `/practice/{dataset_id}/{exercise_id}`; filters via query params on the same route (e.g. `?difficulty=Beginner&mode=Timed`). |
| **Client stack** | `fetch` + JSON APIs under `/api/practice/...`. |

## Layout

| Region | Content |
|--------|---------|
| **Top** | Dataset, difficulty, mode filters; exercise title; progress summary; clear progress |
| **Left** | Schema (name, type, description); prompt; hint; learning objectives; collapsible sample SQL |
| **Right top** | Editor, Run SQL, Submit for grading, timer if Timed |
| **Right bottom** | Output console (query results and execution errors only) |
| **Drawer** | Toggle exercise list with Not started / Attempted / Passed badges |
| **Footer** | Previous / Next in filtered catalog order |
| **Grading** | Overlay notification on submit (pass/fail + summary); OK dismisses |

```text
┌─────────────────────────────────────────────────────────────┐
│ Filters   [Exercise list ▤]                    12 / 50 passed│
├──────────────────────┬──────────────────────────────────────┤
│ Schema               │  SQL editor                          │
│ Prompt               │  [Run SQL]  [Submit]                 │
│ Hint                 ├──────────────────────────────────────┤
│ Objectives           │  Output console (results / errors)     │
│ ▸ Sample SQL         │                                      │
├──────────────────────┴──────────────────────────────────────┤
│  ◀ Previous                         Next ▶                  │
└─────────────────────────────────────────────────────────────┘
        ┌─────────────────────────┐
        │  Passed / Not passed    │  ← modal on submit
        │  [summary text]   [OK]  │
        └─────────────────────────┘
```

## Requirements

### R1. Workspace route and URL shape

- `GET /` redirects to `GET /practice` (first eligible exercise or last visited per implementation plan).
- **Canonical exercise URL:** `GET /practice/{dataset_id}/{exercise_id}` renders the workspace with that exercise active (not a separate template page).
- Optional query params on the same path: `dataset` filter is implicit in path; `difficulty`, `mode` for filter state.
- Legacy standalone exercise template flow is removed; path URLs load the workspace shell.
- Catalog card grid removed from all surfaces.

Acceptance criteria:

- Visiting `/` yields a redirect to `/practice/...`.
- Bookmarking `/practice/times-archive/times-archive-014` opens the workspace on that exercise.
- No full-page catalog card grid remains.

### R2. Console run (no reload)

- `POST /api/practice/{dataset_id}/{exercise_id}/run` with JSON `{ "sql": "..." }`.
- Response: result grid JSON or structured execution error.
- UI updates the output console in place; editor focus and content preserved.
- SELECT-only validation and execution limits unchanged.
- Last run stored in session for restore on exercise switch (R5).

Acceptance criteria:

- Run does not change `window.location` (except initial load).
- Automated API + browser tests cover happy path and validation errors.

### R3. Schema panel

- Left panel lists tables/columns for the active dataset from a **checked-in schema fixture** (not live `INFORMATION_SCHEMA` in v1).
- Each column shows **name**, **type**, and **description** when the fixture provides one.
- Updates when the active dataset changes.

### R4. Submit and grading notification

- `POST /api/practice/{dataset_id}/{exercise_id}/submit` with JSON `{ "sql": "...", "elapsed_seconds": optional }`.
- Response includes grading payload (`passed`, `summary`, `status`, etc.).
- UI shows a **temporary notification** (modal or equivalent) with pass/fail and summary text.
- **OK** dismisses the notification; console and editor remain visible underneath.
- Progress cookie updates per Phase 3 rules; drawer badges refresh without navigation.
- Timed timeout auto-submit uses the same API and notification pattern.
- Last grading outcome stored in session for restore on exercise switch (R5).

Acceptance criteria:

- Submit does not reload the page.
- Notification is keyboard-accessible (focus trap or focus return on dismiss).
- Progress cookie updates on pass/attempt in tests.

### R5. Exercise drawer and in-place switching

- Toggle opens filtered exercise list with progress badges.
- Selecting an exercise updates URL to canonical path (`/practice/{dataset}/{exercise}`) via `history.pushState` or navigation that does not reload the workspace shell (SPA-style shell load once, or full navigation acceptable only if shell is the same document — prefer no full reload).
- On switch: restore draft SQL, last run console output, and last grading state from session when present.

### R6. Filters

- Dataset, difficulty, mode — same semantics as Phase 1–4 catalog filters.
- Applying filters updates eligible set, drawer, and prev/next sequence.
- If active exercise falls outside filter, navigate to first eligible in catalog order.
- Filter state in URL query params; exercise identity in path.

### R7. Previous / Next

- Move within filtered catalog order; disabled at ends.
- Position label (e.g. `Exercise 12 of 50` filtered count).
- Same restore behavior as drawer selection (R5).

### R8. Remove interview session product surface

- Remove interview UI, routes under `/practice/interview/...`, `interview_session` state, related templates, tests, and docs references.
- Old interview URLs redirect to `/practice` (or first exercise).

### R9. Progress and session

- `sql_gym_progress` cookie unchanged.
- **Clear my progress** in workspace chrome.
- Session holds per-exercise: `sql`, last `query_result` preview, last `grading`, `execution_error` (bounded previews per Phase 4 rules).

### R10. Timed mode

- Timer in editor toolbar when `mode == Timed`.
- Phase 3 start, countdown, timeout submit behavior.

### R11. Docs and validation

- README describes workspace model.
- `docs/phase-5-manual-test-plan.md` added.
- `docs/session-state.md` updated for workspace + API model.
- `./scripts/validate-env.sh` and pytest green.

## Phase acceptance criteria

- [ ] `/` redirects to practice workspace; path-style exercise URLs work.
- [ ] No catalog card grid or interview UI.
- [ ] Run updates console without full page reload.
- [ ] Submit shows dismissible pass/fail notification; progress updates.
- [ ] Left panel: schema (with descriptions), prompt, hint, objectives, collapsible sample SQL.
- [ ] Drawer and prev/next switch exercises in place with session restore.
- [ ] Interview code removed; legacy behavior documented.

## Edge cases

| Case | Behavior |
|------|----------|
| Submit while notification open | Queue or replace per implementation plan; no double progress write |
| Switch exercise while notification open | Dismiss notification; load selected exercise state |
| No exercises match filters | Empty drawer; disabled editor; guidance copy |
| Session too large | Retain Phase 4.1 slimming; console holds transient run client-side where possible |
| Removed interview URL | Redirect to `/practice` |

## Success signals

- Iterative run loop without document reload.
- Grading feedback is lightweight (notification) but trustworthy.
- Route and template surface area shrinks after interview removal.

## Approval needed

- [ ] Approve PRD scope (product decisions above are locked).
- [ ] Name Phase 5 **active** in `prd/README.md` when ready for `implement-from-prd`.
- [ ] Approve implementation plan from `implement-from-prd` before application code.

## References

- `prd/00-product-vision.md`
- `prd/phase-4-interview-sessions-and-polish.md`
- `docs/session-state.md`, `docs/progress.md`
- `src/app/main.py`, `templates/practice_exercise.html`
