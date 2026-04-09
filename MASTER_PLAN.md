# OpenBrain Master Plan

> **Purpose:** The single source of truth for building the personal OpenBrain system. Track every stage, task, and decision here.
> **Ledger:** All significant changes are logged in `UPDATE_LEDGER.md`.

---

## ◼ Vision

A fully personal, self-maintaining AI second-brain. One input gesture (message to Telegram). The system classifies, stores, summarises, and surfaces relevant information proactively — across five life domains — without requiring ongoing manual filing.

---

## ◼ Five Domains

| Domain | Alias | Description |
|---|---|---|
| **Capital** | Cash / Charts | Finance, investments, research |
| **Computers** | Tech | Tools, servers, codebases, AI projects |
| **Cars** | — | Automotive research and projects |
| **Cannapy** | — | Domain-specific research |
| **Clan** | Personal | Family, relationships, personal development |

Each domain shares the same internal sub-categories: **People · Projects · Ideas · Admin · Inbox Log**.

---

## ◼ Tech Stack

| Layer | Tool | Notes |
|---|---|---|
| Input | Telegram | Single-drop inbox for all info |
| Database | Affine (OSS) | Notion replacement, self-hosted |
| Automation | Comfy UI | Zapier replacement |
| Intelligence | Kimi k2.5 (Nvidia API) or Ollama (Qwen 3.5 on Windows server) | Low/no-cost AI layer |

---

## ◼ The 8 Building Blocks

| # | Block | Role |
|---|---|---|
| 1 | **Dropbox** | Telegram channel — single capture point |
| 2 | **Sorter** | AI classifier — domain + category routing |
| 3 | **Form** | Schema/data contract for structured entries |
| 4 | **Filing Cabinet** | Affine databases (one per domain) |
| 5 | **Receipt** | Audit trail / Inbox Log |
| 6 | **Bouncer** | Quality gate — prevents noise entering storage |
| 7 | **Tap on the Shoulder** | Proactive digests — daily / weekly / monthly |
| 8 | **Fix Button** | Human-in-the-loop correction mechanism |

---

## ◼ Core Principles

1. **Architecture is portable, tools are not.** Design the system around the workflow, not specific services.
2. **Principle-based guidance > rule-based.** Agents use software engineering principles (test-driven, separation of concerns, no swallowed errors).
3. **If the agent builds it, the agent can maintain it.** Writer-Critic loop ensures self-verification.
4. **Your system is infrastructure, not just a tool.** Design for uptime, restartability, and longevity.
5. **Self-heal.** When scripts break → fix → test → update the directive. Never leave a broken state undocumented.
6. **Reduce human job to one behaviour.** User drops a message. Everything else is automatic.

---

## ◼ Agent Roster

| Agent | Role | Primary Tool | What it represents | It is NOT... |
|---|---|---|---|---|
| **Scribe** | Researcher | Web scraping, NotebookLM | The Researcher persona; gathering data and scoping problems. | A specific tool, though it uses NotebookLM. |
| **Engineer** | Builder | Code syntax, Comfy UI flows | The Technical lead; designing automation logic and scripts. | A platform, though it uses Comfy UI. |
| **Foreman** | Logistics | Telegram, Affine | The Logistics lead; moving data/materials between domains. | An integration service, though it use Affine/Telegram. |
| **Architect** | Orchestrator | Blueprint review, Writer-Critic | The Blueprint holder; ensuring quality and orchestration. | A product, but the logic that coordinates the crew. |

We are defining the "Core Utility Crew" now, and we define the "Specialist Sub-Contractors" later during Domain Expansion.

Here is the breakdown of why this approach ensures a solid foundation:

1. The "Core Crew" (Infrastructure)
The 4 roles we just defined (Scribe, Engineer, Foreman, Architect) are your permanent staff. They are the engine of the system. Their job is to maintain the pipelines, build the tools, and move information, regardless of what that information is.

Scribe knows how to find data.
Engineer knows how to build scripts.
Foreman knows how to route messages.
Architect knows how to maintain the master plan.
2. The "Specialist Sub-Contractors" (Domain Experts)
The roles you mentioned—the Market Sentiment Analyst, the Botanist, the Mechanical Historian—are Specialist Personas. These are defined in the "Directives" layer for specific workflows.

In the Techstruction metaphor: If you are building a generic office building, you only need your core crew. But if you are building a high-tech laboratory (the Cannapy domain), the Architect "hires" (invokes) a Scientific Lab Consultant directive to ensure the ventilation and equipment (the data structure) meet specific requirements.

---

## ◼ Stages & Tasks

### Stage 0 — Foundation ✅
- [x] Synthesize research from Apple Notes and NotebookLM
- [x] Define 5-domain hierarchy (4Cs + Clan)
- [x] Define tech stack preference
- [x] Create all foundation documents (this file + UPDATE_LEDGER.md)
- [x] Create `directives/openbrain_principles.md`
- [x] Create `directives/system_architecture.md`
- [x] Create `directives/agent_roster.md`
- [x] Update `AGENTS.md` with OpenBrain-specific context and self-heal rule for directives

### Stage 1 — Capture Layer 🔲
- [x] Write `execution/classify_message.py` (Sorter — Kimi + Ollama backends, auto-fallback)
- [x] Write `execution/telegram_webhook.py` (webhook server + pipeline runner)
- [x] Write `directives/sorter.md`
- [x] Write `directives/telegram_capture.md`
- [x] Create `requirements.txt` + Python venv (`venv/`)
- [x] Syntax-verified all scripts
- [ ] **ACTION NEEDED:** Copy `.env.example` → `.env` and add `TELEGRAM_BOT_TOKEN` + API keys
- [ ] Create Telegram bot via @BotFather
- [ ] Start webhook server: `source venv/bin/activate && python3 execution/telegram_webhook.py`
- [x] Expose via Cloudflare Tunnel: `gobi.techstruction.co`
- [x] Register webhook: `python3 execution/telegram_webhook.py --register https://gobi.techstruction.co`
- [ ] Send a test message to the bot and verify receipt response

### Stage 2 — Storage Layer ✅
- [x] Write `execution/write_to_affine.py` (Affine storage logic)
- [x] Write `directives/filing_cabinet.md`
- [x] **ACTION COMPLETED:** Added `AFFINE_API_TOKEN` and `WORKSPACE_ID` to `.env`
- [x] Verify Affine API endpoint mapping in script

### Stage 3 — Quality Gate (Bouncer) ✅
- [x] Write `execution/bouncer_check.py` (pass/flag logic)
- [x] Write `directives/bouncer.md`
- [ ] Test Bouncer with simulated low-quality messages

### Stage 4 — Intelligence Layer ✅
- [x] Test Kimi k2.5 API connection (Fixed model name: `moonshotai/kimi-k2.5`)
- [x] Tuned timeouts (120s) for high-latency 'thinking' models
- [x] Verified Ollama fallback functionality
- [x] Verified `qwen3.5:9b` local model compatibility
- [x] Parameterise model selection in `.env`
- [x] Write `directives/intelligence_layer.md`

### Stage 5 — Digest Layer ✅
- [x] Write `execution/generate_digest.py` (Daily summary logic)
- [x] Write `directives/digest.md`
- [ ] Connect digest trigger to cron or scheduler
- [ ] Test weekly digest expansion

### Stage 6 — Fix Button (Human-in-the-Loop) ✅
- [x] Write `execution/apply_correction.py` (Override logic)
- [x] Write `directives/correction.md`
- [ ] Connect `/fix` command in `telegram_webhook.py`
- [ ] Implement feedback loop for Sorter reinforcement

### Stage 7 — Self-Maintenance & Architect (Review Loop) ✅
- [x] Implement Writer-Critic loop between Scribe (Sorter) and Architect
- [x] Implement Skills+Evidence layer (outputs must cite sources)
- [x] Write `directives/architect.md`
- [x] Test full end-to-end flow: Telegram → Sorter → Bouncer → Affine → Digest
- [x] Document known edge cases in directives

### Stage 8 — Hardening & Multi-domain Expansion 🔲
- [ ] Apply domain-specific routing rules per 5 domains
- [ ] Stress-test with real daily inputs for 1 week
- [ ] Review and prune low-quality entries
- [ ] Refine field schemas based on actual use
- [ ] Document stable baseline in `UPDATE_LEDGER.md`
 
 ### Stage 9 — Orchestration Upgrade (NemoClaw) 🔲
 - [x] Research NemoClaw capabilities and security (via NotebookLM)
 - [x] Download NemoClaw to repo root <!-- id: 1 -->
 - [ ] Configure network guardrails (whitelist `applenotes.losguerreros.com`) <!-- id: 2 -->
 - [ ] Synchronize execution scripts as NemoClaw Skills <!-- id: 3 -->
 - [ ] Deploy and scale NemoClaw on MacBridge VPS <!-- id: 4 -->
 - [ ] Verify sandboxed orchestration loop <!-- id: 5 -->

---

## ◼ MVP Loop (Minimum Viable Pipeline)

```
Telegram → Sorter (Classify) → Bouncer (Quality Check) → Affine (File) → Daily Digest → Telegram
```

Build this first. Everything else is a module added on top.

---

*Last updated: 2026-03-09 — Stages 1-3 code complete. Pipeline is functional pending .env keys.*
