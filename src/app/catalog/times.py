import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.domain.catalog import Catalog, build_catalog
from app.domain.datasets import TIMES_ARCHIVE_CATALOG_DATASET
from app.domain.exercises import Exercise, ExpectedGrid, ExpectedResultSpec

_EXERCISES_PATH = Path(__file__).resolve().parent / "data" / "times_exercises.json"
_GRIDS_DIR = Path(__file__).resolve().parent / "data" / "expected_grids"
_MAX_GRID_ROWS = 500


def _load_expected_grid(exercise_id: str) -> ExpectedGrid | None:
    grid_path = _GRIDS_DIR / f"{exercise_id}.json"
    if not grid_path.is_file():
        return None

    payload = json.loads(grid_path.read_text(encoding="utf-8"))
    columns = tuple(payload.get("columns", ()))
    raw_rows = payload.get("rows", ())
    rows = tuple(tuple(row) for row in raw_rows)
    if not columns:
        raise ValueError(f"Exercise {exercise_id!r} expected grid is missing columns.")
    if not rows:
        raise ValueError(f"Exercise {exercise_id!r} expected grid has no rows.")
    if len(rows) > _MAX_GRID_ROWS:
        raise ValueError(
            f"Exercise {exercise_id!r} expected grid exceeds {_MAX_GRID_ROWS} rows."
        )
    return ExpectedGrid(columns=columns, rows=rows)


def _parse_exercise(entry: dict[str, Any]) -> Exercise:
    payload = dict(entry)
    expected_result = payload.pop("expected_result", {})
    exercise_id = payload["id"]
    reference_sql = payload.pop("reference_sql", None)
    payload["concept_tags"] = tuple(payload["concept_tags"])
    payload["learning_objectives"] = tuple(payload["learning_objectives"])

    expected_grid = _load_expected_grid(exercise_id)
    if reference_sql and expected_grid is None:
        raise ValueError(
            f"Exercise {exercise_id!r} has reference_sql but no expected grid file."
        )
    if expected_grid and not reference_sql:
        raise ValueError(
            f"Exercise {exercise_id!r} has an expected grid but no reference_sql."
        )

    column_names = (
        expected_grid.columns
        if expected_grid is not None
        else tuple(expected_result.get("column_names", ()))
    )

    payload["expected_result"] = ExpectedResultSpec(
        description=expected_result.get("description"),
        column_names=column_names,
        reference_sql=reference_sql,
        expected_grid=expected_grid,
    )
    return Exercise.model_validate(payload)


@lru_cache(maxsize=1)
def load_times_exercises() -> tuple[Exercise, ...]:
    payload = json.loads(_EXERCISES_PATH.read_text(encoding="utf-8"))
    return tuple(_parse_exercise(entry) for entry in payload)


def build_times_archive_catalog() -> Catalog:
    return build_catalog([TIMES_ARCHIVE_CATALOG_DATASET], load_times_exercises())


TIMES_ARCHIVE_CATALOG = build_times_archive_catalog()
