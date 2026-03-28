# OpenBrain Update Ledger

> **Purpose:** An append-only log of all significant changes to the OpenBrain system. When a directive is fixed, a script is updated, or the architecture changes, log it here.
> Never delete entries. Add new entries at the top.

---

## Log Format

```
### [YYYY-MM-DD] — [Type] — [Short title]
- **What changed:** (what was modified and where)
- **Why:** (what broke or what was learned)
- **Directive updated:** (yes/no — which directive was updated)
- **Tested:** (yes/no — how it was verified)
```

**Change types:** `FIX` · `FEATURE` · `ARCHITECTURE` · `DIRECTIVE` · `SCHEMA` · `CONFIG`

### [2026-03-28] — ARCHITECTURE — Directus deployed; all GOBI infra migrated to Zo
- **What changed:**
  - GOBI webhook migrated from MacBridge Docker → Zo supervisord (`gobi-webhook` program, port 8769)
  - SQLite DB canonical location moved to Zo: `/home/workspace/OPENBRAIN/openbrain.db`
  - Datasette replaced by Directus — deployed at `/home/workspace/directus/` on Zo via npm/Node.js
  - Directus runs via supervisord `directus` program on port 8922, public at `data.techstruction.co`
  - Directus bootstrapped with SQLite: `directus_*` system tables created alongside `items`, `inbox_log`, `digests`
  - All three collections auto-detected and CRUD-enabled in Directus admin UI
  - MacBridge `openbrain_agent` container now idle — can be stopped
- **Why:** Architecture required Zo to be the cloud brain for all data/UI; MacBridge is on-prem only
- **Directive updated:** No directive changes — operational deployment only
- **Tested:** `https://gobi.techstruction.co/health` → `{"status":"ok"}` ✅; `https://data.techstruction.co/server/health` → `{"status":"ok"}` ✅; items query via Directus API returns correct data ✅

### [2026-03-28] — ARCHITECTURE — SQLite DB + GOBI Pipeline Rebuild
- **What changed:**
  - Replaced all per-domain JSONL/CSV files with a single SQLite database (`openbrain.db`) on MacBridge at `/home/tonyg/GzOpenBrain/openbrain.db`
  - New `execution/db.py` — unified data access layer (CRUD, domain-scoped queries, no direct DB writes elsewhere)
  - Rewrote `execution/telegram_webhook.py` — removes all Affine references; new flow: inbox_log → Sorter → Bouncer → items table → Telegram receipt
  - Updated `execution/classify_message.py` — KIMI_API_KEY → NVIDIA_API_KEY, model → meta/llama-3.3-70b-instruct, domain name normalization
  - New `execution/migrate_to_db.py` — one-time migration of CAPITAL/COMPUTERS/CARS/CANNAPY/CLAN JSONL + CSV → SQLite (38 records)
  - Datasette deployed as `gobi_datasette` Docker container on MacBridge port 8922, public at `data.techstruction.co`
  - `.env.example` updated: KIMI_* → NVIDIA_*, Affine vars removed, GOBI bot + SQLite path added
  - OPENBRAIN alias folders (COMP/CAP/CANN) deleted from Zo — canonical 5C folders remain
  - `directives/sorter.md` and `directives/bouncer.md` updated to reflect SQLite routing
- **Why:** CSV/JSONL per domain made cross-domain queries impossible and VP agent access inconsistent. SQLite + Datasette provides a single source of truth with zero-config table views for human review.
- **Directive updated:** Yes — `directives/sorter.md`, `directives/bouncer.md`
- **Tested:** Yes — End-to-end: sent "I have an idea for Claude code based market agent" to @GzOpenBrainInbox_bot → classified COMPUTERS/Ideas → "Claude Code Market Agent" → filed to items table → visible at data.techstruction.co


### [2026-03-23] — ARCHITECTURE — NemoClaw Persistent Deployment Complete (K3s Hybrid + Telegram + Ollama)
- **What changed:**
  - **Deployment (3 failed strategies, 1 success):**
    - ❌ Attempt 1: Vanilla K3s Sandbox — data lost on every pod restart (89 circular attempts).
    - ❌ Attempt 2: Standalone Docker Compose — gateway started but Cloudflare returned 502 (OpenShell CRD only routes K3s pods).
    - ❌ Attempt 3: K3s Sandbox with manual file persistence — `hostPath` volume inode decoupling caused config drift.
    - ✅ **Final: Hybrid K3s Sandbox** — K3s pod triggers OpenShell Traefik ingress for Cloudflare routing, `hostPath` volume mounts bind `/sandbox/.openclaw/` → `/home/tonyg/GzOpenBrain/open-claw/` for true persistence. Gateway runs OpenClaw v2026.3.11 on port 18789.
  - **Dashboard Bypass:**
    - The web dashboard (`nemoclaw-macbridge.techstruction.co`) hit a permanent `v2026.3.11` pairing deadlock (close code 4008, `device.pair.create` never called by frontend). Tested across Chrome, Incognito, iPhone Safari — all identical failure.
    - **Pivoted to Telegram** as the primary interface. Enabled the `telegram` channel plugin, connected bot `@OG_Datadogs_bot` (token `8718754783:...`), approved user `7645251071` via `openclaw pairing approve telegram PRMA9PS4`.
  - **AI Engine:**
    - Connected remote Ollama instance (`https://ollama-mbp.techstruction.co`) running `llama3.1` as the default model.
    - Used `openclaw onboard --non-interactive --auth-choice ollama --custom-base-url ... --custom-model-id llama3.1 --accept-risk` to properly register credentials in persistent `auth-profiles.json`.
  - **Decommissioned systems:**
    - Removed all Docker Compose NemoClaw artifacts (`Dockerfile.gateway`, `docker-compose.yml` in `NemoClaw/`).
    - Confirmed HiClaw fully removed (previous session).
    - Affine database services fully decommissioned (previous session).
    - **memU memory system retained** — still operational for persistent agent memory.
  - **Active stack on macbridge:**
    - NemoClaw (K3s Sandbox `nemoclaw` in `openshell` namespace) — OpenClaw v2026.3.11
    - Telegram channel (`@OG_Datadogs_bot`) — primary human interface
    - Ollama (`ollama-mbp.techstruction.co`) — llama3.1 inference engine
    - memU — persistent memory layer
    - Zo Computer — centralized agentic data repository (replacing Affine)
- **Why:** NemoClaw replaces HiClaw and the custom Docker-based OpenClaw as the unified orchestration layer. Telegram replaces the broken web dashboard. Zo Computer replaces Affine as the filing/storage backend.
- **Directive updated:** Yes — `SELF_HEALING.md` (5 new case studies), `MASTER_PLAN.md` (Stage 9 updated)
- **Tested:** Yes — Telegram bot responds to messages powered by Llama 3.1 via remote Ollama. Persistent config survives daemon restarts.

### [2026-03-21] — ARCHITECTURE — Tech Stack Pivot (Affine to Zo Computer)
- **What changed:**
  - Decommissioned and removed entire Affine installation, hub, and services.
  - Removed `affine_net` and related routing from `docker-compose.yml` and `Caddyfile`.
  - Shifted storage and agentic functions to **Zo Computer**.
  - Updated `MASTER_PLAN.md` and core directives to reflect the change.
- **Why:** Affine integration proved difficult; switching to Zo Computer for its built-in agentic and dataset support.
- **Directive updated:** Yes — `MASTER_PLAN.md`, `system_architecture.md`, `filing_cabinet.md`
- **Tested:** N/A — Infrastructure cleanup and roadmap update.

### [2026-03-18] — ARCHITECTURE — NemoClaw Transition & Notes Security
- **What changed:**
  - Began transition from HiClaw to NemoClaw for stage 9 orchestration.
  - Downloaded `nemoclaw.sh` installer and cloned `NemoClaw` repository to repo root.
  - Updated `MASTER_PLAN.md` Stage 9 to reflect NemoClaw and new security policies.
- **Why:** Replaced HiClaw with NemoClaw as requested. NotebookLM revealed requirement for network guardrails (whitelisting `applenotes.losguerreros.com`) for notes access.
- **Directive updated:** Yes — `MASTER_PLAN.md`
- **Tested:** Yes — Verified download and clone.

### [2026-03-18] — ARCHITECTURE — Decommissioned HiClaw Installation
- **What changed:**
  - Removed `hiclaw-manager` container and installation files from MacBridge VPS.
  - Reverted `Caddyfile` to remove HiClaw/Matrix routing.
  - Deleted local `HICLAW_USER_MANUAL.md` and `hiclaw_config.json`.
  - Reverted `MASTER_PLAN.md` Stage 9 to planned status.
- **Why:** The HiClaw framework proved too complex/challenging for current project needs; reverted to the standard 3-layer architecture.
- **Directive updated:** Yes — `directives/agent_roster.md` (reverted logically)
- **Tested:** Yes — Verified container removal and Caddy reload on the server.

### [2026-03-15] — ARCHITECTURE — Initialized HiClaw Migration
- **What changed:**
  - Created `HiClaw-upgrade` branch.
  - Drafted `hiclaw_config.json` defining Architect (Manager) and Scribe, Engineer, Foreman (Workers).
  - Created `execution/hi_claw_skill_sync.py` and synced 16 core scripts to `open-claw/skills/openbrain_core`.
  - Created `execution/migrate_to_hiclaw.py` and synced codebase to `macbridge` VPS.
- **Why:** To evolve from a custom 3-layer orchestration to a native Manager-Worker model with Matrix-based observability and human-in-the-loop coordination.
- **Directive updated:** Yes — `directives/agent_roster.md` (role mapping)
- **Tested:** Yes — Skill synchronization verified; VPS filesystem sync successful.

### [2026-03-15] — FEATURE — Optimized Excalidraw Skill Triggering
- **What changed:**
  - Updated `SKILL.md` frontmatter with a more "pushy" description to override built-in `canvas` tools.
  - Added a "Triggering Priority" section to the skill body to explicitly warn against using competing native tools.
  - Restarted the `open-claw` container on `macbridge` to apply instructions.
- **Why:** The bot was defaulting to a built-in `canvas` tool which failed due to missing mobile node context.
- **Directive updated:** Yes — `open-claw/skills/excalidraw-builder/SKILL.md`
- **Tested:** Yes — Deployment and container restart verified.

### [2026-03-15] — FEATURE — Migrated Excalidraw Skill to Macbridge
- **What changed:**
  - Packaged Excalidraw skill into `open-claw/skills/excalidraw-builder/`.
  - Updated `open-claw/Dockerfile` to install `python3-pip`, `Excalidraw_Interface`, and `pillow`.
  - Refined `SKILL.md` instructions with file retrieval details and corrected execution paths.
  - Deployed to `macbridge` VPS and verified dependencies inside the container.
- **Why:** To enable the OpenClaw agent to generate diagrams and visualizations on the production server.
- **Directive updated:** Yes — `open-claw/skills/excalidraw-builder/SKILL.md`
- **Tested:** Yes — Verified `Excalidraw_Interface` and `PIL` imports in the `openbrain_openclaw` container.

---
### [2026-03-13] — CONFIG — Configured SMTP for email invites
- **What changed:**
  - Added SMTP configuration variables (`MAILER_HOST`, `MAILER_PORT`, `MAILER_USER`, `MAILER_PASSWORD`, `MAILER_SENDER`, `MAILER_SECURE`) to the root `.env` and `storage/affine/.env`.
  - Configured for Gmail (`smtp.gmail.com`) using `techstruction.co@gmail.com`.
- **Why:** To enable email invites and notifications in the self-hosted Affine instance.
- **Directive updated:** No (infrastructure config update)
- **Tested:** Yes — Verified email delivery to `tony.guerrero@gmail.com` using Port 465 (SSL). Updated both `.env` files to Port 465 and `MAILER_SECURE=true` for better reliability.

### [2026-03-13] — CONFIG — Fixed macbridge SSH and Affine connectivity
- **What changed:**
  - Updated `~/.ssh/config` for `macbridge` to use Cloudflare Tunnel (`macbridge-ssh.techstruction.co`) and `cloudflared` ProxyCommand.
  - Updated `AFFINE_API_URL` in `.env` from local IP (`192.168.1.87`) to public URL (`https://affine-macbridge.techstruction.co`).
- **Why:** To enable off-premise communication with the macbridge VPS, replacing local IP addresses with public Cloudflare Tunnel routes.
- **Directive updated:** No (infrastructure config fix)
- **Tested:** Yes — Verified SSH connectivity with `ssh macbridge hostname` and Affine API via `curl`.

### [2026-03-12] — FEATURE — OpenClaw Self-Healing & Updating System
- **What changed:** 
  - Created `execution/check_openclaw_status.py` for version and health monitoring.
  - Created `execution/apply_openclaw_update.py` for non-interactive Docker-based updates.
  - Created `execution/heal_openclaw.py` with tiered troubleshooting (restart -> diagnose -> reasoning fix).
  - Created `directives/openclaw_system.md` to define the 3-layer maintenance policy.
- **Why:** To address frequent OpenClaw updates and security requirements while maintaining human-in-the-loop control for high-stakes actions.
- **Directive updated:** Yes — `directives/openclaw_system.md`
- **Tested:** Yes — Verified version detection and container status check; confirmed update availability (2026.3.11).

---

### [2026-03-10] — CONFIG — Stage 2 Storage Layer established (Self-hosted Affine)
- **What changed:** 
  - Installed **OrbStack** as the Docker runtime.
  - Deployed self-hosted **Affine** instance using Docker Compose on port `3110`.
  - Configured production workspace `GzOpenBrain` (`00925943-6237-425b-b3a2-5641b75f568f`).
  - Set up `tony.guerrero@gmail.com` as primary Admin and enabled cloud sync.
  - Linked `tony@openbrain.local` as Collaborator to grant existing API token access.
  - Updated main `.env` with `AFFINE_API_URL`, `AFFINE_API_TOKEN`, and `AFFINE_WORKSPACE_ID`.
- **Why:** To provide the permanent, private storage layer for the OpenBrain system as specified in Stage 2.
- **Directive updated:** Yes — `MASTER_PLAN.md` (Stage 2 marked complete)
- **Tested:** Yes — Manual UI check via browser subagent and workspace access verified.

### [2026-03-10] — ARCHITECTURE — Agent Roster nomenclature update (Techstruction brand)
- **What changed:** Renamed agent roster from service-proximate names (Manus, Lovable, Zapper) to Techstruction-aligned roles: **Scribe** (Researcher), **Engineer** (Builder), **Foreman** (Routing & Logistics), and **Architect** (Orchestrator). Updated `MASTER_PLAN.md`, `AGENTS.md`, and `directives/agent_roster.md`.
- **Why:** Align system identity with the parent organization "Techstruction" and move away from product-specific naming conventions.
- **Directive updated:** Yes — `directives/agent_roster.md`
- **Tested:** N/A — nomenclature change verified across all core documents.

---

### [2026-03-09] — ARCHITECTURE — Initial OpenBrain system design established
- **What changed:** Created `MASTER_PLAN.md`, `UPDATE_LEDGER.md`, `directives/openbrain_principles.md`, `directives/system_architecture.md`, `directives/agent_roster.md`
- **Directive updated:** Yes — `directives/openbrain_principles.md` (new)
- **Tested:** N/A — foundation stage

---

*Entries above this line are the most recent.*
