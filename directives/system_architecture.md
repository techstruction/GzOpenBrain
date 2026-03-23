# Directive: System Architecture

> **Last updated:** 2026-03-09

---

## The 5 Domains

All information in OpenBrain is organized under five top-level domains. Each domain is a separate repository in **Zo Computer** and uses the same internal sub-category structure.

| Domain | Alias | Scope |
|---|---|---|
| **Capital** | Cash / Charts | Finance, trading, investments, cash management |
| **Computers** | Tech | AI tools, servers, scripts, codebases, dev projects |
| **Cars** | — | Automotive research, parts, projects |
| **Cannapy** | — | Domain-specific research and operations |
| **Clan** | Personal | Family, relationships, health, personal development |

### Sub-Categories (shared across all domains)
- **People** — contacts and relationships relevant to this domain
- **Projects** — active or planned work
- **Ideas** — unvalidated thoughts, research seeds
- **Admin** — documents, processes, logistics
- **Inbox Log** — audit trail of everything classified into this domain

---

## The 8 Building Blocks

### 1. Dropbox (Capture)
**Tool:** Telegram channel / bot
**What it does:** Single point of input. User drops any raw text, link, screenshot, or forward.
**Rule:** Must require zero friction. One gesture = done.

### 2. Sorter (Classifier)
**Tool:** Kimi k2.5 or Ollama (Qwen 3.5)
**What it does:** Reads the incoming message and determines:
- Which **domain** it belongs to (Capital / Computers / Cars / Cannapy / Clan)
- Which **sub-category** (People / Projects / Ideas / Admin)
- Optional: urgency, tags
**Output:** Structured JSON matching the Form schema

### 3. Form (Schema / Data Contract)
Defines the required structure for all classified entries. Kept minimal (3–5 fields max).
```json
{
  "domain": "string",
  "category": "string",
  "title": "string",
  "summary": "string",
  "source_raw": "string",
  "tags": ["string"],
  "created_at": "ISO8601"
}
```

### 4. Filing Cabinet (Storage)
**Tool:** Zo Computer (Scalable agentic data repository)
**What it does:** Stores classified entries in the correct domain repository.
**Note:** Built-in functions handle agents and various datasets out of the box.
**One Zo repository per domain. One dataset per sub-category.**

### 5. Receipt (Audit Trail)
Every item classified and stored generates an entry in the relevant domain's **Inbox Log** table. This is the paper trail.
Fields: `timestamp`, `raw_input`, `classified_as`, `stored_where`, `bouncer_decision`

### 6. Bouncer (Quality Gate)
**What it does:** Reviews the Sorter's output *before* writing to storage. If the entry is:
- Too vague to be useful
- A duplicate
- Below quality threshold
→ Routes to **Inbox Log** with `bouncer_decision: flagged` for human review rather than silently mis-filing.
**Script:** `execution/bouncer_check.py`

### 7. Tap on the Shoulder (Proactive Surfacing)
**Tool:** Comfy UI (automation) → Telegram output
**What it does:** Generates proactive digests on a schedule.
- **Daily:** Top 3 actionable items from yesterday's captures + any flagged items needing review
- **Weekly:** Summary across all domains, recurring themes, suggested next actions
- **Monthly (optional):** Trend summary, stale projects to prune

### 8. Fix Button (Human-in-the-Loop)
**What it does:** Allows user to correct the system via a simple Telegram reply.
Examples:
- "Move this to Cars, not Computers"
- "This is low quality, remove it"
**Script:** `execution/apply_correction.py`
Corrections also update the Bouncer's learned patterns over time.

---

## Pipeline Flow

```
User Message (Telegram)
   ↓
Comfy UI Trigger
   ↓
Sorter Agent (Kimi / Ollama)
   → Classify to domain + category
   → Output structured JSON (Form)
   ↓
Bouncer (Quality Check)
   → PASS → Filing Cabinet (Affine)
   → FLAG → Inbox Log (for human review)
   ↓
Receipt written to Inbox Log
   ↓
[Scheduled] Digest → Telegram
```

---

## Directory Structure

```
GzOpenBrain/
├── AGENTS.md               # Root orchestration instructions
├── MASTER_PLAN.md          # Build roadmap + stage checklist
├── UPDATE_LEDGER.md        # Append-only change log
├── directives/             # SOPs for each component
│   ├── openbrain_principles.md
│   ├── system_architecture.md (this file)
│   ├── agent_roster.md
│   ├── sorter.md           (Stage 1)
│   ├── filing_cabinet.md   (Stage 2)
│   ├── bouncer.md          (Stage 3)
│   ├── intelligence_layer.md (Stage 4)
│   ├── digest.md           (Stage 5)
│   ├── correction.md       (Stage 6)
│   └── meta_agent.md       (Stage 7)
├── execution/              # Deterministic Python scripts
│   ├── classify_message.py
│   ├── write_to_zo.py      (Planned)
│   ├── bouncer_check.py
│   ├── generate_digest.py
│   └── apply_correction.py
├── .env                    # API keys, model selection, config
└── .tmp/                   # Temporary processing files (never commit)
```
