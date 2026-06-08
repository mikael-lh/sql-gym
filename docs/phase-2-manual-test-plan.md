# Phase 2 manual test plan

End-to-end checklist for SQL execution and strict grid-match grading.

## Prerequisites

1. Copy `.env.example` to `.env` and set `DATABASE_URL` / `DATABASE_ADMIN_URL`.
2. `docker compose up -d` and wait for Postgres health.
3. `./scripts/import-times-from-times-api.sh` (requires GCS credentials).
4. `uv sync` and `uv run uvicorn app.main:app --reload`.

## Smoke path

| Step | Action | Expected |
|------|--------|----------|
| 1 | Open `/` | Home mentions Phase 2 practice and links to `/practice`. |
| 2 | Open `/practice` | 50 exercises listed; copy mentions run/grade on previews. |
| 3 | Open `/practice/times-archive/times-archive-003` | CodeMirror editor, Run SQL, Submit for grading. |
| 4 | Run `SELECT section_name, COUNT(*) AS article_count FROM times_archive GROUP BY section_name ORDER BY article_count DESC LIMIT 5;` | Result table with ≤5 rows. |
| 5 | Submit the same SQL | Pass or fail feedback appears (strict grid match). |
| 6 | Submit intentionally wrong SQL (e.g. `SELECT 1`) | Fail summary without answer leakage. |
| 7 | Refresh page | Session attempt state persists for this browser session. |
| 8 | Open a new private window | Previous attempt not visible (session-only). |

## Failure cases

| Case | SQL | Expected message theme |
|------|-----|------------------------|
| Empty | whitespace | Enter a SQL query |
| DML | `DELETE FROM times_archive` | Only SELECT queries |
| DB down | any SELECT | Database is not configured / connection error |

## Docs references

- [times-data-setup.md](times-data-setup.md)
- [grading.md](grading.md)
