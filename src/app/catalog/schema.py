from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

_SCHEMA_DIR = Path(__file__).resolve().parent / "data"
_SCHEMA_BY_DATASET: dict[str, str] = {
    "times-archive": "times_archive_schema.json",
}


class SchemaColumn(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    type: str
    description: str = ""


class SchemaTable(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    columns: tuple[SchemaColumn, ...]


class DatasetSchema(BaseModel):
    model_config = ConfigDict(frozen=True)

    dataset_id: str
    tables: tuple[SchemaTable, ...] = Field(default_factory=tuple)


@lru_cache(maxsize=8)
def get_dataset_schema(dataset_id: str) -> DatasetSchema | None:
    filename = _SCHEMA_BY_DATASET.get(dataset_id)
    if filename is None:
        return None
    path = _SCHEMA_DIR / filename
    payload = json.loads(path.read_text(encoding="utf-8"))
    return DatasetSchema.model_validate(payload)
