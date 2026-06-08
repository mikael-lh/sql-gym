"""Catalog data loaders for SQL Gym practice content."""

from app.catalog.times import (
    TIMES_ARCHIVE_CATALOG,
    build_times_archive_catalog,
    load_times_exercises,
)

__all__ = [
    "TIMES_ARCHIVE_CATALOG",
    "build_times_archive_catalog",
    "load_times_exercises",
]
