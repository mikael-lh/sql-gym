#!/usr/bin/env bash
# Per-session Cloud VM dependency refresh. Runs after git pull on agent startup.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"

uv sync --locked
