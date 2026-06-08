#!/usr/bin/env python3
"""Run reference_sql for each catalog exercise and write expected grid JSON files."""

from __future__ import annotations

import json
import os
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import psycopg

ROOT = Path(__file__).resolve().parents[1]
EXERCISES_PATH = ROOT / "src/app/catalog/data/times_exercises.json"
GRIDS_DIR = ROOT / "src/app/catalog/data/expected_grids"
MAX_GRID_ROWS = 500


def _normalize_cell(value: object) -> object:
    if value is None:
        return None
    if isinstance(value, Decimal):
        if value == value.to_integral_value():
            return int(value)
        return float(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _execute_reference_sql(conn: psycopg.Connection, sql: str) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute(sql)
        if cur.description is None:
            raise RuntimeError("Reference SQL did not return a result set.")
        columns = [desc.name for desc in cur.description]
        rows = [
            tuple(_normalize_cell(value) for value in row)
            for row in cur.fetchmany(MAX_GRID_ROWS + 1)
        ]
        if len(rows) > MAX_GRID_ROWS:
            raise RuntimeError(
                f"Reference SQL returned more than {MAX_GRID_ROWS} rows; "
                "add LIMIT/OFFSET or aggregation to reference_sql."
            )
    return {"columns": columns, "rows": rows}


def main() -> int:
    database_url = os.environ.get("DATABASE_ADMIN_URL") or os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_ADMIN_URL or DATABASE_URL is required.", file=sys.stderr)
        return 1

    exercises = json.loads(EXERCISES_PATH.read_text(encoding="utf-8"))
    GRIDS_DIR.mkdir(parents=True, exist_ok=True)

    generated = 0
    with psycopg.connect(database_url) as conn:
        for entry in exercises:
            exercise_id = entry["id"]
            reference_sql = entry.get("reference_sql")
            if not reference_sql:
                print(f"SKIP {exercise_id}: missing reference_sql", file=sys.stderr)
                continue

            grid = _execute_reference_sql(conn, reference_sql)
            if not grid["columns"]:
                raise RuntimeError(f"{exercise_id}: reference_sql returned no columns.")

            output_path = GRIDS_DIR / f"{exercise_id}.json"
            output_path.write_text(
                json.dumps(grid, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            generated += 1
            print(f"Wrote {output_path.name} ({len(grid['rows'])} rows)")

    print(f"Generated {generated} expected grids in {GRIDS_DIR}.")
    return 0 if generated == len(exercises) else 1


if __name__ == "__main__":
    raise SystemExit(main())
