"""Learner-facing expected output copy derived from catalog metadata."""

from __future__ import annotations

import re

from app.domain.exercises import Exercise

_ORDER_BY_PATTERN = re.compile(
    r"\bORDER\s+BY\s+(.+?)(?:\s+LIMIT\s+\d+)?\s*;?\s*$",
    re.IGNORECASE | re.DOTALL,
)
_LIMIT_PATTERN = re.compile(r"\bLIMIT\s+(\d+)\s*;?\s*$", re.IGNORECASE)
_POSITIONAL_ORDER_PATTERN = re.compile(
    r"^(\d+)(\s+(ASC|DESC))?$",
    re.IGNORECASE,
)


def _extract_order_by(reference_sql: str | None) -> str | None:
    if not reference_sql:
        return None
    match = _ORDER_BY_PATTERN.search(reference_sql.strip())
    if match is None:
        return None
    clause = match.group(1).strip().rstrip(";")
    return clause or None


def _humanize_order_by(clause: str, columns: tuple[str, ...]) -> str:
    """Turn positional ORDER BY (e.g. ``1 DESC``) into column names learners can use."""
    positional = _POSITIONAL_ORDER_PATTERN.match(clause.strip())
    if positional is None:
        return clause

    index = int(positional.group(1))
    direction = (positional.group(2) or "").strip()
    if index < 1 or index > len(columns):
        return clause

    column_name = columns[index - 1]
    return f"{column_name} {direction}".strip() if direction else column_name


def _extract_limit(reference_sql: str | None) -> int | None:
    if not reference_sql:
        return None
    match = _LIMIT_PATTERN.search(reference_sql.strip())
    if match is None:
        return None
    return int(match.group(1))


def build_output_requirements_text(exercise: Exercise) -> str:
    """Describe the exact result grid learners must produce for strict grading."""
    columns = exercise.expected_result.column_names
    if not columns:
        return (
            "Your query result must match the expected output exactly "
            "(column names, order, row order, and values). "
            "Grading compares the result grid, not your SQL wording."
        )

    column_list = ", ".join(f"`{name}`" for name in columns)
    parts = [
        f"Return exactly these columns in this order: {column_list}.",
    ]

    reference_sql = exercise.expected_result.reference_sql
    order_by = _extract_order_by(reference_sql)
    if order_by:
        humanized = _humanize_order_by(order_by, columns)
        parts.append(f"Order rows by: {humanized}.")

    limit = _extract_limit(reference_sql)
    if limit is not None:
        parts.append(f"Return at most {limit} row(s).")

    parts.append(
        "Grading compares your query result to the expected output grid "
        "(column names, order, row order, and values)—not your SQL wording."
    )
    return " ".join(parts)
