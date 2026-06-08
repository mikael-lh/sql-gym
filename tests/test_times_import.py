import os

import psycopg
import pytest

EXPECTED_COLUMNS = {
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
}

DATABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE_ADMIN_URL")
DEMO_ROW_COUNT = 2
MIN_IMPORTED_ROW_COUNT = DEMO_ROW_COUNT + 1

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL or DATABASE_ADMIN_URL not set; start Docker Postgres and import data.",
)


def test_times_archive_table_has_expected_columns() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'times_archive'
            """
        )
        columns = {row[0] for row in cur.fetchall()}

    assert EXPECTED_COLUMNS.issubset(columns)


def test_times_archive_has_imported_rows() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM times_archive")
        count_row = cur.fetchone()

    assert count_row is not None
    assert count_row[0] > MIN_IMPORTED_ROW_COUNT


def test_times_archive_sample_row_shape() -> None:
    assert DATABASE_URL is not None
    with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT article_id, pub_date, keywords, byline_person
            FROM times_archive
            WHERE article_id IS NOT NULL
            LIMIT 1
            """
        )
        row = cur.fetchone()

    assert row is not None
    article_id, pub_date, keywords, byline_person = row
    assert article_id
    assert pub_date is None or hasattr(pub_date, "year")
    assert keywords is not None
    assert byline_person is not None
