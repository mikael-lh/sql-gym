#!/usr/bin/env python3
"""Generate expected grids only for exercises missing grid files."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_expected_results import GRIDS_DIR, _execute_reference_sql  # noqa: E402

EXERCISES_PATH = ROOT / "src/app/catalog/data/times_exercises.json"


def main() -> int:
    database_url = os.environ.get("DATABASE_ADMIN_URL") or os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_ADMIN_URL or DATABASE_URL is required.", file=sys.stderr)
        return 1

    import psycopg

    exercises = json.loads(EXERCISES_PATH.read_text(encoding="utf-8"))
    GRIDS_DIR.mkdir(parents=True, exist_ok=True)
    missing = [
        entry
        for entry in exercises
        if entry.get("reference_sql")
        and not (GRIDS_DIR / f"{entry['id']}.json").exists()
    ]
    if not missing:
        print("No missing expected grids.")
        return 0

    generated = 0
    with psycopg.connect(database_url) as conn:
        for entry in missing:
            exercise_id = entry["id"]
            grid = _execute_reference_sql(conn, entry["reference_sql"])
            output_path = GRIDS_DIR / f"{exercise_id}.json"
            output_path.write_text(
                json.dumps(grid, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            generated += 1
            print(f"Wrote {output_path.name} ({len(grid['rows'])} rows)")

    print(f"Generated {generated} missing expected grids.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
