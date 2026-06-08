#!/usr/bin/env python3
"""Download Times Archive slim NDJSON from GCS and load into PostgreSQL."""

from __future__ import annotations

import json
import os
import stat
import sys
import tempfile
from collections.abc import Iterator
from datetime import date, datetime
from typing import Any

import psycopg
from google.cloud import storage

EXPECTED_COLUMNS = (
    "article_id",
    "uri",
    "pub_date",
    "section_name",
    "news_desk",
    "type_of_material",
    "document_type",
    "word_count",
    "web_url",
    "headline_main",
    "byline_original",
    "abstract",
    "snippet",
    "keywords",
    "byline_person",
    "multimedia_count_by_type",
)

INSERT_SQL = f"""
INSERT INTO times_archive ({", ".join(EXPECTED_COLUMNS)})
VALUES ({", ".join(f"%({col})s" for col in EXPECTED_COLUMNS)})
ON CONFLICT (article_id) DO UPDATE SET
    uri = EXCLUDED.uri,
    pub_date = EXCLUDED.pub_date,
    section_name = EXCLUDED.section_name,
    news_desk = EXCLUDED.news_desk,
    type_of_material = EXCLUDED.type_of_material,
    document_type = EXCLUDED.document_type,
    word_count = EXCLUDED.word_count,
    web_url = EXCLUDED.web_url,
    headline_main = EXCLUDED.headline_main,
    byline_original = EXCLUDED.byline_original,
    abstract = EXCLUDED.abstract,
    snippet = EXCLUDED.snippet,
    keywords = EXCLUDED.keywords,
    byline_person = EXCLUDED.byline_person,
    multimedia_count_by_type = EXCLUDED.multimedia_count_by_type
"""


def _parse_pub_date(value: str | None) -> date | None:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    if "T" in normalized:
        return datetime.fromisoformat(normalized).date()
    return date.fromisoformat(normalized)


def _normalize_row(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "article_id": raw.get("article_id"),
        "uri": raw.get("uri"),
        "pub_date": _parse_pub_date(raw.get("pub_date")),
        "section_name": raw.get("section_name"),
        "news_desk": raw.get("news_desk"),
        "type_of_material": raw.get("type_of_material"),
        "document_type": raw.get("document_type"),
        "word_count": raw.get("word_count"),
        "web_url": raw.get("web_url"),
        "headline_main": raw.get("headline_main"),
        "byline_original": raw.get("byline_original"),
        "abstract": raw.get("abstract"),
        "snippet": raw.get("snippet"),
        "keywords": json.dumps(raw.get("keywords") or []),
        "byline_person": json.dumps(raw.get("byline_person") or []),
        "multimedia_count_by_type": json.dumps(raw.get("multimedia_count_by_type"))
        if raw.get("multimedia_count_by_type") is not None
        else None,
    }


def _iter_ndjson_rows(
    client: storage.Client,
    bucket_name: str,
    prefix: str,
) -> Iterator[dict[str, Any]]:
    bucket = client.bucket(bucket_name)
    blobs = sorted(client.list_blobs(bucket, prefix=prefix), key=lambda blob: blob.name)
    if not blobs:
        raise RuntimeError(f"No objects found under gs://{bucket_name}/{prefix}")

    for blob in blobs:
        if not blob.name.endswith(".ndjson"):
            continue
        print(f"Downloading gs://{bucket_name}/{blob.name}", flush=True)
        for line_number, line in enumerate(blob.download_as_text().splitlines(), start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                yield json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise RuntimeError(
                    f"Invalid JSON in {blob.name} line {line_number}: {exc}"
                ) from exc


def _resolve_credentials_path() -> str | None:
    cloud_secret = os.environ.get("GCS View SA")
    if cloud_secret:
        fd, cred_path = tempfile.mkstemp(prefix="gcs-sa-", suffix=".json")
        with os.fdopen(fd, "w") as handle:
            handle.write(cloud_secret)
        os.chmod(cred_path, stat.S_IRUSR)
        return cred_path

    explicit = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    return explicit if explicit and os.path.isfile(explicit) else None


def main() -> int:
    database_url = os.environ.get("DATABASE_ADMIN_URL") or os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_ADMIN_URL or DATABASE_URL is required.", file=sys.stderr)
        return 1

    bucket_name = os.environ.get("GCS_BUCKET", "ny-archive-bucket")
    prefix = os.environ.get("GCS_PREFIX", "nyt-ingest/archive_slim/").rstrip("/") + "/"

    temp_cred_path: str | None = None
    try:
        temp_cred_path = _resolve_credentials_path()
        if temp_cred_path:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_cred_path

        client = storage.Client()
        rows_loaded = 0

        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                print("Truncating times_archive …", flush=True)
                cur.execute("TRUNCATE times_archive")

                batch: list[dict[str, Any]] = []
                for raw_row in _iter_ndjson_rows(client, bucket_name, prefix):
                    batch.append(_normalize_row(raw_row))
                    if len(batch) >= 500:
                        cur.executemany(INSERT_SQL, batch)
                        rows_loaded += len(batch)
                        batch.clear()
                        print(f"Loaded {rows_loaded} rows …", flush=True)

                if batch:
                    cur.executemany(INSERT_SQL, batch)
                    rows_loaded += len(batch)

            conn.commit()

        print(f"Import complete: {rows_loaded} rows in times_archive.", flush=True)
        return 0
    except Exception as exc:  # noqa: BLE001 - CLI entrypoint reports and exits
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if temp_cred_path:
            try:
                os.remove(temp_cred_path)
            except OSError:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
