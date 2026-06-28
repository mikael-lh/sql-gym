from pydantic import BaseModel, ConfigDict, Field


class QueryResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    columns: tuple[str, ...]
    rows: tuple[tuple[object, ...], ...]
    row_count: int = Field(ge=0)
    truncated: bool = False


class ExecutionError(BaseModel):
    model_config = ConfigDict(frozen=True)

    message: str
    code: str
    postgres_message: str | None = None
