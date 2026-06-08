# Times Archive data setup

Phase 2 loads real Times Archive article rows from the private `times-api` GCS export into local PostgreSQL for SQL practice.

## Source

| Item | Value |
|------|-------|
| Bucket | `ny-archive-bucket` |
| Prefix | `nyt-ingest/archive_slim/` |
| Object pattern | `YYYY/MM.ndjson` (1920–2019) |
| Schema | [`times-api/schema/archive_articles.json`](https://github.com/mikael-lh/times-api/blob/main/schema/archive_articles.json) |
| Postgres table | `times_archive` |

## Content pin

Validated against GCS listing on **2026-06-08** using service account `cursor-agent@times-api-ingest.iam.gserviceaccount.com`. Sample objects:

- `nyt-ingest/archive_slim/1920/01.ndjson`
- `nyt-ingest/archive_slim/1920/02.ndjson`

Update this pin deliberately when the slim export is refreshed.

## Prerequisites

1. Docker with Compose v2.
2. GCP credentials with `storage.objectViewer` on `ny-archive-bucket` / `nyt-ingest/`.
3. Python deps synced: `uv sync`.

### GCP credentials

Choose one:

| Method | Setup |
|--------|-------|
| Service account file | Set `GOOGLE_APPLICATION_CREDENTIALS` to a JSON key path (see `.env.example`). |
| Application Default Credentials | `gcloud auth application-default login` on a machine with bucket access. |
| Cursor Cloud secret | Inject **GCS View SA** in Cloud Agent settings; `scripts/import-times-from-times-api.sh` reads it automatically. |

Contributors without bucket access cannot import (by design). CI skips DB integration tests when `DATABASE_URL` is unset.

## Quick start

```bash
cp .env.example .env
# Edit .env if needed (defaults match docker-compose).

docker compose up -d
docker compose ps   # wait until postgres is healthy

./scripts/import-times-from-times-api.sh
```

Verify row count:

```bash
psql "$DATABASE_ADMIN_URL" -c "SELECT COUNT(*) FROM times_archive;"
```

## Environment variables

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Learner read-only URL (`sql_gym_readonly`) for the app. |
| `DATABASE_ADMIN_URL` | Admin URL for import (`sqlgym` superuser from Compose). |
| `GCS_BUCKET` | GCS bucket name (default `ny-archive-bucket`). |
| `GCS_PREFIX` | Object prefix (default `nyt-ingest/archive_slim`). |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account JSON (optional with ADC or Cloud secret). |

## Import behavior

- Downloads all `*.ndjson` objects under the configured prefix.
- `TRUNCATE times_archive` then reload (idempotent full refresh).
- Skips malformed NDJSON lines with a warning (continues import).
- Batch inserts via `psycopg`; JSON array/object columns stored as `JSONB`.

## Expected result grids

After import, regenerate grading grids:

```bash
./scripts/generate-expected-results.sh
```

Writes `src/app/catalog/data/expected_grids/<exercise_id>.json` from each exercise's `reference_sql` (max 500 rows).

First import may take several minutes depending on network speed (full 1920–2019 archive).

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `connection refused` on port 5432 | Run `docker compose up -d` and wait for healthcheck. |
| GCS permission denied | Confirm service account has `storage.objectViewer` on the bucket. |
| `No objects found under gs://…` | Check `GCS_BUCKET` / `GCS_PREFIX`; verify credentials can list the prefix. |
| Import slow | Expected on first run; subsequent runs still re-download all objects. |

## Roles

Docker init creates:

- `sql_gym_readonly` — `SELECT` on `times_archive` (learner queries in Phase 2).
- `sql_gym_app` — `SELECT` on `times_archive` (reserved for app wiring).

Import uses `DATABASE_ADMIN_URL` (Compose superuser).
