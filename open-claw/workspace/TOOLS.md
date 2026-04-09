# TOOLS.md — Adam's Setup Notes

Skills define _how_ tools work. This file has adam's specific paths and configuration.

---

## Project Management

### Python skill commands (primary)

```bash
# List all projects (cross-domain read)
source ~/.nemoclaw-secrets && \
  python3 ~/GzOpenBrain/NemoClaw/scripts/skills/project-manage/project_manage.py project-list

# Create project (own domains: CAPITAL, CANNAPY, CLAN)
source ~/.nemoclaw-secrets && \
  python3 ~/GzOpenBrain/NemoClaw/scripts/skills/project-manage/project_manage.py project-create \
  CAPITAL "Project Title" "Description" --vp vault --priority 2 --status elevated --agent adam

# CEO status report
source ~/.nemoclaw-secrets && \
  python3 ~/GzOpenBrain/NemoClaw/scripts/skills/project-manage/project_manage.py project-report
```

### Directus MCP via mcporter (natural language)

```bash
source ~/.nvm/nvm.sh
mcporter list                              # shows 20 directus tools
mcporter call directus-openbrain.readItems collection=projects
mcporter call directus-openbrain.readItem collection=projects id=PRJ-CAP-...
mcporter call directus-openbrain.createItem collection=projects --args '{"title":"..."}'
```

---

## OpenBrain Inbox & ToDo

```bash
# Check open tasks in adam's domains
source ~/.nemoclaw-secrets && \
  python3 ~/GzOpenBrain/NemoClaw/scripts/skills/openbrain-interact/openbrain_interact.py todo-check

# Review unprocessed inbox
source ~/.nemoclaw-secrets && \
  python3 ~/GzOpenBrain/NemoClaw/scripts/skills/openbrain-interact/openbrain_interact.py inbox-review

# Assign item to VP
source ~/.nemoclaw-secrets && \
  python3 ~/GzOpenBrain/NemoClaw/scripts/skills/openbrain-interact/openbrain_interact.py item-assign <item-id> vault
```

---

## Health Monitor

```bash
python3 ~/GzOpenBrain/NemoClaw/scripts/adam-health-monitor.py --once
cat /tmp/adam-health.log | tail -30
```

---

## Systems

| System | Role | Access |
|---|---|---|
| MacBridge (here) | adam's home — private, policy-enforced | local |
| Zo Computer | cloud ops, mmat, ACOM, Directus | SSH: `ssh -p 10220 root@ts3.zocomputer.io` |
| Directus API | openbrain.db REST interface | `http://100.106.189.97:8922` |

## Domains (adam owns)

- CAPITAL — Vault (Vinny) is VP
- CANNAPY — Flora is VP
- CLAN — Kira is VP

Read-only awareness of: COMPUTERS (Rigs), CARS (Slick)

## Directus API Token

`DIRECTUS_API_TOKEN` — in `~/.nemoclaw-secrets`
Domain access: R/W CAPITAL+CANNAPY+CLAN, R all others
