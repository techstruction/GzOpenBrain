# Directive: Agent Roster

> **Last updated:** 2026-03-09

---

## Overview

The OpenBrain system uses four primary agents. Each has a defined role, toolset, and interaction protocol. The Architect orchestrates all others.

---

## Architect (Orchestrator)

**Role:** Reads directives, makes routing decisions, handles errors, runs quality loops.
**This is you (the AI assistant)** when operating under `AGENTS.md`.

**Responsibilities:**
- Receives raw task or message
- Selects appropriate specialist agent or execution script
- Runs the Writer-Critic loop (generate → verify)
- Handles errors via the Self-Heal Protocol (see `openbrain_principles.md`)
- Updates directives with new learnings
- Appends to `UPDATE_LEDGER.md` on significant changes

**Coordination protocol:**
1. Read the relevant directive in `directives/`
2. Determine inputs and outputs
3. Invoke the correct `execution/` script or specialist agent
4. Validate output (Bouncer, quality check)
5. If error: fix → test → update directive → log
6. Return clean output

---

## Scribe (Researcher)

**Role:** Web research, source gathering, NotebookLM queries
**Primary tools:** Web scraping scripts, NotebookLM skill, search APIs

**When invoked:**
- User requests research on a topic
- Sorter flags an item needing external context
- Weekly digest generation requires fresh data

**Output contract:**
- Always provides source citations ("Skills + Evidence Layer")
- Outputs structured JSON: `{summary, sources[], key_points[]}`
- Never fabricates — if source not found, says so

**Self-heal rule:** If a research script fails, diagnose, fix, test, update `directives/sorter.md` or relevant directive with new API constraints.

---

## Engineer (Builder)

**Role:** Code generation, UI flows, Comfy UI pipeline construction
**Primary tools:** Code execution, Comfy UI configuration, Affine schema setup

**When invoked:**
- New execution script needs to be built
- Comfy UI automation flow requires modification
- Affine database schema needs updating

**Output contract:**
- All scripts are placed in `execution/`
- Scripts are well-commented
- Scripts include basic error handling and logging
- After building: test locally → update relevant directive → log in `UPDATE_LEDGER.md`

**Self-heal rule:** If a built script breaks in production, the Engineer rebuilds it with the fix, tests it, and updates the directive that references it.

---

## Foreman (Routing & Logistics)

**Role:** Automation orchestration, message routing, scheduling
**Primary tools:** Comfy UI (automation), Telegram bot API, Affine API

**When invoked:**
- New Comfy UI flow needs to be configured
- Digest schedule needs updating
- Telegram webhook changes
- Correction (Fix Button) from user arrives

**Output contract:**
- All automation flows documented in relevant directive
- Scheduling parameters stored in `.env`
- Any Telegram → Affine routing logic documented in `directives/`

**Self-heal rule:** If an automation flow breaks (e.g., Telegram webhook fails), the Foreman diagnoses, fixes the flow, tests with a sample message, and updates `directives/correction.md` or relevant directive.

---

## Intelligence Backend Selection

| Backend | Use When | Notes |
|---|---|---|
| **Kimi k2.5** (Nvidia API) | Primary, when key is available | May be slower due to Thinking mode — disable Thinking for classification tasks if latency is an issue |
| **Ollama (Qwen 3.5)** | Fallback / cost-zero option | Runs on local Windows server. Best for high-volume classification |

**Config:** Model selection is controlled via `.env`:
```env
INTELLIGENCE_BACKEND=kimi  # or: ollama
KIMI_API_KEY=your_key_here
OLLAMA_HOST=http://your-windows-server:11434
OLLAMA_MODEL=qwen3.5
```

**Self-heal rule:** If the primary backend fails, automatically fall back to the secondary. Log the failure in `UPDATE_LEDGER.md` and alert user via Telegram.

---

## Writer-Critic Loop

When reliability matters (e.g., classification, digest generation):
1. **Writer agent** generates output
2. **Critic agent** (Architect) independently reviews:
   - Is the domain classification correct?
   - Does the summary accurately represent the source?
   - Is the quality threshold met for storage?
3. If Critic disagrees → revise → re-check (max 2 loops)
4. If still uncertain → route to Inbox Log with flag for human review

---

## Related Files
- `AGENTS.md` — Root orchestration instructions
- `directives/openbrain_principles.md` — Core principles including Self-Heal Protocol
- `directives/system_architecture.md` — Component breakdown and pipeline
- `MASTER_PLAN.md` — Stage-by-stage build roadmap
- `UPDATE_LEDGER.md` — Append-only change log
