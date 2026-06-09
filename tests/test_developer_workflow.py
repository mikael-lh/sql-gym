from pathlib import Path

README = Path("README.md")
WORKFLOW_RULE = Path(".cursor/rules/workflow.mdc")
VALIDATE_ENV = Path("scripts/validate-env.sh")


BASELINE_COMMANDS = (
    "uv build",
    "uv run ruff check .",
    "uv run mypy .",
    "uv run pytest",
    "./scripts/validate-env.sh",
)

README_REQUIRED_PHASE4_DOCS = (
    "## Phase 4 behavior status",
    "interview sessions",
    "docs/session-state.md",
    "docs/phase-4-manual-test-plan.md",
    "/practice/interview/",
    "Resume interview",
)

README_REQUIRED_PHASE3_DOCS = (
    "## Phase 3 behavior status",
    "sql_gym_progress",
    "docs/progress.md",
    "docs/phase-3-manual-test-plan.md",
    "Clear my progress",
    "Timed",
)

README_REQUIRED_PHASE2_DOCS = (
    "## Phase 2 behavior status",
    "Strict grid-match grading",
    "docs/times-data-setup.md",
    "docs/grading.md",
    "docs/phase-2-manual-test-plan.md",
    "docker compose up -d",
)

README_REQUIRED_PHASE1_DOCS = (
    "## Phase 1 behavior status",
    "50 structured exercise entries",
    "/practice` catalog browsing",
    "/practice/{dataset_id}/{exercise_id}` exercise preview",
)

README_REQUIRED_PHASE0_DOCS = (
    "## Phase 0 behavior status",
    "Working behavior",
    "## Remaining follow-up decisions",
    "Persistence",
    "Authentication",
    "AI provider",
)

README_WORKFLOW_POINTERS = (
    ".cursor/rules/workflow.mdc",
    "sql-gym-pre-review",
    "docs/WORKFLOW.md",
)

WORKFLOW_GATE_TEXT = (
    "No product features",
    "No application code",
    "Engineering standards",
    "engineering.mdc",
    "sql-gym-pre-review",
)


def test_readme_documents_baseline_validation_checks() -> None:
    readme = README.read_text()

    assert "## Baseline validation checks" in readme
    for command in BASELINE_COMMANDS:
        assert command in readme


def test_readme_documents_phase_4_behavior_status() -> None:
    readme = README.read_text()

    for expected_text in README_REQUIRED_PHASE4_DOCS:
        assert expected_text in readme


def test_readme_documents_phase_3_behavior_status() -> None:
    readme = README.read_text()

    for expected_text in README_REQUIRED_PHASE3_DOCS:
        assert expected_text in readme


def test_readme_documents_phase_2_behavior_status() -> None:
    readme = README.read_text()

    for expected_text in README_REQUIRED_PHASE2_DOCS:
        assert expected_text in readme


def test_readme_documents_phase_1_behavior_status() -> None:
    readme = README.read_text()

    for expected_text in README_REQUIRED_PHASE1_DOCS:
        assert expected_text in readme


def test_readme_documents_phase_0_behavior_status() -> None:
    readme = README.read_text()

    for expected_text in README_REQUIRED_PHASE0_DOCS:
        assert expected_text in readme


def test_readme_points_to_workflow_gates() -> None:
    readme = README.read_text()

    for expected_text in README_WORKFLOW_POINTERS:
        assert expected_text in readme


def test_workflow_rule_preserves_prd_gates() -> None:
    workflow_rule = WORKFLOW_RULE.read_text()

    for expected_text in WORKFLOW_GATE_TEXT:
        assert expected_text in workflow_rule


def test_validate_env_runs_baseline_validation_checks() -> None:
    validate_env = VALIDATE_ENV.read_text()

    for command in BASELINE_COMMANDS[:-1]:
        assert command in validate_env
