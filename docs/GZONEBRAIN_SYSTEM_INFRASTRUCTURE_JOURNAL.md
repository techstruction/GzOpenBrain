# GzOpenBrain System Infrastructure Journal

> **Purpose:** The definitive technical reference for the entire GzOpenBrain system. Contains every server, application, network route, port binding, script, file path, and configuration parameter required to understand, maintain, and rebuild the infrastructure.  
> **Last updated:** 2026-03-23  
> **Status:** Active — Zo Computer era (post-Affine migration)

---

## System Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           INTERNET / CLOUDFLARE                              │
│                                                                              │
│   *.techstruction.co Domains (Cloudflare DNS + Tunnel)                       │
│   ┌─────────────────────────────────────────────────────────┐                │
│   │  nemoclaw-macbridge.techstruction.co ──► K3s Traefik    │                │
│   │  ollama-mbp.techstruction.co ─────────► Ollama (MBP)    │                │
│   │  macbridge-ssh.techstruction.co ──────► SSH (port 22)   │                │
│   └─────────────────────────────────────────────────────────┘                │
│                              │                                               │
│                    Cloudflare Tunnel (cloudflared)                            │
│                              │                                               │
├──────────────────────────────┼───────────────────────────────────────────────┤
│                              ▼                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                    macbridge Server                                   │   │
│   │                    Hostname: macbridge                                │   │
│   │                    LAN IP: 192.168.1.87                              │   │
│   │                    User: tonyg                                        │   │
│   │                                                                       │   │
│   │   ┌─────────────────────────────────────────────────────────────┐     │   │
│   │   │  K3s Cluster (managed by OpenShell)                         │     │   │
│   │   │                                                             │     │   │
│   │   │  Pod: nemoclaw (ns: openshell)                              │     │   │
│   │   │  ├── OpenClaw v2026.3.11 Gateway (:18789)                   │     │   │
│   │   │  ├── Telegram Channel (@OG_Datadogs_bot)                    │     │   │
│   │   │  ├── AI Engine: ollama/llama3.1                             │     │   │
│   │   │  └── hostPath: /sandbox/.openclaw ↔ host:open-claw/        │     │   │
│   │   │                                                             │     │   │
│   │   │  Traefik Ingress (auto-managed by OpenShell CRD)            │     │   │
│   │   │  └── Routes: nemoclaw-macbridge.techstruction.co → :18789   │     │   │
│   │   └─────────────────────────────────────────────────────────────┘     │   │
│   │                                                                       │   │
│   │   ┌─────────────────────────────────────────────────────────────┐     │   │
│   │   │  Docker Compose Services                                    │     │   │
│   │   │  ├── caddy-proxy (:80, :443) — Reverse proxy               │     │   │
│   │   │  ├── openbrain_hub (:3030) — MCP Affine Hub (legacy)       │     │   │
│   │   │  ├── openbrain_memu (:8001) — memU Memory System           │     │   │
│   │   │  └── openbrain_adminer (:9090) — DB Admin (legacy)         │     │   │
│   │   └─────────────────────────────────────────────────────────────┘     │   │
│   │                                                                       │   │
│   │   /home/tonyg/GzOpenBrain/                                            │   │
│   │   └── (Project root — mirrored from local Mac)                        │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                    Local Mac (Development)                            │   │
│   │                    User: tonyg                                        │   │
│   │                    Project: /Users/tonyg/Documents/GzOpenBrain        │   │
│   │                                                                       │   │
│   │   SSH → macbridge (via cloudflared ProxyCommand)                      │   │
│   │   Ollama Server: ollama-mbp.techstruction.co (local Ollama)          │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌──────────────────────────────────────────────────────────────────────┐   │
│   │                    External Services                                  │   │
│   │                                                                       │   │
│   │   Zo Computer — Centralized agentic data repository (replaces Affine)│   │
│   │   Telegram Bot API — @OG_Datadogs_bot (primary human interface)      │   │
│   │   Nvidia NIM API — Kimi k2.5 inference (intelligence fallback)       │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Servers & Machines

### macbridge (Production Server)

| Property | Value |
|----------|-------|
| **Hostname** | `macbridge` |
| **LAN IP** | `192.168.1.87` |
| **Docker Bridge IPs** | `172.80.0.1` through `172.80.5.1` |
| **OS** | Linux (Mac Mini or equivalent, running K3s + Docker) |
| **SSH User** | `tonyg` |
| **SSH Access** | Via Cloudflare Tunnel: `macbridge-ssh.techstruction.co` |
| **Project Root** | `/home/tonyg/GzOpenBrain/` |
| **OpenShell CLI** | `~/.local/bin/openshell` |
| **NemoClaw Data** | `/home/tonyg/GzOpenBrain/open-claw/` |
| **Backups** | `/home/tonyg/GzOpenBrain/.nemoclaw-backups/` |

### Local Mac (Development Workstation)

| Property | Value |
|----------|-------|
| **User** | `tonyg` |
| **Project Root** | `/Users/tonyg/Documents/GzOpenBrain/` |
| **SSH Config Host** | `macbridge` |
| **SSH Hostname** | `macbridge-ssh.techstruction.co` |
| **SSH Identity** | `~/.ssh/id_ed25519` |
| **SSH ProxyCommand** | `/opt/homebrew/bin/cloudflared access ssh --hostname %h` |
| **Ollama Server** | Local instance, tunneled via `ollama-mbp.techstruction.co` |

---

## Network Topology

### Cloudflare Tunnel Domains

| Domain | Target | Purpose |
|--------|--------|---------|
| `nemoclaw-macbridge.techstruction.co` | K3s Traefik → pod `nemoclaw` :18789 | NemoClaw OpenClaw Gateway (WebSocket + API) |
| `ollama-mbp.techstruction.co` | Local Mac → Ollama :11434 | Remote Ollama AI inference endpoint |
| `macbridge-ssh.techstruction.co` | macbridge :22 | SSH access via Cloudflare Tunnel |

### K3s Services (namespace: `openshell`)

| Service Name | Type | Cluster IP | Port Mapping | Purpose |
|-------------|------|-----------|--------------|---------|
| `nemoclaw` | ClusterIP | None | — | Headless service for pod DNS |
| `nemoclaw-dashboard` | NodePort | `10.43.251.162` | `18789:31294/TCP` | Gateway WebSocket endpoint |
| `nemoclaw-fixed` | NodePort | `10.43.80.246` | `18789:30799/TCP` | Fixed port gateway binding |
| `nemoclaw-http` | NodePort | `10.43.237.102` | `80:30270/TCP` | HTTP endpoint |
| `openshell` | NodePort | `10.43.142.42` | `8080:30051/TCP` | OpenShell management API |

### Docker Compose Ports (macbridge)

| Container | Host Port | Container Port | Purpose |
|-----------|-----------|---------------|---------|
| `caddy-proxy` | 80, 443 | 80, 443 | Reverse proxy (HTTPS termination) |
| `openbrain_hub` | 3030 | 3030 | MCP Affine Hub (legacy, to be decommissioned) |
| `openbrain_memu` | 8001 | 8001 | **memU Memory System** (active) |
| `openbrain_adminer` | 9090 | 8080 | Database admin UI (legacy) |

### Docker Networks

| Network | Type | Purpose |
|---------|------|---------|
| `openbrain_net` | bridge | Internal communication between OpenBrain services |
| `affine_net` (`affine_default`) | external | Legacy Affine database network (retained for memU) |

---

## Applications & Services

### NemoClaw (Primary Orchestrator)

| Property | Value |
|----------|-------|
| **Version** | OpenClaw v2026.3.11 |
| **Runtime** | K3s Sandbox pod `nemoclaw` in namespace `openshell` |
| **Container Image** | `node:22` (OpenShell-managed) |
| **Gateway Port** | `18789` (bound to `0.0.0.0` via `bind: lan`) |
| **Auth Mode** | Password (`openclaw123`) + Token (`78f92e...`) |
| **Primary Channel** | Telegram (`@OG_Datadogs_bot`) |
| **AI Model** | `ollama/llama3.1` via `https://ollama-mbp.techstruction.co` |
| **Config File** | `/sandbox/.openclaw/openclaw.json` (container) |
| **Config File (host)** | `/home/tonyg/GzOpenBrain/open-claw/openclaw.json` |
| **Agent Dir** | `/sandbox/.openclaw/agents/main/agent/` |
| **Auth Store** | `/sandbox/.openclaw/agents/main/agent/auth-profiles.json` |
| **Skills Dir** | `/sandbox/.openclaw/skills/` |
| **Workspace Dir** | `/sandbox/.openclaw/workspace/` |
| **Memory Dir** | `/sandbox/.openclaw/agents/main/memory/` |
| **Session Logs** | `/sandbox/.openclaw/agents/main/sessions/` |
| **Gateway Logs** | `/tmp/gw_*.log` (inside container) |

**Key Commands:**
```bash
# Start gateway daemon
export PATH=/sandbox/.npm-global/bin:$PATH
nohup openclaw gateway run --allow-unconfigured --verbose > /tmp/gw.log 2>&1 &

# Check model status
openclaw models status

# List channels
openclaw channels list

# Approve a Telegram pairing
openclaw pairing approve telegram <CODE>

# Onboard an Ollama provider
openclaw onboard --non-interactive --auth-choice ollama \
  --custom-base-url https://ollama-mbp.techstruction.co \
  --custom-model-id llama3.1 --accept-risk
```

### Telegram Bot (@OG_Datadogs_bot)

| Property | Value |
|----------|-------|
| **Bot Username** | `@OG_Datadogs_bot` |
| **Bot Display Name** | Datadogs |
| **Bot Token** | `8718754783:AAEyw6y0sfyFff1lXY6TpbJRdojBLCA3-6k` |
| **Approved User ID** | `7645251071` |
| **Pairing Code** | `PRMA9PS4` |
| **DM Policy** | `pairing` (requires CLI approval) |
| **Group Policy** | `allowlist` (groups silently dropped unless explicitly allowed) |
| **Streaming** | `partial` |

### Ollama (AI Inference Engine)

| Property | Value |
|----------|-------|
| **Host** | Local Mac (development workstation) |
| **Public URL** | `https://ollama-mbp.techstruction.co` |
| **Native Port** | `11434` |
| **Model** | `llama3.1` |
| **API Key** | `ollama-local` (placeholder — Ollama has no real auth) |
| **API Type** | `ollama` (native, not OpenAI-compatible `/v1`) |
| **Provider ID in OpenClaw** | `ollama` |
| **Model ID in OpenClaw** | `ollama/llama3.1` |

### memU (Persistent Memory System)

| Property | Value |
|----------|-------|
| **Container** | `openbrain_memu` |
| **Port** | `8001` |
| **Build Context** | `./mcp-memu` |
| **Volumes** | `.env:/app/.env`, `./open-claw:/root/.openclaw` |
| **Status** | **Active** — retained through all migrations |

### Zo Computer (Centralized Data Repository)

| Property | Value |
|----------|-------|
| **Role** | Replaces Affine as the filing cabinet / database layer |
| **Type** | Cloud-based agentic data repository |
| **Integration Status** | Repositories to be initialized (Stage 2 migration in progress) |

---

## File System Layout

### macbridge: `/home/tonyg/GzOpenBrain/`

```
GzOpenBrain/
├── AGENTS.md                       # Agent instruction set (3-layer architecture rules)
├── MASTER_PLAN.md                  # Project roadmap and stage tracker
├── SELF_HEALING.md                 # Debugging case studies and golden rules
├── UPDATE_LEDGER.md                # Append-only change log
├── ARCHITECT_SOP.md                # Standard operating procedure for the Architect agent
├── .env                            # Environment variables (secrets, API keys)
├── .env.example                    # Template for .env
├── .gitignore                      # Git exclusions
├── requirements.txt                # Python dependencies
├── docker-compose.yml              # Docker Compose service definitions
├── nemoclaw.sh                     # NemoClaw installer script
│
├── directives/                     # SOPs (the instruction set for agents)
│   ├── openbrain_principles.md     # Core operating principles
│   ├── system_architecture.md      # 5 domains, 8 building blocks
│   ├── agent_roster.md             # Scribe, Engineer, Foreman, Architect
│   ├── sorter.md                   # Message classification SOP
│   ├── bouncer.md                  # Quality gate SOP
│   ├── filing_cabinet.md           # Zo Computer storage SOP
│   ├── digest.md                   # Daily/weekly digest generation SOP
│   ├── correction.md               # Human-in-the-loop fix SOP
│   ├── architect.md                # Writer-Critic loop SOP
│   ├── scribe.md                   # Research agent SOP
│   ├── telegram_capture.md         # Telegram webhook SOP
│   ├── openclaw_system.md          # OpenClaw maintenance policy
│   ├── edge_cases.md               # Known edge cases and workarounds
│   └── affine_mcp.md               # Legacy Affine MCP integration (deprecated)
│
├── execution/                      # Deterministic Python scripts (Layer 3)
│   ├── classify_message.py         # Sorter — AI classifier (Kimi + Ollama)
│   ├── telegram_webhook.py         # Webhook server + pipeline runner
│   ├── bouncer_check.py            # Quality gate pass/flag logic
│   ├── generate_digest.py          # Daily summary generator
│   ├── apply_correction.py         # Human-in-the-loop override logic
│   ├── architect_critic.py         # Writer-Critic loop implementation
│   ├── scribe_research.py          # Web scraping + research logic
│   ├── agent_dispatcher.py         # Multi-agent routing dispatcher
│   ├── memu_sync.py                # memU memory synchronization
│   ├── deploy_vps.py               # VPS deployment automation
│   ├── check_openclaw_status.py    # OpenClaw version + health check
│   ├── apply_openclaw_update.py    # Non-interactive Docker update
│   ├── heal_openclaw.py            # Tiered self-healing (restart → diagnose → fix)
│   ├── restore_nemoclaw.py         # NemoClaw data recovery utility
│   ├── nanoclaw.py                 # Lightweight local OpenClaw wrapper
│   └── mcp_servers/
│       └── affine_mcp.py           # Legacy Affine MCP server (deprecated)
│
├── open-claw/                      # NemoClaw persistent data (hostPath volume)
│   ├── openclaw.json               # Master configuration
│   ├── openclaw.json.bak           # Auto-backup of previous config
│   ├── update-check.json           # Version check tracker
│   ├── agents/
│   │   └── main/
│   │       ├── AGENTS.md           # Agent identity instructions
│   │       ├── agent/
│   │       │   ├── auth-profiles.json  # API keys (Ollama, etc.)
│   │       │   └── models.json         # Model configuration
│   │       ├── memory/
│   │       │   └── SELF_HEALING.md     # Agent's self-healing knowledge
│   │       └── sessions/
│   │           ├── sessions.json       # Session index
│   │           └── *.jsonl             # Conversation transcripts
│   ├── skills/
│   │   ├── market-price-checker/       # Market price lookup skill
│   │   └── excalidraw-builder/         # Diagram generation skill
│   └── workspace/
│       ├── IDENTITY.md                 # Agent persona
│       ├── USER.md                     # User context
│       ├── SOUL.md                     # Personality and values
│       ├── TOOLS.md                    # Tool registry
│       ├── HEARTBEAT.md               # Health status
│       ├── BOOTSTRAP.md               # First-boot instructions
│       ├── skills/
│       │   ├── market-price-checker/   # Workspace skill copy
│       │   └── skill-creator/          # Skill creation tool
│       └── .openclaw/
│           └── workspace-state.json    # Workspace tracking state
│
├── .nemoclaw-backups/              # Timestamped backup archives
│   └── nemoclaw-backup-*.tar.gz    # Compressed snapshots (last 10 kept)
│
├── NemoClaw/                       # NemoClaw repository clone
│   ├── nemoclaw                    # Main binary/installer
│   └── nemoclaw-blueprint          # Blueprint configuration
│
├── proxy/
│   └── Caddyfile                   # Caddy reverse proxy configuration
│
├── mcp-memu/                       # memU MCP server (Docker build context)
│   ├── Dockerfile
│   └── requirements.txt
│
├── mcp-affine-hub/                 # Legacy Affine MCP hub (deprecated)
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│
├── docs/                           # Project documentation
│   ├── SELF_HEALING.md             # Copy of self-healing protocols
│   ├── NEMOCLAW_DATA_SYNC_MANUAL.md
│   └── GZONEBRAIN_SYSTEM_INFRASTRUCTURE_JOURNAL.md  # ← This file
│
├── storage/                        # Storage configurations
│   └── affine/                     # Legacy Affine storage (deprecated)
│
├── tests/                          # Test scripts
├── venv/                           # Python virtual environment
└── .tmp/                           # Temporary processing files
```

---

## Scripts & Utilities Reference

### Execution Scripts (`execution/`)

| Script | Purpose | Key Dependencies |
|--------|---------|-----------------|
| `classify_message.py` | AI-powered message classification into 5 domains + sub-categories. Supports Kimi k2.5 (Nvidia API) and Ollama backends with automatic fallback. | `KIMI_API_KEY`, `OLLAMA_HOST` |
| `telegram_webhook.py` | Webhook server receiving Telegram messages. Runs the full pipeline: classify → bounce → file → acknowledge. | `TELEGRAM_BOT_TOKEN`, `OPENBRAIN_PORT` |
| `bouncer_check.py` | Quality gate that evaluates incoming messages. Passes high-quality entries, flags low-quality ones for review. | — |
| `generate_digest.py` | Generates daily/weekly summary digests from stored entries across all 5 domains. | Zo Computer API |
| `apply_correction.py` | Human-in-the-loop override. Allows manual reclassification or deletion of entries via `/fix` command. | — |
| `architect_critic.py` | Writer-Critic loop implementation. The Architect reviews Scribe outputs for quality and consistency. | — |
| `scribe_research.py` | Web scraping and research automation. Gathers data from specified sources. | — |
| `agent_dispatcher.py` | Routes tasks to the appropriate agent (Scribe, Engineer, Foreman) based on task type. | — |
| `memu_sync.py` | Synchronizes data between the local project and the memU memory system. | `openbrain_memu` container |
| `deploy_vps.py` | Automates deployment of project files to the macbridge server. | SSH access |
| `check_openclaw_status.py` | Checks current OpenClaw version and container health. | Docker access |
| `apply_openclaw_update.py` | Non-interactive Docker-based OpenClaw update procedure. | Docker access |
| `heal_openclaw.py` | Tiered self-healing: restart container → diagnose → apply reasoning fix. | Docker access |
| `restore_nemoclaw.py` | Recovery utility for NemoClaw data from available backups and host volumes. | SSH to macbridge |
| `nanoclaw.py` | Lightweight local OpenClaw wrapper for development/testing. | — |

### Operational Scripts (macbridge)

| Script | Location | Purpose |
|--------|----------|---------|
| `nemoclaw-sync.sh` | `/home/tonyg/nemoclaw-sync.sh` | Backup and sync all irreplaceable NemoClaw data. See `NEMOCLAW_DATA_SYNC_MANUAL.md`. |
| `nemoclaw.sh` | `/home/tonyg/GzOpenBrain/nemoclaw.sh` | Original NemoClaw installer script. |

### Key kubectl Commands

```bash
# All commands use the OpenShell kubectl proxy:
KUBECTL="~/.local/bin/openshell doctor exec -- kubectl"

# List all pods
$KUBECTL get pods -n openshell

# Exec into NemoClaw
$KUBECTL exec -it nemoclaw -n openshell -- bash

# View gateway logs
$KUBECTL exec nemoclaw -n openshell -- tail -f /tmp/gw_onboarded.log

# Kill gateway daemon (for restart)
$KUBECTL exec nemoclaw -n openshell -- pkill -f openclaw

# Start gateway daemon
$KUBECTL exec -i nemoclaw -n openshell -- bash -c '
export PATH=/sandbox/.npm-global/bin:$PATH
nohup openclaw gateway run --allow-unconfigured --verbose > /tmp/gw.log 2>&1 &
'
```

---

## SSH Configuration

### Local Mac → macbridge

```
Host macbridge
    HostName macbridge-ssh.techstruction.co
    User tonyg
    IdentityFile ~/.ssh/id_ed25519
    ProxyCommand /opt/homebrew/bin/cloudflared access ssh --hostname %h
```

**Usage:** `ssh macbridge` from any network (routes through Cloudflare Tunnel).

---

## Environment Variables (`.env`)

| Variable | Purpose | Example |
|----------|---------|---------|
| `INTELLIGENCE_BACKEND` | AI backend selector (`kimi` or `ollama`) | `kimi` |
| `KIMI_API_KEY` | Nvidia NIM API key for Kimi k2.5 | `nvapi-...` |
| `KIMI_BASE_URL` | Nvidia NIM API endpoint | `https://integrate.api.nvidia.com/v1` |
| `KIMI_MODEL` | Kimi model identifier | `moonshotai/kimi-k2-5` |
| `OLLAMA_HOST` | Ollama server URL | `https://ollama-mbp.techstruction.co` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.1` |
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token | `8718754783:AA...` |
| `TELEGRAM_WEBHOOK_SECRET` | Webhook verification secret | (custom string) |
| `TELEGRAM_OWNER_CHAT_ID` | Owner's Telegram user ID | `7645251071` |
| `OPENBRAIN_PORT` | Webhook server listen port | `8765` |
| `OPENBRAIN_HOST` | Webhook server bind address | `0.0.0.0` |

---

## Agent Roster

| Agent | Role | Primary Tools | Responsibility |
|-------|------|--------------|----------------|
| **Scribe** | Researcher | Web scraping, NotebookLM | Gathering data, scoping problems, finding sources |
| **Engineer** | Builder | Code, Comfy UI flows | Designing and building automation scripts |
| **Foreman** | Logistics | Telegram, Zo Computer | Moving data between domains, routing messages |
| **Architect** | Orchestrator | Writer-Critic loop | Quality assurance, master plan maintenance |

---

## The 5 Domains

| Domain | Alias | Description | Examples |
|--------|-------|-------------|----------|
| **Capital** | Cash / Charts | Finance, investments, research | Stock analysis, budget tracking |
| **Computers** | Tech | Tools, servers, codebases, AI | Server configs, code reviews |
| **Cars** | — | Automotive research and projects | Parts research, build logs |
| **Cannapy** | — | Domain-specific research | Botanical data, cultivation notes |
| **Clan** | Personal | Family, relationships, development | Personal goals, family events |

---

## MVP Pipeline Flow

```
User Message (Telegram)
        │
        ▼
   ┌─────────┐
   │ Dropbox  │  @OG_Datadogs_bot receives message
   └────┬─────┘
        │
        ▼
   ┌─────────┐
   │ Sorter   │  classify_message.py — AI classifies into domain + category
   └────┬─────┘
        │
        ▼
   ┌─────────┐
   │ Bouncer  │  bouncer_check.py — Quality gate (pass / flag / reject)
   └────┬─────┘
        │
        ▼
   ┌──────────────┐
   │ Filing Cabinet│  Zo Computer — Stores in the appropriate domain repo
   └────┬──────────┘
        │
        ▼
   ┌─────────┐
   │ Receipt  │  Inbox Log entry created (audit trail)
   └────┬─────┘
        │
        ▼
   ┌──────────────┐
   │ Tap on       │  generate_digest.py — Daily/weekly summary
   │ the Shoulder │
   └────┬──────────┘
        │
        ▼
   User receives digest via Telegram
```

---

## Decommissioned Systems

| System | Decommission Date | Reason | Replacement |
|--------|------------------|--------|-------------|
| **Affine** (self-hosted) | 2026-03-21 | Integration complexity, unstable API | Zo Computer |
| **HiClaw** | 2026-03-18 | Framework too complex for current needs | NemoClaw |
| **Docker Compose OpenClaw** | 2026-03-23 | Invisible to OpenShell CRD routing | K3s Hybrid Sandbox |
| **OpenClaw Web Dashboard** | 2026-03-23 | Permanent pairing deadlock (v2026.3.11 bug) | Telegram channel |

---

## Version History

| Component | Current Version | Install Date |
|-----------|----------------|-------------|
| OpenClaw | v2026.3.11 (29dc654) | 2026-03-15 |
| K3s | Managed by OpenShell | — |
| Node.js | 22 (inside Sandbox) | — |
| Caddy | Latest (Docker Hub) | 2026-03-10 |
| Python | 3.x (venv) | 2026-03-09 |
| Ollama | Latest | — |
| Llama 3.1 | Latest | — |

---

## Quick Reference Commands

```bash
# SSH into macbridge
ssh macbridge

# Check NemoClaw pod status
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl get pods -n openshell"

# View NemoClaw gateway logs
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec nemoclaw -n openshell -- tail -50 /tmp/gw_onboarded.log"

# Run a NemoClaw backup
ssh macbridge "/home/tonyg/nemoclaw-sync.sh --backup"

# Full sync + backup
ssh macbridge "/home/tonyg/nemoclaw-sync.sh"

# Check NemoClaw model config
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -i nemoclaw -n openshell -- bash -c 'export PATH=/sandbox/.npm-global/bin:\$PATH && openclaw models status'"

# Restart NemoClaw gateway
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec nemoclaw -n openshell -- pkill -f openclaw"

# Check Docker containers
ssh macbridge "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"

# Check listening ports
ssh macbridge "ss -tlnp"
```

---

*This document is the definitive infrastructure reference for the GzOpenBrain system. For debugging guidance, see `SELF_HEALING.md`. For the project roadmap, see `MASTER_PLAN.md`. For the change log, see `UPDATE_LEDGER.md`. For backup procedures, see `docs/NEMOCLAW_DATA_SYNC_MANUAL.md`.*
