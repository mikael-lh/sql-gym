#!/usr/bin/env bash
# Regenerate committed expected-result grids from reference_sql against imported data.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [[ -z "${DATABASE_ADMIN_URL:-}" && -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: Set DATABASE_ADMIN_URL (recommended) or DATABASE_URL." >&2
  echo "Start Docker Postgres and run ./scripts/import-times-from-times-api.sh first." >&2
  exit 1
fi

echo "=== Generate expected result grids ==="
uv run python scripts/generate_expected_results.py
