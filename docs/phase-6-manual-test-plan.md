# Phase 6 manual test plan

Reliability and code-quality checks for [prd/phase-6-reliability-and-code-quality.md](../prd/phase-6-reliability-and-code-quality.md). Learner-facing flows should match Phase 5; this plan focuses on the reliability fixes and config guards.

## Prerequisites

- `./scripts/dev.sh` or equivalent: Postgres up, Times data imported, `uv run uvicorn app.main:app --reload`
- Browser with JavaScript enabled

## 1. Run / submit happy path

1. Open `/practice` → land on a workspace exercise.
2. Confirm the **Elapsed** stopwatch ticks (`M:SS`).
3. Enter a valid `SELECT` for the exercise and click **Run SQL**.
4. Confirm the output console shows a result grid (or a clear execution error).
5. Click **Submit for grading**.
6. Confirm the grading modal appears; on a pass, progress badge updates and first-pass solve time is shown.

## 2. R2 false-rejection fix (string keywords / semicolons)

These must **run**, not be rejected as writes:

1. Run a query with a banned keyword inside a string literal, e.g.  
   `SELECT 'drop table' AS note;`  
   Expect rows (or a normal SQL error), not a read-only / banned-keyword rejection.
2. Run a query with a semicolon inside a string, e.g.  
   `SELECT 'a;b' AS note;`  
   Expect the same — no false rejection from client-side statement splitting.

Optional negative check:

3. Attempt a write such as `UPDATE times_archive SET headline_main = 'x' WHERE false;`  
   Expect rejection (read-only transaction / execution error), not a successful write.

## 3. Progress tracking

1. Pass an exercise; confirm badge **Passed** and “solved in `M:SS`”.
2. Switch exercises via drawer or prev/next; draft SQL / console restore still work.
3. **Clear progress** → badges reset to Not started; passed count returns to 0.

## 4. Production session-secret hard-fail

With the app stopped, start uvicorn **with** `APP_ENV=production` and no usable secret:

```bash
env -u SESSION_SECRET APP_ENV=production \
  uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Or with a blank secret:

```bash
APP_ENV=production SESSION_SECRET='   ' \
  uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Expect startup to **fail fast** (missing/blank `SESSION_SECRET` in production).

Development check (optional):

```bash
# APP_ENV unset or development; SESSION_SECRET unset → app starts with the committed dev fallback
env -u SESSION_SECRET APP_ENV=development \
  uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 5. Smoke after JS module split

1. Hard-refresh the workspace; confirm `document.documentElement.dataset.workspaceReady === "submit"` in the console.
2. Run, submit, open the exercise drawer, use prev/next, and dismiss the grading modal — same as Phase 5.

## Automated coverage

Prefer `./scripts/validate-env.sh` and `uv run pytest` for regression. Browser layout suites cover top navigation at desktop and mobile viewports.
