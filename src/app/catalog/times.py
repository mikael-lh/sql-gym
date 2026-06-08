import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.domain.catalog import Catalog, build_catalog
from app.domain.datasets import TIMES_ARCHIVE_CATALOG_DATASET
from app.domain.exercises import Exercise, ExpectedResultSpec

_EXERCISES_PATH = Path(__file__).resolve().parent / "data" / "times_exercises.json"


def _parse_exercise(entry: dict[str, Any]) -> Exercise:
    payload = dict(entry)
    expected_result = payload.pop("expected_result", {})
    payload["concept_tags"] = tuple(payload["concept_tags"])
    payload["learning_objectives"] = tuple(payload["learning_objectives"])
    payload["expected_result"] = ExpectedResultSpec(
        description=expected_result.get("description"),
        column_names=tuple(expected_result.get("column_names", ())),
    )
    return Exercise.model_validate(payload)


@lru_cache(maxsize=1)
def load_times_exercises() -> tuple[Exercise, ...]:
    payload = json.loads(_EXERCISES_PATH.read_text(encoding="utf-8"))
    return tuple(_parse_exercise(entry) for entry in payload)


def build_times_archive_catalog() -> Catalog:
    return build_catalog([TIMES_ARCHIVE_CATALOG_DATASET], load_times_exercises())


TIMES_ARCHIVE_CATALOG = build_times_archive_catalog()
