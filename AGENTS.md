# AGENTS.md

Guidance for **Cursor agents** in [sql-gym](https://github.com/mikael-lh/sql-gym).

sql-gym will be a SQL practice app. **Product scope is not finalized** until [prd/00-product-vision.md](prd/00-product-vision.md) exists and [prd/README.md](prd/README.md) names an active phase. Do not implement application features, choose frameworks, or invent requirements before that.

| What | Where |
|------|--------|
| Requirements & product principles | [prd/](prd/) |
| Development process (ChatPRD, Linear, GitHub) | [docs/WORKFLOW.md](docs/WORKFLOW.md) |
| Session guardrails (always applied in Cursor) | [.cursor/rules/workflow.mdc](.cursor/rules/workflow.mdc) |

**Secrets:** none are committed. When the app is built, document env vars in `.env.example`. On Cursor Cloud VMs, ask the user to add secrets in Cloud settings—do not assume a local `.env` exists.
