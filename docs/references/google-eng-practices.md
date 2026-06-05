# Google engineering practices (reference)

sql-gym adopts a **subset** of [google/eng-practices](https://github.com/google/eng-practices) for change authoring and review. Read the upstream docs for full context; this page is the repo-local checklist.

**License:** Upstream content is [Apache-2.0](https://github.com/google/eng-practices/blob/master/LICENSE). Do not copy large passages into PRs—link here or to the upstream file.

## Author (before review)

From the [CL author's guide](https://github.com/google/eng-practices/tree/master/review/developer):

| Practice | Link |
|----------|------|
| Small, focused changes | [small-cls.md](https://github.com/google/eng-practices/blob/master/review/developer/small-cls.md) |
| Good CL / PR descriptions | [cl-descriptions.md](https://github.com/google/eng-practices/blob/master/review/developer/cl-descriptions.md) |
| Handle review comments constructively | [handling-comments.md](https://github.com/google/eng-practices/blob/master/review/developer/handling-comments.md) |

**Agent / author:** One concern per PR when possible; describe *what*, *why*, and how tested—not only which files changed.

## Reviewer standard

From [The Standard of Code Review](https://github.com/google/eng-practices/blob/master/review/reviewer/standard.md):

- Goal: **overall code health improves** with each merge.
- Approve when the change **clearly improves** health, even if not perfect—prefer **continuous improvement** over blocking on polish.
- Do **not** approve changes that **definitely worsen** health.
- Non-blocking suggestions: prefix with **`Nit:`** (style nits not in the project style guide).

## Reviewer checklist (what to look for)

From [What to look for in a code review](https://github.com/google/eng-practices/blob/master/review/reviewer/looking-for.md). Agents use this in **sql-gym-pre-review** after product alignment.

| Area | Check |
|------|--------|
| **Design** | Change fits the codebase; integrates with existing design; right layer (not over-abstracted). |
| **Functionality** | Matches intent and PRD; edge cases; concurrency if relevant. |
| **Complexity** | No harder-to-read code than needed; no speculative “future” features. |
| **Tests** | Appropriate tests with the change; tests are simple and would fail if code breaks. |
| **Naming** | Clear names—long enough to mean something, short enough to read. |
| **Comments** | Explain *why*, not *what*; remove obsolete TODOs. |
| **Style** | Match project conventions (language style guides when chosen); separate style-only PRs from behavior. |
| **Documentation** | README / module docs updated if behavior or usage changed. |
| **Context** | Change makes sense in the **whole file** and **system**; does not degrade health. |
| **Good things** | Note what was done well, not only issues. |

## Language style guides

### Python (sql-gym)

Primary reference: [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) (pyguide). It extends [PEP 8](https://peps.python.org/pep-0008/) with project conventions for readability and consistency.

When this repo adds tooling (`pyproject.toml`, Ruff, Black, etc.), **repo config wins** over generic pyguide where they differ.

### SQL

When SQL is linted (e.g. SQLFluff), follow the dialect and rules chosen in repo config. General SQL clarity: [Kickstarter SQL style guide](https://github.com/kristerkoch/sql-style-guide).

### Other languages

- [Google style guide index](https://google.github.io/styleguide/)

## Where this is enforced

| Layer | Role |
|-------|------|
| [.cursor/rules/engineering.mdc](../../.cursor/rules/engineering.mdc) | Always-on **authoring** principles (subset of Google—no reviewer checklist) |
| [sql-gym-pre-review](../../.cursor/skills/sql-gym-pre-review/SKILL.md) | Agent **review** pass using the checklist below |
| [docs/WORKFLOW.md](../WORKFLOW.md) | Pre-review before user review |
