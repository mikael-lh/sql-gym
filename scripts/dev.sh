#!/usr/bin/env bash
# One-command local setup for sql-gym:
# git pull, env file, deps, Postgres, Times data (if needed), dev server, browser.
#
# Usage (from repo root):
#   ./scripts/dev.sh
#
# Options:
#   --skip-pull     Skip `git pull --ff-only origin main`
#   --skip-import   Skip Times Archive import even when the table is empty
#   --force-import  Re-import Times Archive data from GCS
#   --no-open       Start the server but do not open a browser tab
#   -h, --help      Show this help
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"
URL="http://${HOST}:${PORT}/practice"

SKIP_GIT_PULL=0
SKIP_IMPORT=0
FORCE_IMPORT=0
OPEN_BROWSER=1

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-pull)
      SKIP_GIT_PULL=1
      ;;
    --skip-import)
      SKIP_IMPORT=1
      ;;
    --force-import)
      FORCE_IMPORT=1
      ;;
    --no-open)
      OPEN_BROWSER=0
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: '$1' is required but not installed." >&2
    exit 1
  fi
}

load_env() {
  if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
  fi
}

open_browser() {
  if [[ "$OPEN_BROWSER" != 1 ]]; then
    return 0
  fi
  if command -v open >/dev/null 2>&1; then
    open "$URL"
  elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL"
  else
    echo "Open $URL in your browser."
  fi
}

wait_for_server() {
  local deadline=$((SECONDS + 45))
  while (( SECONDS < deadline )); do
    if curl -fsS "$URL" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  echo "Timed out waiting for $URL" >&2
  return 1
}

wait_for_postgres() {
  local deadline=$((SECONDS + 90))
  until docker compose exec -T postgres pg_isready -U sqlgym -d sqlgym >/dev/null 2>&1; do
    if (( SECONDS >= deadline )); then
      echo "ERROR: Postgres did not become ready in time." >&2
      echo "Try: docker compose ps && docker compose logs postgres" >&2
      exit 1
    fi
    sleep 1
  done
}

times_archive_row_count() {
  docker compose exec -T postgres psql -U sqlgym -d sqlgym -tAc \
    "SELECT COUNT(*) FROM times_archive;" 2>/dev/null | tr -d '[:space:]'
}

echo "=== sql-gym dev setup ==="

require_command git
require_command uv
require_command docker
require_command curl

if [[ "$SKIP_GIT_PULL" -eq 0 ]]; then
  echo "==> Updating from git (origin/main)..."
  git pull --ff-only origin main
fi

if [[ ! -f .env ]]; then
  echo "==> Creating .env from .env.example..."
  cp .env.example .env
fi

load_env

echo "==> Installing Python dependencies..."
uv sync --locked

echo "==> Starting Postgres (Docker)..."
docker compose up -d

echo "==> Waiting for Postgres..."
wait_for_postgres

row_count="$(times_archive_row_count || echo 0)"
if [[ -z "$row_count" ]]; then
  row_count=0
fi

if [[ "$FORCE_IMPORT" -eq 1 ]]; then
  echo "==> Re-importing Times Archive data from GCS..."
  ./scripts/import-times-from-times-api.sh
elif [[ "$SKIP_IMPORT" -eq 0 && "$row_count" -eq 0 ]]; then
  echo "==> Times Archive table is empty — importing from GCS (first run; may take several minutes)..."
  if ./scripts/import-times-from-times-api.sh; then
    row_count="$(times_archive_row_count || echo 0)"
    echo "==> Import complete ($row_count rows)."
  else
    echo "WARNING: Times import failed or credentials are missing." >&2
    echo "The app will start, but SQL exercises need data in times_archive." >&2
    echo "See docs/times-data-setup.md for GCS credentials, then re-run:" >&2
    echo "  ./scripts/import-times-from-times-api.sh" >&2
    echo "Or force a fresh import on the next dev run:" >&2
    echo "  ./scripts/dev.sh --force-import" >&2
  fi
elif [[ "$row_count" -gt 0 ]]; then
  echo "==> Times Archive data present ($row_count rows)."
fi

if lsof -iTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "==> Port $PORT is already in use — opening $URL"
  open_browser
  exit 0
fi

echo "==> Starting dev server at $URL"
uv run uvicorn app.main:app --reload --host "$HOST" --port "$PORT" &
SERVER_PID=$!

cleanup() {
  kill "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

wait_for_server
open_browser
echo
echo "sql-gym is running at $URL"
echo "Press Ctrl+C to stop the dev server."
wait "$SERVER_PID"
