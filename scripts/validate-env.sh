#!/usr/bin/env bash
# Validates the sql-gym development workflow environment (docs/skills phase).
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
check "on main or feature branch" git rev-parse --abbrev-ref HEAD
check "README.md exists" test -f README.md
check "WORKFLOW.md exists" test -f docs/WORKFLOW.md
check "prd/README.md exists" test -f prd/README.md
check "PR template exists" test -f .github/pull_request_template.md
check "engineering rule exists" test -f .cursor/rules/engineering.mdc
check "workflow rule exists" test -f .cursor/rules/workflow.mdc

for skill in sql-gym-start-issue sql-gym-implement-issue sql-gym-pre-review sql-gym-pre-review-reviewer sql-gym-pre-review-fix; do
  check "skill $skill" test -f ".cursor/skills/$skill/SKILL.md"
done

check "GitHub CLI authenticated" gh auth status
check "origin remote configured" git remote get-url origin

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
echo "Note: No application code or dependency manifests exist yet."
echo "Active phase: none (see prd/README.md). Next step: write-prd for TIM-16."
