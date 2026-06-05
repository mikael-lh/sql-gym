# Plugin setup and verification

sql-gym uses three Cursor marketplace plugins for workflow steps 1–3. Install them in your IDE (not in this repo). Use this checklist to confirm each one works.

## 1. ChatPRD (requirements)

**Install:** Agent chat → `/add-plugin` and search **ChatPRD**, or [ChatPRD on the marketplace](https://cursor.com/marketplace).

**What it provides:** MCP to ChatPRD, skills (`write-prd`, `implement-from-prd`, `check-prd-alignment`, `update-prd`), product-aware rules.

### Verify ChatPRD

| Check | How |
|-------|-----|
| Plugin installed | **Cursor Settings** → **Plugins** — ChatPRD listed and enabled |
| MCP connected | **Settings** → **Tools & MCP** — **ChatPRD** server present and connected (OAuth if prompted) |
| Skills available | New Agent chat → type `/` — skills such as `write-prd` appear, or ask: *"Use the write-prd skill to list what you need from me"* |
| MCP responds | In Agent chat: *"List my ChatPRD projects"* (or open a known doc) — should return data, not "MCP unavailable" |

**If MCP fails:** Fully quit and reopen Cursor; reconnect ChatPRD under Tools & MCP; ensure you are signed into [ChatPRD](https://chatprd.ai) in the browser when OAuth runs.

**Repo tie-in:** Approved specs are saved under `prd/` per [WORKFLOW.md](WORKFLOW.md).

---

## 2. Linear (backlog)

**Install:** **Settings** → **Tools & MCP** → search **Linear** → **Add to Cursor** and complete OAuth.

Alternatively, add a project MCP file (team-shared):

```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/mcp"]
    }
  }
}
```

Save as `.cursor/mcp.json` in the repo root if you want the whole team to use the same config ([Linear + Cursor docs](https://linear.app/integrations/cursor-mcp)).

You can also install the **Cursor Plugin for Linear** from the marketplace if listed separately from the MCP entry.

### Verify Linear

| Check | How |
|-------|-----|
| MCP connected | **Tools & MCP** — Linear shows connected (green / no error) |
| Read issues | Agent: *"List open issues in team sql-gym"* (adjust team/project name to your workspace) |
| Create issue (optional) | Agent: *"Create a draft Linear issue titled 'Test MCP' in project sql-gym"* — confirm in Linear UI, then cancel/delete the test issue |

**If connection fails:** Toggle Linear off/on in MCP settings; restart Cursor; retry OAuth. Remote MCP can need more than one attempt.

**Repo tie-in:** Issues link to `prd/…` sections; do not paste full PRDs into Linear ([WORKFLOW.md](WORKFLOW.md#linear-conventions)).

---

## 3. Superpowers (implementation)

**Install:** Agent chat → `/add-plugin superpowers` or [Superpowers on the marketplace](https://cursor.com/marketplace/superpowers).

**When to install:** Before Phase 0 coding, or as soon as you start implementation. Not required for requirements-only work.

**Scope in this repo:** Implementation discipline only—not product discovery. See [.cursor/rules/superpowers.mdc](../.cursor/rules/superpowers.mdc).

### Verify Superpowers

| Check | How |
|-------|-----|
| Plugin installed | **Settings** → **Plugins** — Superpowers listed |
| Skills available | Agent chat → `/` — skills such as `executing-plans`, `code-reviewer` appear |
| Skill runs | *"Use the executing-plans skill"* on a trivial task, or *"Use code-reviewer"* after a small change |

**If skills missing:** Update Cursor; quit fully and reopen; `/plugin-update superpowers` if your build supports it; invoke by name in chat even if `/` list is empty.

### Superpowers skills used here

| Skill | Use when |
|-------|----------|
| `executing-plans` | Breaking down an approved ChatPRD milestone plan into implementation steps |
| TDD-related skills | Writing features with tests (once stack exists) |
| `code-reviewer` | After a logical chunk of code vs plan + `engineering.mdc` |
| `finishing-a-development-branch` | Tests pass, ready to open or finalize a PR |

**Do not use** Superpowers `brainstorming` for product scope—use ChatPRD `write-prd` instead.

---

## Quick confirmation script (copy into Agent chat)

After installing plugins 1 and 2, paste:

```text
Confirm my Cursor setup for sql-gym:
1. ChatPRD MCP — list projects or confirm connection.
2. Linear MCP — list my teams and one project I specify (I'll name it).
3. Report which ChatPRD and Superpowers skills you can see.
Do not create or change any issues or PRDs yet.
```

Replace step 3 with Superpowers checks once plugin 3 is installed.
