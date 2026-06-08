#!/usr/bin/env bash
# Rebuild vendored CodeMirror bundle for the practice editor.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

npm install codemirror @codemirror/lang-sql @codemirror/view @codemirror/state @codemirror/commands @codemirror/language esbuild --no-save
npx esbuild static/js/practice-editor-entry.js \
  --bundle \
  --format=iife \
  --global-name=PracticeEditorBundle \
  --outfile=static/vendor/codemirror/bundle.js \
  --minify
