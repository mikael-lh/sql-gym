#!/usr/bin/env python3
"""One-time helper: populate reference_sql from sample_sql in times_exercises.json."""

from __future__ import annotations

import json
import re
from pathlib import Path

EXERCISES_PATH = Path(__file__).resolve().parents[1] / "src/app/catalog/data/times_exercises.json"
DIALECT_PREFIX = re.compile(r"^-- PostgreSQL target dialect\s*\n", re.IGNORECASE)


def _clean_sample_sql(sample_sql: str) -> str:
    return DIALECT_PREFIX.sub("", sample_sql).strip()


def main() -> None:
    exercises = json.loads(EXERCISES_PATH.read_text(encoding="utf-8"))
    for entry in exercises:
        entry["reference_sql"] = _clean_sample_sql(entry["sample_sql"])
    EXERCISES_PATH.write_text(
        json.dumps(exercises, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Updated reference_sql for {len(exercises)} exercises.")


if __name__ == "__main__":
    main()
