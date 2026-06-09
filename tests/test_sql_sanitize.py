from app.execution import validate_select_only
from app.execution.sql_sanitize import strip_sql_comments


def test_strip_sql_comments_removes_line_comments() -> None:
    sql = "-- hint\nSELECT 1;"
    assert strip_sql_comments(sql) == "SELECT 1;"


def test_validate_select_allows_leading_line_comment() -> None:
    sql = "-- Write PostgreSQL for: Arts section headlines\nSELECT 1;"
    assert validate_select_only(sql) is None
