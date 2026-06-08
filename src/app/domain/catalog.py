from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, model_validator

from app.domain.datasets import Dataset
from app.domain.exercises import Exercise


class Catalog(BaseModel):
    model_config = ConfigDict(frozen=True)

    datasets: tuple[Dataset, ...]
    exercises: tuple[Exercise, ...]

    @model_validator(mode="after")
    def validate_dataset_references(self) -> "Catalog":
        dataset_ids = {dataset.id for dataset in self.datasets}
        for exercise in self.exercises:
            if exercise.dataset_id not in dataset_ids:
                message = (
                    f"Exercise {exercise.id!r} references unknown dataset "
                    f"{exercise.dataset_id!r}."
                )
                raise ValueError(message)
        return self


def build_catalog(
    datasets: Iterable[Dataset],
    exercises: Iterable[Exercise],
) -> Catalog:
    return Catalog(
        datasets=tuple(datasets),
        exercises=tuple(exercises),
    )
