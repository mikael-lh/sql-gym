#!/usr/bin/env bash
# Validates the sql-gym development workflow environment.
# Run from repo root: ./scripts/validate-env.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

pass=0
fail=0

check() {
  local desc="$1"
  shift
  if "$@"; then
    echo "PASS: $desc"
    pass=$((pass + 1))
  else
    echo "FAIL: $desc" >&2
    fail=$((fail + 1))
  fi
}

echo "=== sql-gym environment validation ==="
echo "Repo: $ROOT"
echo

check "git repository" test -d .git
check "on a git branch" git rev-parse --abbrev-ref HEAD
check "README.md exists" test -f README.md
check "WORKFLOW.md exists" test -f docs/WORKFLOW.md
check "prd/README.md exists" test -f prd/README.md
check "product vision PRD exists" test -f prd/00-product-vision.md
check "phase 0 PRD exists" test -f prd/phase-0-product-scaffolding.md
check "PR template exists" test -f .github/pull_request_template.md
check "engineering rule exists" test -f .cursor/rules/engineering.mdc
check "workflow rule exists" test -f .cursor/rules/workflow.mdc

for skill in \
  write-prd \
  implement-from-prd \
  check-prd-alignment \
  update-prd \
  sql-gym-implement-issue \
  sql-gym-run-phase \
  sql-gym-pre-review \
  sql-gym-pre-review-reviewer \
  sql-gym-pre-review-fix
do
  check "skill $skill" test -f ".cursor/skills/$skill/SKILL.md"
done

check "GitHub CLI authenticated" gh auth status
check "origin remote configured" git remote get-url origin

if [[ -f pyproject.toml ]]; then
  check "uv available" uv --version
  check "dependencies are synced" uv sync --locked
  check "production build" uv build
  check "ruff lint" uv run ruff check .
  check "mypy static check" uv run mypy .
  check "pytest suite" uv run pytest
fi

if [[ -n "${DATABASE_URL:-}" ]]; then
  check "postgres reachable via DATABASE_URL" uv run python - <<'PY'
import os
import sys

import psycopg

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    sys.exit(1)

with psycopg.connect(database_url) as conn, conn.cursor() as cur:
    cur.execute("SELECT 1")
    if cur.fetchone() != (1,):
        sys.exit(1)
PY
else
  echo "SKIP: postgres reachable via DATABASE_URL (DATABASE_URL unset)"
fi

echo
echo "=== Summary ==="
echo "Passed: $pass"
echo "Failed: $fail"

if [[ "$fail" -gt 0 ]]; then
  echo "Environment validation FAILED." >&2
  exit 1
fi

echo "Environment validation PASSED."
echo
if [[ -f pyproject.toml ]]; then
  echo "Application stack: Python 3.12 + FastAPI + uv."
else
  echo "Application stack: not scaffolded yet (see prd/phase-0-product-scaffolding.md)."
fi
echo "Active phase: Phase 7 active - local LLM explain-on-fail."
