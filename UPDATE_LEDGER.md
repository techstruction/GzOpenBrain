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

### [2026-03-14] — FEATURE — Upgraded OpenClaw with Skill Creator ability
- **What changed:**
  - Created `open-claw/skills/skill-creator` directory.
  - Copied `skill-creator` files and renamed `SKILL_skillcreator.md` to `SKILL.md` for OpenClaw compatibility.
  - Deployed to `macbridge` VPS and verified skill registration via `openclaw skills list`.
- **Why:** To give the OpenClaw agent the ability to create and optimize its own skills as requested by the user.
- **Directive updated:** No
- **Tested:** Yes — Verified with `openclaw skills info skill-creator` inside the `openbrain_openclaw` container.

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
  - Configured production workspace `GzOpenBrain` (`1142150e-fc29-4e8e-b5af-181cd8a7283c`).
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
- **Why:** Synthesized research from Apple Notes and NotebookLM to define the full OpenBrain architecture.
- **Key decisions:**
  - Five-domain hierarchy: Capital, Computers, Cars, Cannapy, Clan
  - Tech stack: Telegram + Affine (OSS) + Comfy UI + Kimi k2.5 / Ollama (Qwen 3.5)
  - Eight building blocks: Dropbox, Sorter, Form, Filing Cabinet, Receipt, Bouncer, Tap on the Shoulder, Fix Button
  - Principle-based guidance > rule-based guidance
  - Self-annealing directive: fix → test → update directive
- **Directive updated:** Yes — `directives/openbrain_principles.md` (new)
- **Tested:** N/A — foundation stage

---

*Entries above this line are the most recent.*
