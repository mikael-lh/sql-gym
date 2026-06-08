from pydantic import BaseModel, ConfigDict, Field


class DatasetProvenance(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_name: str
    source_url: str
    schema_reference: str
    fixture_path: str
    note: str


class Dataset(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    description: str
    provenance: DatasetProvenance
    is_demo: bool = Field(default=True)


TIMES_ARCHIVE_DEMO_DATASET = Dataset(
    id="times-archive-demo",
    name="Times Archive demo",
    description="Schema-aligned Times article rows for Phase 0 UI placeholders.",
    provenance=DatasetProvenance(
        source_name="times-api",
        source_url="https://github.com/mikael-lh/times-api",
        schema_reference="times-api/schema/archive_articles.json",
        fixture_path="src/app/fixtures/times/archive_articles_demo.json",
        note="Schema-aligned demo rows only; not final production Times data.",
    ),
)

TIMES_ARCHIVE_CATALOG_DATASET = Dataset(
    id="times-archive",
    name="Times Archive",
    description=(
        "Production-ready Times article catalog for SQL practice on curated archive rows."
    ),
    provenance=DatasetProvenance(
        source_name="times-api",
        source_url="https://github.com/mikael-lh/times-api",
        schema_reference="times-api/schema/archive_articles.json",
        fixture_path="src/app/catalog/data/times_exercises.json",
        note=(
            "Production-ready catalog exercises aligned to the times-api archive schema. "
            "Article rows remain in src/app/fixtures/times/archive_articles_demo.json."
        ),
    ),
    is_demo=False,
)
