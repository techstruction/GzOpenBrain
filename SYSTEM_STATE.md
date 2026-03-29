# SYSTEM_STATE.md

> Machine-readable snapshot of the full GzOpenBrain / Techstruction agent stack.
> Read this at the start of any Claude project that needs awareness of the live system.
> Updated at the end of every working session. Last updated: 2026-03-28

---

## Overall Status

| Stage | Name | Status |
|-------|------|--------|
| 0 | Foundation | ✅ Complete |
| 1 | Capture Layer (GOBI Telegram bot) | ✅ Complete |
| 2 | Storage Layer | ✅ Complete — SQLite on Zo |
| 3 | Quality Gate (Bouncer) | ✅ Complete |
| 4 | Intelligence Layer | ✅ Complete — Llama 3.3 70B via Nvidia API |
| 5 | Digest Layer | ✅ Complete |
| 6 | Fix Button (Human-in-the-loop) | ✅ Complete |
| 7 | Self-Maintenance & Architect loop | ✅ Complete |
| 8 | Hardening & Multi-domain Expansion | 🔲 Not started |
| 9 | Orchestration Upgrade (NemoClaw) | ✅ Complete |

---

## Agent Identity Map

| Agent Name | Persona | System | Telegram Bot | Bot ID | AI Model | Status |
|-----------|---------|--------|-------------|--------|----------|--------|
| Zo native | SAM (Security Agent Manager) | Zo Computer (always-on cloud) | TBD — existing Zo bot | TBD | Zo native | ⚠️ Rules migration needed |
| ZoClaw | Mmat | OpenClaw v2026.3.24 on Zo | `@OG_Mmat_bot` | 8382972952 | llama-3.1-8b-instruct (Nvidia) | ✅ Live |
| NemoClaw | Adam | OpenClaw v2026.3.11 on MacBridge K3s | `@OG_Datadogs_bot` | TBD | Ollama llama3.1 | ✅ Live — Adam rules pending |

### 5C VP Sub-Agents (Mmat's team — ZoClaw)
Team name: **"My Mans and Them"**

| Domain | VP Name | YAML | Status |
|--------|---------|------|--------|
| CAPITAL | TBD | `agents/openclaw-zo/capital-vp.yaml` | ❌ Not defined |
| COMPUTERS | TBD | `agents/openclaw-zo/computers-vp.yaml` | ❌ Not defined |
| CARS | TBD | `agents/openclaw-zo/cars-vp.yaml` | ❌ Not defined |
| CANNAPY | TBD | `agents/openclaw-zo/cannapy-vp.yaml` | ❌ Not defined |
| CLAN | TBD | `agents/openclaw-zo/clan-vp.yaml` | ❌ Not defined |

---

## Infrastructure Endpoints

| Service | Public URL | Internal | Machine | Port | Status |
|---------|-----------|----------|---------|------|--------|
| GOBI webhook | `https://gobi.techstruction.co` | localhost:8769 | Zo | 8769 | ✅ Live |
| Directus UI | `https://data.techstruction.co` | localhost:8922 | Zo | 8922 | ✅ Live — program `directus` in `/root/.zo/supervisord-custom.conf` |
| Ollama | `https://ollama-mbp.techstruction.co` | localhost:11434 | MacBridge | 11434 | ✅ Live |
| memU (MCP) | `https://memu-macbridge.techstruction.co` | localhost:8001 | MacBridge | 8001 | ✅ Live |
| NemoClaw gateway | internal only | localhost:18789 | MacBridge K3s | 18789 | ✅ Live — never expose publicly |
| MacBridge Caddy proxy | internal | localhost:8818 | MacBridge | 8818 | ✅ Live |
| Agent Org Chart webapp | via MacBridge relay | localhost:7842 | Zo | 7842 | ✅ Live |
| Nvidia API | `https://integrate.api.nvidia.com/v1` | — | Cloud | — | ✅ Live |

---

## Machine Reference

| Machine | Hostname (Tailscale) | Tailscale IP | Role | Service Manager |
|---------|---------------------|-------------|------|----------------|
| MacBook Pro M3 | `tonygs-macbook-pro` | 100.127.64.38 | Primary workstation / Claude Code orchestrator | — |
| Zo Computer | `zo-workspace` | 100.106.189.97 | Cloud compute, long-running agents, GOBI pipeline | supervisord — `/etc/zo/supervisord-user.conf` |
| MacBridge | `macbridge` | 100.100.225.112 | On-prem server, memU, NemoClaw, Ollama | Docker Compose + systemd |
| iPhone 15 Pro | `iphone-15-pro` | 100.114.125.101 | Remote trigger | — |

### SSH Access
```bash
ssh zo-computer          # Tailscale (preferred)
ssh root@100.106.189.97  # Tailscale IP fallback

ssh macbridge            # Tailscale (preferred)
ssh -o ProxyCommand='cloudflared access ssh --hostname macbridge-ssh.techstruction.co' \
    tonyg@macbridge-ssh.techstruction.co  # Off-Tailscale fallback
```

---

## Key File Paths

### Zo Computer
```
/home/workspace/GzOpenBrain/execution/     ← Python pipeline scripts
/home/workspace/GzOpenBrain/.env           ← Zo environment variables
/home/workspace/OPENBRAIN/openbrain.db     ← CANONICAL SQLite database
/home/workspace/directus/                  ← Directus install
/home/workspace/directus/.env             ← Directus config (DB path, admin creds)
/etc/zo/supervisord-user.conf              ← ONLY service manager on Zo (no PM2, no systemd)
/dev/shm/gobi-webhook.log                  ← GOBI webhook logs
/dev/shm/directus.log                      ← Directus logs
~/.openclaw/workspace/                     ← ZoClaw (Mmat) config
```

### MacBridge
```
/home/tonyg/GzOpenBrain/                  ← MacBridge working directory
/home/tonyg/GzOpenBrain/open-claw/        ← NemoClaw persistent config (K3s hostPath bind)
/home/tonyg/GzOpenBrain/open-claw/MEMORY.md  ← memU memory store
/home/tonyg/GzOpenBrain/docker-compose.yml   ← MacBridge Docker services
```

### OPENBRAIN Filing Cabinet (Zo)
```
/home/workspace/OPENBRAIN/
├── openbrain.db         ← SQLite — all domain data
├── CAPITAL/             ← Legacy flat files (pre-migration, kept for reference)
├── COMPUTERS/
├── CARS/
├── CANNAPY/
└── CLAN/
```

---

## Environment Variables Reference

> Values are in `.env` on each machine. Never hardcoded here.

| Variable | Purpose | Used By |
|----------|---------|---------|
| `NVIDIA_API_KEY` | Nvidia API auth (Llama 3.3 70B) | Sorter, Bouncer, Digest |
| `NVIDIA_BASE_URL` | `https://integrate.api.nvidia.com/v1` | All Nvidia API calls |
| `NVIDIA_MODEL` | `meta/llama-3.3-70b-instruct` | All Nvidia API calls |
| `GOBI_BOT_TOKEN` | `@GzOpenBrainInbox_bot` Telegram token | GOBI webhook |
| `OPENBRAIN_DB_PATH` | Path to `openbrain.db` | `db.py` |
| `OPENBRAIN_PORT` | Webhook server port (8769) | `telegram_webhook.py` |
| `OLLAMA_HOST` | `https://ollama-mbp.techstruction.co` | Ollama fallback |
| `OLLAMA_MODEL` | `llama3.1` | Ollama fallback |

---

## ZoClaw (Mmat) Config Reference

```bash
# On Zo Computer
~/.openclaw/workspace/IDENTITY.md     ← Mmat persona
~/.openclaw/workspace/SOUL.md         ← Mmat values/behavior
~/.openclaw/workspace/AGENTS.md       ← Agent definitions
~/.openclaw/workspace/USER.md         ← User profile

# Supervisord programs on Zo
supervisorctl -c /etc/zo/supervisord-user.conf status

# Current programs:
#   cloudflared      ← Cloudflare tunnel
#   frpc-frp-standard-3  ← FRP relay
#   gobi-webhook     ← GOBI Telegram pipeline (port 8769)
#   directus         ← Data UI (port 8922)
```

---

## NemoClaw (Adam) Config Reference

```bash
# On MacBridge — K3s pod in openshell namespace
kubectl get pods -n openshell                 # check pod status
kubectl logs -n openshell [pod-name]          # check logs

# Persistent config (hostPath bind to /sandbox/.openclaw/)
/home/tonyg/GzOpenBrain/open-claw/

# Gateway port (NEVER expose publicly)
localhost:18789

# Ingress (via Cloudflare + Traefik)
https://nemoclaw-macbridge.techstruction.co
```

---

## Database Schema Summary

```sql
-- items: all filed knowledge (ideas, tasks, notes, people, projects)
id, domain, category, item_type, title, content,
status, priority, source, agent, tags (JSON), metadata (JSON),
created_at, updated_at

-- inbox_log: raw GOBI captures + Sorter/Bouncer audit trail
id, raw_content, source, sender_id,
classified_domain, classified_category, classified_item_type,
classified_title, classified_summary, classified_tags, classified_metadata,
quality_score, bouncer_decision, bouncer_reason,
processed, item_id (→items), created_at, processed_at

-- digests: scheduled digest history
id, domain, digest_type, content, items_included (JSON), sent_at, created_at
```

**Valid domains:** `CAPITAL`, `COMPUTERS`, `CARS`, `CANNAPY`, `CLAN`
**Valid categories:** `People`, `Projects`, `Ideas`, `Admin`, `Tasks`, `Thoughts`, `Inbox Log`

---

## Active GOBI Pipeline Flow

```
User → Telegram @GzOpenBrainInbox_bot
  → gobi.techstruction.co/webhook (Zo, port 8769)
  → inbox_log (raw capture)
  → Sorter: Llama 3.3 70B classifies domain + category + title + tags
  → inbox_log updated with classification
  → Bouncer: quality gate
  → PASS: items table + Telegram receipt to user
  → FLAG: inbox_log flagged + review alert to user
  → data.techstruction.co (Directus) reflects new item immediately
```

---

## Open Items for Agent Org Chart Project

- [ ] Name the 5 VP sub-agents (one per 5C domain)
- [ ] Author ZoClaw Rules (`systems/openclaw-zo/rules.md`) — Mmat persona + VP team
- [ ] Author NemoClaw Rules (`systems/nemoclaw/rules.md`) — Adam persona
- [ ] Author Zo native Rules (`systems/zo/rules.md`) — SAM persona
- [ ] Create agent YAML files in `agents/openclaw-zo/` for Mmat + 5 VPs
- [ ] Create `agents/nemoclaw/adam.yaml`
- [ ] Decide: which agent/bot handles the `/fix` command?
- [ ] Decide: does the Sorter route classified content to the VP's inbox or just to the shared DB?
- [ ] Write `workflows/thoughts-and-ideas/SPEC.md`
