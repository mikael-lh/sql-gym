#!/usr/bin/env python3
"""Validate output-requirements copy for all catalog exercises.

Expected output specs are rendered in the workspace UI (not embedded in prompts).
Re-run after changing reference_sql or column metadata.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.catalog.output_requirements import build_output_requirements_text  # noqa: E402
from app.catalog.times import _parse_exercise  # noqa: E402

EXERCISES_PATH = ROOT / "src/app/catalog/data/times_exercises.json"


def main() -> int:
    entries = json.loads(EXERCISES_PATH.read_text(encoding="utf-8"))
    issues: list[str] = []
    for entry in entries:
        exercise = _parse_exercise(dict(entry))
        text = build_output_requirements_text(exercise)
        if "Order rows by: 1." in text or "Order rows by: 2." in text:
            issues.append(f"{exercise.id}: positional ORDER BY in learner copy")
        for name in exercise.expected_result.column_names:
            if f"`{name}`" not in text:
                issues.append(f"{exercise.id}: missing column `{name}` in output copy")

    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        return 1

    print(f"Validated output requirements for {len(entries)} exercises.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
