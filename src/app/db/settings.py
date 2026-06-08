import os


def get_database_url() -> str | None:
    return os.environ.get("DATABASE_URL")
