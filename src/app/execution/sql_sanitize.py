from __future__ import annotations

import re

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_LINE_COMMENT = re.compile(r"--[^\n]*")


def strip_sql_comments(sql: str) -> str:
    without_blocks = _BLOCK_COMMENT.sub(" ", sql)
    without_lines = _LINE_COMMENT.sub("", without_blocks)
    return without_lines.strip()
