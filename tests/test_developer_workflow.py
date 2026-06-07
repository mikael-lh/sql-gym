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

README_REQUIRED_PHASE0_DOCS = (
    "## Phase 0 behavior status",
    "Working behavior",
    "Placeholder behavior",
    "## Remaining follow-up decisions",
    "Production Times refresh process",
    "Grading model",
    "Persistence",
    "Authentication",
    "AI provider",
)

README_REQUIRED_WORKFLOW_GATES = (
    "No product work",
    "No application code",
    "approved plan",
    "sql-gym-pre-review",
)


def test_readme_documents_baseline_validation_checks() -> None:
    readme = README.read_text()

    assert "## Baseline validation checks" in readme
    for command in BASELINE_COMMANDS:
        assert command in readme


def test_readme_documents_phase_0_behavior_status() -> None:
    readme = README.read_text()

    for expected_text in README_REQUIRED_PHASE0_DOCS:
        assert expected_text in readme


def test_readme_preserves_prd_workflow_gates() -> None:
    readme = README.read_text()

    for expected_text in README_REQUIRED_WORKFLOW_GATES:
        assert expected_text in readme


def test_validate_env_runs_baseline_validation_checks() -> None:
    validate_env = VALIDATE_ENV.read_text()

    for command in BASELINE_COMMANDS[:-1]:
        assert command in validate_env
