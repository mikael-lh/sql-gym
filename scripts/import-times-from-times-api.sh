#!/usr/bin/env bash
# Download Times Archive slim NDJSON from GCS and load into PostgreSQL.
# Run from repo root after `docker compose up -d` and Postgres is healthy.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

: "${GCS_BUCKET:=ny-archive-bucket}"
: "${GCS_PREFIX:=nyt-ingest/archive_slim}"
export GCS_BUCKET GCS_PREFIX

if [[ -z "${DATABASE_ADMIN_URL:-}" && -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: Set DATABASE_ADMIN_URL (recommended) or DATABASE_URL." >&2
  exit 1
fi

echo "=== Times Archive import ==="
echo "Source: gs://${GCS_BUCKET}/${GCS_PREFIX}/"
echo "Target: ${DATABASE_ADMIN_URL:-$DATABASE_URL}"
echo

uv run python scripts/import_times_from_gcs.py
