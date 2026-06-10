from app.catalog.schema import get_dataset_schema


def test_get_dataset_schema_loads_times_archive() -> None:
    schema = get_dataset_schema("times-archive")
    assert schema is not None
    assert schema.dataset_id == "times-archive"
    assert len(schema.tables) == 1
    table = schema.tables[0]
    assert table.name == "times_archive"
    assert len(table.columns) == 16
    headline = next(column for column in table.columns if column.name == "headline_main")
    assert headline.type == "TEXT"
    assert headline.description


def test_get_dataset_schema_unknown_dataset() -> None:
    assert get_dataset_schema("unknown") is None
