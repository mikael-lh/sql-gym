#!/usr/bin/env python3
"""Append precise expected-output requirements to catalog exercise prompts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.catalog.output_requirements import build_output_requirements_text  # noqa: E402
from app.catalog.times import _parse_exercise  # noqa: E402

EXERCISES_PATH = ROOT / "src/app/catalog/data/times_exercises.json"
_EXPECTED_OUTPUT_MARKER = "\n\nExpected output:"


def _base_prompt(prompt: str) -> str:
    if _EXPECTED_OUTPUT_MARKER in prompt:
        return prompt.split(_EXPECTED_OUTPUT_MARKER, maxsplit=1)[0].rstrip()
    return prompt.rstrip()


def main() -> int:
    entries = json.loads(EXERCISES_PATH.read_text(encoding="utf-8"))
    updated = 0
    for entry in entries:
        exercise = _parse_exercise(dict(entry))
        requirements = build_output_requirements_text(exercise)
        base = _base_prompt(entry["prompt"])
        new_prompt = f"{base}{_EXPECTED_OUTPUT_MARKER} {requirements}"
        if entry["prompt"] != new_prompt:
            entry["prompt"] = new_prompt
            updated += 1

    EXERCISES_PATH.write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Updated prompts for {updated} exercises.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
