#!/usr/bin/env bash
# One-time Cloud VM bootstrap (idempotent). Installs tooling and fixes permissions.
# Invoked from .cursor/environment.json on every session; safe to re-run.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

chmod +x scripts/validate-env.sh 2>/dev/null || true
chmod +x scripts/cloud-env-bootstrap.sh scripts/cloud-env-update.sh 2>/dev/null || true
