# GitHub PR operations for agents

How **Cursor Cloud Agents** (and other agents on this repo) create, update, inspect, and merge pull requests on `mikael-lh/sql-gym`.

**Default process:** implement → open a **draft** PR → run [pre-review](WORKFLOW.md#pre-review-before-user-review) → hand off to the **user** for review and merge. This doc covers the **mechanics** when an agent needs to touch GitHub directly.

## Why two tools?

Cloud Agent VMs use **two different GitHub credentials**:

| Credential | Prefix / identity | Used for |
|------------|-------------------|----------|
| Git remote token | `x-access-token:…` in `git` URLs | `git push`, `git fetch`, `git pull` |
| `gh` CLI token | `ghs_…`, viewer `cursor[bot]` | `gh pr view`, `gh pr ready`, `gh pr merge`, checks, comments |

`gh` runs as the **Cursor GitHub App** (`cursor[bot]`), not the developer's personal account. That app token is **scoped**: some PR APIs work, others return:

```text
Resource not accessible by integration
```

Verified on this repo (2026-06-08):

| Action | `gh` CLI | Cursor `ManagePullRequest` tool |
|--------|----------|----------------------------------|
| Push branch | ✅ (`git push`) | — |
| Create PR | ❌ `gh pr create` fails | ✅ `create_pr` |
| Update PR title/body | ❌ (same integration limit) | ✅ `update_pr` |
| View PR / checks | ✅ `gh pr view`, `gh pr checks` | — |
| Mark ready for review | ✅ `gh pr ready` | — |
| Merge PR | ✅ `gh pr merge` (squash only) | — |
| Add/remove labels | — | ✅ `EditPullRequestLabels` (when user asks) |

**Rule of thumb:** use **`ManagePullRequest`** to open or update PRs; use **`gh`** to inspect, mark ready, and merge.

Repo merge settings: **squash merge only** (`allow_squash_merge: true`; merge commit and rebase disabled).

## End-to-end workflow

### 1. Branch and commit

```bash
git checkout -b cursor/<short-desc>-<suffix>   # cloud template supplies suffix, e.g. -4f22
# … implement …
git add <files>
git commit -m "TIM-NN: concise summary"
git push -u origin cursor/<short-desc>-<suffix>
```

Branch naming: see [GitHub conventions](WORKFLOW.md#github-conventions). Do **not** use `feature/…`.

### 2. Create the PR (Cursor tool — not `gh`)

Use the **`ManagePullRequest`** tool with `action: create_pr`:

- `branch_name`: the pushed branch (e.g. `cursor/tim-42-parser-4f22`)
- `base_branch`: `main` (unless user specified otherwise)
- `title`: `TIM-NN: <summary>` when implementing a Linear issue
- `body`: follow [.github/pull_request_template.md](../.github/pull_request_template.md) — summary, risks, test plan, PRD link
- `draft`: `true` by default until [pre-review](WORKFLOW.md#pre-review-before-user-review) passes

**Do not** use `gh pr create` on Cloud Agents — it fails with `Resource not accessible by integration`.

Example failure (for debugging):

```bash
gh pr create --base main --head cursor/my-branch-4f22 --title "…" --body "…" --draft
# GraphQL: Resource not accessible by integration (createPullRequest)
```

### 3. Update the PR after more commits

Push additional commits to the same branch, then use **`ManagePullRequest`** with `action: update_pr` (same `branch_name`; optional `title` / `body` changes).

### 4. Inspect with `gh`

```bash
gh pr view --json number,url,state,isDraft,mergeable,mergeStateStatus
gh pr checks
gh pr diff
```

`gh api user` may return 403 (`Resource not accessible by integration`) — that is expected for the app token. Use `gh api graphql -f query='query { viewer { login } }'` → `cursor[bot]` if you need the authenticated identity.

### 5. Mark ready for review

After **sql-gym-pre-review** passes and the user should review:

```bash
gh pr ready <number>
```

Leave the PR in **draft** until pre-review is complete unless the user explicitly asks otherwise.

### 6. Merge (when appropriate)

Merge only when workflow allows it — typically after user approval, or when the user explicitly asks the agent to merge (e.g. capability checks, trivial doc-only fixes they requested).

This repo allows **squash merge** only:

```bash
gh pr ready <number>    # required if still a draft; merge fails on drafts
gh pr merge <number> --squash --delete-branch
```

Merge is attributed to `app/cursor` (`cursor[bot]`), not the human developer.

**Do not** use `gh pr merge` while blocking pre-review findings remain or before the user has reviewed product/architecture changes.

## Checklist before handoff

Align with [workflow.mdc](../.cursor/rules/workflow.mdc) and [pre-review](WORKFLOW.md#pre-review-before-user-review):

1. PR created via **`ManagePullRequest`** (draft)
2. Template filled; agent pre-review boxes accurate
3. Tests/lint green (or documented if CI not configured)
4. **`sql-gym-pre-review`** loop complete (reviewer ≠ implementer)
5. `gh pr ready` when handing off to the user
6. User merges — unless they explicitly delegated merge to the agent

## Troubleshooting

| Symptom | Likely cause | What to do |
|---------|--------------|------------|
| `gh pr create` → `Resource not accessible by integration` | App token cannot create PRs | Use **`ManagePullRequest`** `create_pr` |
| `git push` fails | Branch protection or missing write access | Escalate to user; confirm Cloud Agent GitHub access |
| `gh pr merge` → `Pull Request is still a draft` | PR not marked ready | Run `gh pr ready <number>` first |
| `mergeable: CONFLICTING` | Branch behind or conflicting with `main` | `git fetch origin main && git merge origin/main`, resolve, push |
| Empty or wrong PR body | Used minimal `create_pr` body | `update_pr` with full template content |

## References

- [docs/WORKFLOW.md](WORKFLOW.md) — full agent playbook, pre-review, branch naming
- [.github/pull_request_template.md](../.github/pull_request_template.md)
- [.cursor/skills/sql-gym-implement-issue/SKILL.md](../.cursor/skills/sql-gym-implement-issue/SKILL.md) — open PR after implementation
- [.cursor/skills/sql-gym-pre-review/SKILL.md](../.cursor/skills/sql-gym-pre-review/SKILL.md) — before marking ready for user review
