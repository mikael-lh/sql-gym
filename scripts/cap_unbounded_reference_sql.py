#!/usr/bin/env python3
"""Ensure reference_sql queries include a deterministic LIMIT for grid generation."""

from __future__ import annotations

import json
import re
from pathlib import Path

EXERCISES_PATH = Path(__file__).resolve().parents[1] / "src/app/catalog/data/times_exercises.json"
MAX_ROWS = 500


def _is_scalar_count(sql: str) -> bool:
    stripped = sql.strip().rstrip(";")
    return bool(
        re.fullmatch(
            r"SELECT\s+COUNT\s*\(\s*\*?\s*\)\s+.*",
            stripped,
            re.IGNORECASE | re.DOTALL,
        )
    )


def _cap_sql(sql: str) -> str:
    stripped = sql.strip().rstrip(";")
    if re.search(r"\bORDER BY\b", stripped, re.IGNORECASE):
        return f"{stripped} LIMIT {MAX_ROWS};"
    return f"{stripped} ORDER BY 1 LIMIT {MAX_ROWS};"


def main() -> None:
    exercises = json.loads(EXERCISES_PATH.read_text(encoding="utf-8"))
    capped = 0
    for entry in exercises:
        reference_sql = entry.get("reference_sql", "")
        if re.search(r"\bLIMIT\b", reference_sql, re.IGNORECASE):
            continue
        if _is_scalar_count(reference_sql):
            continue
        entry["reference_sql"] = _cap_sql(reference_sql)
        capped += 1
    EXERCISES_PATH.write_text(
        json.dumps(exercises, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Applied LIMIT {MAX_ROWS} to {capped} reference_sql queries.")


if __name__ == "__main__":
    main()
