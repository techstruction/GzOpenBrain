# NemoClaw Data Sync Manual

> **Script:** `/home/tonyg/nemoclaw-sync.sh` on macbridge  
> **Purpose:** Back up and synchronize all irreplaceable NemoClaw data between the K3s Sandbox container and the Host OS.  
> **Last updated:** 2026-03-23

---

## What This Script Does

NemoClaw runs inside a **K3s Sandbox** on the macbridge server. Kubernetes containers are inherently ephemeral — if the pod is deleted, restarted, or garbage-collected, any data stored only inside the container is permanently lost. To solve this, our deployment uses `hostPath` volume mounts that bind the container's data directory (`/sandbox/.openclaw/`) to a persistent directory on the Host OS (`/home/tonyg/GzOpenBrain/open-claw/`).

**However, this live mount alone is not sufficient.** Some files are created exclusively inside the container (e.g., `auth-profiles.json` from `openclaw onboard`), and the hostPath mount can sometimes experience inode decoupling if files are atomically rewritten from the Host side. This script provides a robust safety net:

1. **Pulls** any container-only files down to the Host directory (ensuring nothing is trapped inside the container).
2. **Pushes** locally edited files back into the container (useful when modifying skills or config offline).
3. **Creates compressed, timestamped backup snapshots** of all irreplaceable data.
4. **Auto-prunes** old backups to prevent disk bloat (keeps the last 10).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  macbridge Host OS                                          │
│                                                             │
│  /home/tonyg/GzOpenBrain/open-claw/   ◄── Host Volume      │
│    ├── openclaw.json                  (Core config)         │
│    ├── agents/main/                                         │
│    │   ├── agent/                     (Auth + model config) │
│    │   │   ├── auth-profiles.json                           │
│    │   │   └── models.json                                  │
│    │   ├── memory/                    (Learned context)     │
│    │   │   └── SELF_HEALING.md                              │
│    │   ├── sessions/                  (Conversation logs)   │
│    │   │   ├── *.jsonl                                      │
│    │   │   └── sessions.json                                │
│    │   └── AGENTS.md                  (Agent identity)      │
│    ├── skills/                        (Custom tools)        │
│    │   ├── market-price-checker/                            │
│    │   └── excalidraw-builder/                              │
│    └── workspace/                     (Personality + AI)    │
│        ├── IDENTITY.md                                      │
│        ├── USER.md                                          │
│        ├── SOUL.md                                          │
│        ├── TOOLS.md                                         │
│        ├── HEARTBEAT.md                                     │
│        ├── BOOTSTRAP.md                                     │
│        ├── skills/                    (Workspace skills)    │
│        └── .openclaw/                 (Workspace state)     │
│                                                             │
│  /home/tonyg/GzOpenBrain/.nemoclaw-backups/                 │
│    ├── nemoclaw-backup-20260323_205839.tar.gz               │
│    └── ...                            (last 10 kept)        │
│                                                             │
├─────────────────── hostPath mount ──────────────────────────┤
│                                                             │
│  K3s Sandbox Container (pod: nemoclaw, ns: openshell)       │
│  /sandbox/.openclaw/                  ◄── Container View    │
│    └── (same structure, live-mirrored via Kubernetes)        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## What Data Is Protected

The script tracks two categories of irreplaceable data:

### Directories (synced recursively)

| Path | Contents | Why It Matters |
|------|----------|----------------|
| `agents/main/memory/` | Learned context files (e.g., `SELF_HEALING.md`) | This is the agent's long-term memory. If lost, the agent forgets all past debugging lessons and operational patterns. |
| `agents/main/sessions/` | `.jsonl` conversation transcripts + `sessions.json` index | Full history of every conversation the agent has had. Used for context continuity across sessions. |
| `agents/main/agent/` | `auth-profiles.json`, `models.json` | API keys for Ollama and other providers. If lost, the agent cannot connect to any AI model until reconfigured. |
| `skills/` | Custom skill bundles (`market-price-checker`, `excalidraw-builder`) | Tools the agent can execute. Each contains `SKILL.md` instructions and supporting scripts/templates. |
| `workspace/skills/` | Workspace-level skill bundles (`skill-creator`, etc.) | Additional skills scoped to the workspace context rather than the global agent. |
| `workspace/.openclaw/` | `workspace-state.json` | Internal workspace tracking state. |

### Individual Files (synced one-by-one)

| File | Purpose |
|------|---------|
| `openclaw.json` | **Master configuration.** Contains gateway settings, Telegram bot token, allowed origins, auth mode, plugin entries, and provider definitions. This is the single most critical file. |
| `openclaw.json.bak` | Automatic backup of the previous config state (created by the OpenClaw CLI on every config write). |
| `update-check.json` | Tracks the last version check timestamp to avoid redundant update polling. |
| `agents/main/AGENTS.md` | Agent-level identity and behavioral instructions. Defines how the `main` agent operates. |
| `workspace/IDENTITY.md` | The agent's self-description and persona definition. |
| `workspace/USER.md` | Information about the user (you) that the agent references for personalization. |
| `workspace/SOUL.md` | Core personality traits, values, and behavioral guidelines. |
| `workspace/TOOLS.md` | Registry of available tools and their descriptions. |
| `workspace/HEARTBEAT.md` | Periodic health/status check file maintained by the agent. |
| `workspace/BOOTSTRAP.md` | Initial startup instructions the agent reads on first boot. |

---

## Usage

### Prerequisites

- SSH access to macbridge (`ssh macbridge`)
- The NemoClaw K3s Sandbox must be running (pod `nemoclaw` in namespace `openshell`)
- `openshell` CLI installed at `~/.local/bin/openshell`

### Commands

Run on **macbridge** (SSH into the server first):

```bash
# Full sync: pull data from container to host, then create a backup
./nemoclaw-sync.sh

# Backup only — compress current host data into a timestamped archive
# (does NOT pull from the container first)
./nemoclaw-sync.sh --backup

# Pull only — copy data from the K3s container to the host
# (does NOT create a backup)
./nemoclaw-sync.sh --pull

# Push only — copy local host data INTO the K3s container
# (use after editing skills or config files on the host)
./nemoclaw-sync.sh --push

# Status — show inventory of all tracked files and existing backups
# (read-only, changes nothing)
./nemoclaw-sync.sh --status
```

### Running Remotely (from your local Mac)

You can run any command remotely via SSH without logging in first:

```bash
ssh macbridge "/home/tonyg/nemoclaw-sync.sh --status"
ssh macbridge "/home/tonyg/nemoclaw-sync.sh --backup"
ssh macbridge "/home/tonyg/nemoclaw-sync.sh"
```

---

## Command Details

### Default Mode (no flags)

**What it does:** Performs a complete safety cycle.

1. **Preflight check** — verifies the `nemoclaw` pod is running in the `openshell` namespace.
2. **Pull** — streams every tracked directory and file from the container to the host using `kubectl exec` + `tar`. This ensures any files created inside the container (like `auth-profiles.json` from `openclaw onboard`) are safely mirrored to the host.
3. **Backup** — compresses all tracked data into a timestamped `.tar.gz` archive stored in `/home/tonyg/GzOpenBrain/.nemoclaw-backups/`.
4. **Status report** — prints a full inventory of all tracked paths and existing backups.
5. **Auto-prune** — if more than 10 backups exist, deletes the oldest ones.

**When to use:** Before making any risky changes. Before updating OpenClaw. As a regular maintenance habit.

### `--pull`

**What it does:** Copies data from the running K3s container to the host directory.

- Directories are streamed via `tar` (preserves permissions, handles nested structures).
- Individual files are read via `kubectl exec -- cat` and written directly to the host.
- Also scans for any `*.md` files at the root of `/sandbox/.openclaw/` that aren't in the tracked list.

**When to use:** After the agent creates new files inside the container (new skills, updated memory, new sessions). After running `openclaw onboard` or `openclaw configure` which write to `auth-profiles.json`.

### `--push`

**What it does:** Copies data from the host directory into the running K3s container.

- Directories are streamed via `tar` into the container.
- Individual files are piped via `cat | kubectl exec -i -- cat >`.
- After completion, warns you to restart the gateway daemon if config files were modified.

**When to use:** After editing skills or `.md` files locally on the host. After restoring from a backup. After modifying `openclaw.json` directly on the host (followed by a daemon restart).

> **⚠️ Important:** After pushing config changes, restart the daemon:
> ```bash
> openshell doctor exec -- kubectl exec nemoclaw -n openshell -- pkill -f openclaw
> ```

### `--backup`

**What it does:** Creates a compressed `.tar.gz` snapshot of all tracked host data.

- Archive name format: `nemoclaw-backup-YYYYMMDD_HHMMSS.tar.gz`
- Stored in: `/home/tonyg/GzOpenBrain/.nemoclaw-backups/`
- Only archives paths that actually exist (gracefully skips missing files).
- Auto-prunes to keep only the last 10 backups.

**When to use:** Before risky operations. On a regular schedule (consider adding to cron).

### `--status`

**What it does:** Read-only inventory check. Shows:

- Which tracked directories exist and how many files they contain.
- Which tracked files exist and their sizes.
- A list of the 5 most recent backups with their sizes.

**When to use:** Anytime you want to verify the health of the sync system without changing anything.

---

## Restoring from a Backup

If NemoClaw's data is corrupted or lost, restore from the most recent backup:

```bash
# 1. List available backups
ls -lth /home/tonyg/GzOpenBrain/.nemoclaw-backups/

# 2. Extract the desired backup over the host directory
cd /home/tonyg/GzOpenBrain/open-claw
tar xzf /home/tonyg/GzOpenBrain/.nemoclaw-backups/nemoclaw-backup-YYYYMMDD_HHMMSS.tar.gz

# 3. Push restored data into the container
/home/tonyg/nemoclaw-sync.sh --push

# 4. Restart the gateway daemon
~/.local/bin/openshell doctor exec -- kubectl exec nemoclaw -n openshell -- pkill -f openclaw

# 5. Restart the gateway
~/.local/bin/openshell doctor exec -- kubectl exec -i nemoclaw -n openshell -- bash -c '
export PATH=/sandbox/.npm-global/bin:$PATH
nohup openclaw gateway run --allow-unconfigured --verbose > /tmp/gw_restored.log 2>&1 &
'
```

---

## Automating with Cron

To run automatic daily backups, add to macbridge's crontab:

```bash
# Edit crontab
crontab -e

# Add this line for daily backups at 3:00 AM
0 3 * * * /home/tonyg/nemoclaw-sync.sh >> /home/tonyg/GzOpenBrain/.nemoclaw-backups/sync.log 2>&1
```

---

## Troubleshooting

### "Pod 'nemoclaw' not found"
The K3s Sandbox has been suspended or deleted by OpenShell. Check with:
```bash
~/.local/bin/openshell sandbox list
```
If the sandbox is missing, recreate it. The host data is safe because it lives on the host volume, not inside the container.

### "tar: permission denied" during pull
Some files inside the container may be owned by `root`. The script uses `2>/dev/null` to suppress these warnings, but the file may not be pulled. In this case, use `kubectl exec` with `sudo` or adjust file permissions inside the container.

### Backup size keeps growing
The auto-prune keeps only the last 10 backups. If you need to manually clean up:
```bash
ls -lth /home/tonyg/GzOpenBrain/.nemoclaw-backups/
rm /home/tonyg/GzOpenBrain/.nemoclaw-backups/nemoclaw-backup-OLDEST.tar.gz
```

### Push doesn't take effect
Config changes in `openclaw.json` require a **daemon restart** to take effect. The script warns you about this after a push, but if you miss it:
```bash
~/.local/bin/openshell doctor exec -- kubectl exec nemoclaw -n openshell -- pkill -f openclaw
```

---

## File Locations Reference

| Item | Path |
|------|------|
| Sync script | `/home/tonyg/nemoclaw-sync.sh` |
| Host data directory | `/home/tonyg/GzOpenBrain/open-claw/` |
| Container data directory | `/sandbox/.openclaw/` (inside pod `nemoclaw`) |
| Backup directory | `/home/tonyg/GzOpenBrain/.nemoclaw-backups/` |
| Gateway logs | `/tmp/gw_*.log` (inside the container) |
| Pod namespace | `openshell` |
| Pod name | `nemoclaw` |
| kubectl proxy | `~/.local/bin/openshell doctor exec -- kubectl` |

---

*This manual is part of the OpenBrain project documentation. See also: `SELF_HEALING.md` for debugging case studies, `MASTER_PLAN.md` for the project roadmap, and `UPDATE_LEDGER.md` for the change log.*
