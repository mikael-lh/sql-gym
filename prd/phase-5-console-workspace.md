# Phase 5 console workspace PRD

## Status

**Draft for review** — not an active implementation phase until you approve this PRD and an `implement-from-prd` plan.

## Source context

Follows `prd/00-product-vision.md`. Supersedes the Phase 4 catalog + interview navigation model.

**Today:** `/practice` card grid; per-exercise pages with form POST run/submit (full reload); `/practice/interview/...` queues; CodeMirror + progress cookie + timed mode.

**Your direction:** One workspace — filters on top; schema/prompt/hint left; editor + console right; exercise drawer with badges; prev/next; no interview mode; no card grid.

## Problem

Run/submit reload the whole page. Practice is split across catalog, exercise, and interview routes. Interview queues duplicate what prev/next + filters already provide.

## Goals

- Single `/practice` workspace as the main surface.
- Run SQL updates console without navigation; submit shows grading inline.
- Remove catalog cards and interview session product surface (routes + UI + state).
- Keep execution, strict grading, progress cookie, timed mode, draft SQL.

## Non-goals

Accounts; AI grading; new datasets; mobile-first; WebSockets; interview queues under another name.

## Layout

| Region | Content |
|--------|---------|
| Top | Dataset, difficulty, mode filters; title; progress; clear progress |
| Left | Schema, prompt, hint (optional sample SQL) |
| Right top | Editor, Run, Submit, timer if Timed |
| Right bottom | Output console (results, errors, grading) |
| Drawer | Toggle exercise list with Not started / Attempted / Passed |
| Footer | Previous / Next in filtered catalog order |

## Requirements

### R1. Workspace route

- `GET /practice` renders shell. `/` redirects to `/practice` (default).
- `/practice/{dataset}/{exercise}` redirects into workspace with exercise selected.
- Card grid removed.

### R2. Console run (no reload)

- `POST /api/practice/{dataset}/{exercise}/run` JSON `{sql}` → grid or error.
- UI updates console in place; editor preserved; SELECT-only rules unchanged.

### R3. Schema panel

- Static `times_archive` column names + types from checked-in fixture (not live INFORMATION_SCHEMA v1).

### R4. Inline submit

- `POST /api/practice/.../submit` → grading JSON; progress cookie updates; timed timeout uses same API.

### R5. Exercise drawer

- Filtered list with progress badges; select loads exercise via fetch, not document navigation.

### R6. Filters

- Same dataset/difficulty/mode semantics; URL query params for filters + active exercise.

### R7. Prev / Next

- Filtered catalog order; disabled at ends; position label (e.g. 12 of 50).

### R8. Remove interview

- Delete interview routes, UI, `interview_session`, related code/tests/docs.

### R9. Progress

- Keep `sql_gym_progress` cookie and clear-progress; sync drawer badges after submit.

### R10. Timed mode

- Timer in toolbar; Phase 3 start/countdown/timeout behavior.

### R11. Docs

- README, `docs/phase-5-manual-test-plan.md`, green validate-env/pytest.

## Phase acceptance criteria

- [ ] Workspace only; no card grid or interview UI.
- [ ] Run/submit without full page reload.
- [ ] Schema left; editor + console right; drawer + prev/next.
- [ ] Legacy URLs redirect; tests documented.

## Open questions

1. Home: redirect `/` → `/practice` or minimal landing?
2. Grading: replace run output vs separate tabs?
3. On exercise switch: clear console vs restore last run/grade?
4. Schema: names/types only or richer?
5. Keep sample SQL collapsible on left?
6. Show learning objectives or drop?
7. Canonical URL: `?exercise=` vs path?
8. `fetch`+JSON (recommended) vs htmx?

## Approval needed

- [ ] Approve scope.
- [ ] Answer open questions (or defer defaults to implementation plan).
- [ ] Name Phase 5 active in `prd/README.md` when ready to implement.
