

# Project Memory — botatc
> 5112 notes | Score threshold: >40

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

- **⚠️ GOTCHA: Added JWT tokens authentication** — - - ⚠️ GOTCHA: Updated schema Fixed
+ - ⚠️ GOTCHA: Added JWT tokens au
- **⚠️ GOTCHA: Added JWT tokens authentication — evolves the database schema to support new ...** — - > 5094 notes | Score threshold: >40
+ > 5105 notes | Score threshold
- **⚠️ GOTCHA: Updated schema Fixed** — - - problem-fix in shared-context.json
+ - problem-fix in server.py
- 
- **gotcha in shared-context.json** — -     }
+     },
-   ]
+     {
- }
+       "id": "30455430262819bd",
+
- **⚠️ GOTCHA: Added JWT tokens authentication — evolves the database schema to support new ...** — - > 5087 notes | Score threshold: >40
+ > 5094 notes | Score threshold
- **gotcha in shared-context.json** — -     }
+     },
-   ]
+     {
- }
+       "id": "2e4b4774ccd8419a",
+

## Project Standards

- Added JWT tokens authentication — confirmed 3x
- problem-fix in shared-context.json — confirmed 3x
- Added JWT tokens authentication — confirmed 4x
- what-changed in shared-context.json — confirmed 3x
- Patched security issue Patched — confirmed 3x
- Added JWT tokens authentication — confirmed 3x
- what-changed in shared-context.json — confirmed 3x
- Added JWT tokens authentication — confirmed 3x

## Known Fixes

- ❌ 📌 IDE AST Context: Modified symbols likely include [app, custom_exception_handler, gemini_client, s → ✅ problem-fix in server.py
- ❌ - - Fixed null crash in HTMLResponse — prevents null/undefined runtime crashes → ✅ problem-fix in agent-rules.md
- ❌ - - Fixed null crash in Nivel — prevents null/undefined runtime crashes → ✅ problem-fix in agent-rules.md
- ❌ - - Fixed null crash in Inbox — prevents null/undefined runtime crashes → ✅ problem-fix in agent-rules.md
- ❌ - - Fixed null crash in Vincular — wraps unsafe operation in error boundary → ✅ problem-fix in agent-rules.md

## Recent Decisions

- Optimized Score — evolves the database schema to support new requirements
- Optimized Project — evolves the database schema to support new requirements
- Optimized None — ensures atomic multi-step database operations
- Optimized None — ensures atomic multi-step database operations

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
- Migrate: `tinybird migrate` (convert .datasource/.pipe files to Python)
- Server-side only; never expose tokens in browsers


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

## Validation Rules

### 1. Always Use {{}}

Expressions **must** be wrapped in double curly braces.



### 2. Use Quotes for Spaces

Field or node names with spaces require **bracket notation**:



### 3. Match Exact Node Names

Node references are **case-sensitive**:



### 4. No Nested {{}}

Don't double-wrap expressions:



---

## Common Mistakes

For complete error catalog with fixes, see [COMMON_MISTAKES.md](COMMON_MISTAKES.md)

### Quick Fixes

| Mistake | Fix |
|---------|-----|
| `$json.field` | `{{$json.field}}` |
| `{{$json.field name}}` | `{{$json['field name']}}` |
| `{{$node.HTTP Request}}` | `{{$node["HTTP Request"]}}` |
| `{{{$json.field}}}` | `{{$json.field}}` |
| `{{$json.name}}` (webhook) | `{{$json.body.name}}` |
| `'={{$json.email}}'` (Code node) | `$json.email` |

---

## Working Examples

For real workflow examples, see [EXAMPLES.md](EXAMPLES.md)

### Example 1: Webhook to Slack

**Webhook receives**:


**In Slack node text field**:


### Example 2: HTTP Request to Email

**HTTP Request returns**:


**In Email node** (reference HTTP Request):


### Example 3: Format Timestamp



---

## Data Type Handling

### Arrays



### Objects



### Strings



### Numbers



---

## Advanced Patterns

### Conditional Content



### Date Manipulation



### String Manipul...
(truncated)


### 📚 Core Framework Rules: [czlonkowski/n8n-code-python]
# Python Code Node (Beta)

Expert guidance for writing Python code in n8n Code nodes.

---

## ⚠️ Important: JavaScript First

**Recommendation**: Use **JavaScript for 95% of use cases**. Only use Python when:
- You need specific Python standard library functions
- You're significantly more comfortable with Python syntax
- You're doing data transformations better suited to Python

**Why JavaScript is preferred:**
- Full n8n helper functions ($helpers.httpRequest, etc.)
- Luxon DateTime library for advanced date/time operations
- No external library limitations
- Better n8n documentation and community support

---

## Quick Start



### Essential Rules

1. **Consider JavaScript first** - Use Python only when necessary
2. **Access data**: `_input.all()`, `_input.first()`, or `_input.item`
3. **CRITICAL**: Must return `[{"json": {...}}]` format
4. **CRITICAL**: Webhook data is under `_json["body"]` (not `_json` directly)
5. **CRITICAL LIMITATION**: **No external libraries** (no requests, pandas, numpy)
6. **Standard library only**: json, datetime, re, base64, hashlib, urllib.parse, math, random, statistics

---

## Mode Selection Guide

Same as JavaScript - choose based on your use case:

### Run Once for All Items (Recommended - Default)

**Use this mode for:** 95% of use cases

- **How it works**: Code executes **once** regardless of input count
- **Data access**: `_input.all()` or `_items` array (Native mode)
- **Best for**: Aggregation, filtering, batch processing, transformations
- **Performance**: Faster for multiple items (single execution)



### Run Once for Each Item

**Use this mode for:** Specialized cases only

- **How it works**: Code executes **separately** for each input item
- **Data access**: `_input.item` or `_item` (Native mode)
- **Best for**: Item-specific logic, independent operations, per-item validation
- **Performance**: Slower for large datasets (multiple executions)



---

## Python Modes: Beta vs Native

n8n offers two Python execution modes:

### Python (Beta) - Recommended
- **Use**: `_input`, `_json`, `_node` helper syntax
- **Best for**: Most Python use cases
- **Helpers available**: `_now`, `_today`, `_jmespath()`
- **Import**: `from datetime import datetime`



### Python (Native) (Beta)
- **Use**: `_items`, `_item` variables only
- **No helpers**: No `_input`, `_now`, etc.
- **More limited**: Standard Python only
- **Use when**: Need pure Python without n8n helpers



**Recommendation**: Use **Python (Beta)** for better n8...
(truncated)

- [JavaScript/TypeScript] Use === not == (strict equality prevents type coercion bugs)

## Available Tools (ON-DEMAND only)
- `sys_core_01(q)` — Deep search when stuck
- `sys_core_05(query)` — Full-text lookup
> Context above IS your context. Do NOT call sys_core_14() at startup.
