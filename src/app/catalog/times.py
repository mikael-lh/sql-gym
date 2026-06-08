import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.domain.catalog import Catalog, build_catalog
from app.domain.datasets import TIMES_ARCHIVE_CATALOG_DATASET
from app.domain.exercises import Exercise, ExpectedResultSpec

_EXERCISES_PATH = Path(__file__).resolve().parent / "data" / "times_exercises.json"


def _parse_exercise(entry: dict[str, Any]) -> Exercise:
    expected_result = entry.get("expected_result", {})
    return Exercise(
        id=entry["id"],
        dataset_id=entry["dataset_id"],
        title=entry["title"],
        prompt=entry["prompt"],
        difficulty=entry["difficulty"],
        mode=entry["mode"],
        target_dialect=entry["target_dialect"],
        concept_tags=tuple(entry["concept_tags"]),
        estimated_time_minutes=entry["estimated_time_minutes"],
        learning_objectives=tuple(entry["learning_objectives"]),
        hint=entry["hint"],
        sample_sql=entry["sample_sql"],
        availability_status=entry.get("availability_status", "available"),
        expected_result=ExpectedResultSpec(
            description=expected_result.get("description"),
            column_names=tuple(expected_result.get("column_names", ())),
        ),
    )


@lru_cache(maxsize=1)
def load_times_exercises() -> tuple[Exercise, ...]:
    payload = json.loads(_EXERCISES_PATH.read_text(encoding="utf-8"))
    return tuple(_parse_exercise(entry) for entry in payload)


def build_times_archive_catalog() -> Catalog:
    return build_catalog([TIMES_ARCHIVE_CATALOG_DATASET], load_times_exercises())


TIMES_ARCHIVE_CATALOG = build_times_archive_catalog()
