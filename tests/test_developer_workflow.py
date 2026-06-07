from pathlib import Path


README = Path("README.md")
VALIDATE_ENV = Path("scripts/validate-env.sh")


BASELINE_COMMANDS = (
    "uv build",
    "uv run ruff check .",
    "uv run mypy .",
    "uv run pytest",
    "./scripts/validate-env.sh",
)


def test_readme_documents_baseline_validation_checks() -> None:
    readme = README.read_text()

    assert "## Baseline validation checks" in readme
    for command in BASELINE_COMMANDS:
        assert command in readme


def test_validate_env_runs_baseline_validation_checks() -> None:
    validate_env = VALIDATE_ENV.read_text()

    for command in BASELINE_COMMANDS[:-1]:
        assert command in validate_env
