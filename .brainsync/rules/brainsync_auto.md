

# Project Memory — botatc
> 6016 notes | Score threshold: >40

## Safety — Never Run Destructive Commands

> Dangerous commands are actively monitored.
> Critical/high risk commands trigger error notifications in real-time.

- **NEVER** run `rm -rf`, `del /s`, `rmdir`, `format`, or any command that deletes files/directories without EXPLICIT user approval.
- **NEVER** run `DROP TABLE`, `DELETE FROM`, `TRUNCATE`, or any destructive database operation.
- **NEVER** run `git push --force`, `git reset --hard`, or any command that rewrites history.
- **NEVER** run `npm publish`, `docker rm`, `terraform destroy`, or any irreversible deployment/infrastructure command.
- **NEVER** pipe remote scripts to shell (`curl | bash`, `wget | sh`).
- **ALWAYS** ask the user before running commands that modify system state, install packages, or make network requests.
- When in doubt, **show the command first** and wait for approval.

**Stack:** JavaScript/Python · Express + FastAPI

## 📝 NOTE: 1 uncommitted file(s) in working tree.\n\n## Important Warnings

- **⚠️ GOTCHA: Fixed null crash in Inyectar — evolves the database schema to support new req...** — -     # Inyectar tema del usuario (colores configurados en Mi Perfil)
- **⚠️ GOTCHA: Fixed null crash in Inyectar — evolves the database schema to support new req...** — -     # Inyectar custom theme igual que en inbox
+     # Inyectar tem
- **⚠️ GOTCHA: Patched security issue Tambi — protects against XSS and CSRF token theft** — -         _synced = 0
+         # También busca pedidos para sesiones
- **⚠️ GOTCHA: Patched security issue Colitas — parallelizes async operations for speed** — - def renderizar_inbox(request: Request, wa_id: str = None, tab: str =
- **⚠️ GOTCHA: Fixed null crash in HTMLResponse — evolves the database schema to support new...** — - from typing import List
+ @app.get("/pipeline", response_class=HTML
- **⚠️ GOTCHA: Updated firebase_client database schema** — - class ChatActionPayload(BaseModel):
+ # ───────────────────────────

## Active: `.`

- **⚠️ GOTCHA: Fixed null crash in Inyectar — evolves the database schema to support new req...**
- **⚠️ GOTCHA: Fixed null crash in Inyectar — evolves the database schema to support new req...**
- **⚠️ GOTCHA: Patched security issue Tambi — protects against XSS and CSRF token theft**
- **⚠️ GOTCHA: Patched security issue Colitas — parallelizes async operations for speed**
- **⚠️ GOTCHA: Fixed null crash in HTMLResponse — evolves the database schema to support new...**

## Project Standards

- Patched security issue Request — parallelizes async operations for speed — confirmed 3x
- problem-fix in server.py — confirmed 4x
- Patched security issue False — protects against XSS and CSRF token theft — confirmed 3x
- problem-fix in server.py — confirmed 3x
- Fixed null crash in PLANTILLAS — evolves the database schema to support new r... — confirmed 3x
- Fixed null crash in Determinar — prevents null/undefined runtime crashes — confirmed 3x
- what-changed in inbox.html — confirmed 4x
- Fixed null crash in Soft — prevents null/undefined runtime crashes — confirmed 3x

## Known Fixes

- ❌ 📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, s → ✅ Patched security issue Sincronizar — protects against XSS and CSRF token theft
- ❌ - - Fixed null crash in HTMLResponse — prevents null/undefined runtime crashes → ✅ problem-fix in agent-rules.md
- ❌ - - Fixed null crash in Nivel — prevents null/undefined runtime crashes → ✅ problem-fix in agent-rules.md
- ❌ - - Fixed null crash in Inbox — prevents null/undefined runtime crashes → ✅ problem-fix in agent-rules.md
- ❌ - - Fixed null crash in Vincular — wraps unsafe operation in error boundary → ✅ problem-fix in agent-rules.md

## Recent Decisions

- Optimized Client — prevents null/undefined runtime crashes
- Optimized Client — prevents null/undefined runtime crashes
- Optimized Client — prevents null/undefined runtime crashes
- Optimized Client — prevents null/undefined runtime crashes

## Learned Patterns

- Avoid: ⚠️ GOTCHA: Replaced auth Score — evolves the database schema to support new requirements (seen 2x)
- Avoid: ⚠️ GOTCHA: Replaced auth Score — evolves the database schema to support new requirements (seen 3x)
- Always: Replaced auth Score — evolves the database schema to support new requirements — confirmed 3x (seen 2x)
- Agent generates new migration for every change (squash related changes)
- Agent installs packages without checking if already installed

### 📚 Core Framework Rules: [tinybirdco/tinybird-python-sdk-guidelines]
# Tinybird Python SDK Guidelines

Guidance for using the `tinybird-sdk` package to define Tinybird resources in Python.

## When to Apply

- Installing or configuring tinybird-sdk
- Defining datasources, pipes, or endpoints in Python
- Creating Tinybird clients in Python
- Using data ingestion or queries in Python
- Running tinybird dev/build/deploy commands for Python projects
- Migrating from legacy .datasource/.pipe files to Python
- Defining connections (Kafka, S3, GCS)
- Creating materialized views, copy pipes, or sink pipes

## Rule Files

- `rules/getting-started.md`
- `rules/configuration.md`
- `rules/defining-datasources.md`
- `rules/defining-endpoints.md`
- `rules/client.md`
- `rules/low-level-api.md`
- `rules/cli-commands.md`
- `rules/connections.md`
- `rules/materialized-views.md`
- `rules/copy-sink-pipes.md`
- `rules/tokens.md`

## Quick Reference

- Install: `pip install tinybird-sdk`
- Initialize: `tinybird init`
- Dev mode: `tinybird dev` (uses configured `dev_mode`, typically branch)
- Build: `tinybird build` (builds against configured dev target)
- Deploy: `tinybird deploy` (deploys to main/production)
- Preview in CI: `tinybird preview`
- Migrate: `tinybird migra...
(truncated)


### 📚 Core Framework Rules: [czlonkowski/n8n-expression-syntax]
# n8n Expression Syntax

Expert guide for writing correct n8n expressions in workflows.

---

## Expression Format

All dynamic content in n8n uses **double curly braces**:



**Examples**:


---

## Core Variables

### $json - Current Node Output

Access data from the current node:



### $node - Reference Other Nodes

Access data from any previous node:



**Important**:
- Node names **must** be in quotes
- Node names are **case-sensitive**
- Must match exact node name from workflow

### $now - Current Timestamp

Access current date/time:



### $env - Environment Variables

Access environment variables:



---

## 🚨 CRITICAL: Webhook Data Structure

**Most Common Mistake**: Webhook data is **NOT** at the root!

### Webhook Node Output Structure



### Correct Webhook Data Access



**Why**: Webhook node wraps incoming data under `.body` property to preserve headers, params, and query parameters.

---

## Common Patterns

### Access Nested Fields



### Reference Other Nodes



### Combine Variables



---

## When NOT to Use Expressions

### ❌ Code Nodes

Code nodes use **direct JavaScript access**, NOT expressions!



### ❌ Webhook Paths



### ❌ Credential Fields



---

## V...
(truncated)


## Available Tools (ON-DEMAND only)
- `sys_core_01(q)` — Deep search when stuck
- `sys_core_05(query)` — Full-text lookup
> Context above IS your context. Do NOT call sys_core_14() at startup.
