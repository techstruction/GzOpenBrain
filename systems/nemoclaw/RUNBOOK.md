# NemoClaw (Adam) — Infrastructure Runbook

> Reference for infrastructure work on NemoClaw. Covers design, config paths,
> skill installation, service management, and known quirks.
> Update this file whenever the config changes.
>
> Last updated: 2026-03-31

---

## Identity

| Field | Value |
|-------|-------|
| Claw name | NemoClaw |
| Persona | Adam — on-prem arm, private data, LAN access, monitoring, HA, backup |
| OpenClaw version | v2026.3.11 |
| Telegram bot | `@Adams_Tech_ClawdBot` |
| Model | `nvidia/meta/llama-3.1-8b-instruct` via Rate Queue Proxy on Zo |
| Host | MacBridge (headless Ubuntu) running K3s |
| MacBridge SSH | `ssh macbridge` (Tailscale) or via cloudflared ProxyCommand |

---

## Architecture — CRITICAL READ BEFORE ANY WORK

NemoClaw's architecture is **fundamentally different** from ZoClaw. It runs inside a
K3s pod managed by NVIDIA's OpenShell runtime. The pod filesystem is **completely
ephemeral** — everything in `/sandbox/` is lost on every pod restart.

```
MacBridge (Ubuntu, always-on)
├── K3s cluster (openshell namespace)
│   ├── openshell-0 pod (OpenShell control plane)
│   └── adam pod (THE sandbox — ghcr.io/nvidia/openshell-community/sandboxes/openclaw:latest)
│       ├── PID 1: openshell-sandbox (IS the runtime — not a separate openclaw process)
│       ├── sleep infinity (OPENSHELL_SANDBOX_COMMAND)
│       └── openclaw gateway run (started by nemoclaw-start or manually)
│           EPHEMERAL — all of /sandbox/ is lost on pod restart
│
├── systemd user services (persistent, on MacBridge)
│   ├── openshell-forward.service → openshell forward start 18789 adam
│   └── nemoclaw-gateway-proxy.service → tailscale-gateway-proxy.py (18789→18790)
│
└── ~/GzOpenBrain/open-claw/ (persistent — NOT mounted into pod)
    └── skills/              (source-of-truth for skill files; needs rebuild after restart)
```

### Why the pod is ephemeral (RESOLVED — custom image solution)

The K3s adam pod spec has no PVC. Originally everything in `/sandbox/` was lost on
pod restart. This is now **solved** with a custom Docker image.

**Current image:** `docker.io/library/nemoclaw-custom:v2` (baked into K3s containerd)
**Canonical Dockerfile:** `~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom` on MacBridge

What's baked in:
- OpenSpace (`/sandbox/.venv/bin/openspace-mcp`) — installed as `sandbox` user
- CLI-Anything SKILL.md (`/sandbox/.openclaw/skills/cli-anything/`)
- OpenSpace host skills (`delegate-task/`, `skill-discovery/`)
- mcporter.json for OpenSpace MCP (`/sandbox/.mcporter/mcporter.json`)

**Still ephemeral after pod restart (must restore manually):**
- `/root/.openclaw/openclaw.json` — gateway config (model, controlUi settings)
- `/root/.openclaw/agents/` — auth profiles (NVIDIA API key)
- `/root/.mcporter/mcporter.json` — Directus MCP registration
- `/sandbox/.nemoclaw-secrets` — tokens
- `/sandbox/config/mcporter.json` — mcporter project config
- `/tmp/gateway.log` — gateway process (must be restarted)

### Crash root cause discovered (2026-04-01)

The pod was in CrashLoopBackOff (exit code 0, < 1 second) with BOTH the original
NVIDIA image AND the custom image. Root cause: **stale state in openshell-0's SQLite DB**
after multiple Sandbox CRD patches during debugging. The `openshell-sandbox` binary would
connect to openshell-0 (marking it Ready), then exit immediately.

**Fix:** Delete the sandbox entirely (`openshell sandbox delete adam`) and recreate fresh.
This clears the stale DB entry and gives a new UUID with clean state.

**DO NOT** use `kubectl patch sandbox --type=merge` when modifying container fields.
It wipes the entire container spec array entry (env vars, volumeMounts). Always use
`--type=json` for surgical patches to individual fields.

**Current sandbox UUID:** `854b2d84-783c-4749-bed4-ba5362184e7a` (regenerated 2026-04-01)

---

## Accessing the Sandbox

### Method 1: SSH (preferred for interactive work)
```bash
# One-time setup: add SSH config on MBP
ssh macbridge "~/.local/bin/openshell sandbox ssh-config adam" >> ~/.ssh/config
# Then:
ssh openshell-adam
# Inside: you are root in the /sandbox environment
```

The SSH config uses `openshell ssh-proxy` as a ProxyCommand. This requires the
openshell-forward.service to be running (port 18789 forwarded from adam pod).

**NSSH1 handshake caveat:** OpenShell uses a custom SSH handshake
(`OPENSHELL_SSH_HANDSHAKE_SECRET`). After a K3s Docker container stop/start,
TLS certs rotate and the handshake fails. Workaround: delete and recreate the adam pod.

### Method 2: kubectl exec (always works, doesn't require SSH handshake)
```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- <command>"
# Example:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- ps aux"
```

This is the **reliable fallback** when SSH proxy fails. Use it to diagnose issues
and re-start the gateway.

---

## Config Files

### Persistent (on MacBridge — survive restarts)

**`~/GzOpenBrain/NemoClaw/Dockerfile`** — the base image definition
- Base: `node:22-slim`
- Installs: `openclaw@2026.3.11`, `pyyaml`, NemoClaw plugin, nemoclaw-start script
- No CMD (openshell-sandbox is the entrypoint)
- Python is installed (`python3`, `python3-pip`, `python3-venv`) but the sandbox
  uses a uv-managed venv at `/sandbox/.venv/` (Python 3.13)

**`~/GzOpenBrain/NemoClaw/scripts/nemoclaw-start.sh`** — startup entrypoint
- Runs `openclaw doctor --fix`, sets model, installs plugin, starts gateway
- `openclaw gateway run` launched as background process
- Logs to `/tmp/gateway.log` inside pod

**`~/GzOpenBrain/open-claw/skills/`** — canonical skill source (NOT auto-mounted)
```
delegate-task/
excalidraw-builder/
market-price-checker/
openbrain_core/
skill-creator/
skill-discovery/
```
After any pod restart, skills must be manually transferred to `/sandbox/.openclaw/skills/`.

### Ephemeral (inside /sandbox/ — lost on pod restart)

All of these must be recreated after every pod restart:

**`/sandbox/.openclaw/openclaw.json`** — generated by nemoclaw-start
```json
{
  "agents": {"defaults": {"model": {"primary": "nvidia/meta/llama-3.1-8b-instruct"}}},
  "gateway": {"mode": "local", "controlUi": {...}}
}
```

**`/sandbox/.mcporter/mcporter.json`** — MCP registration (ephemeral)
Must be written via kubectl exec or SSH after every restart.

Target state (when OpenSpace is properly installed):
```json
{
  "mcpServers": {
    "openspace": {
      "command": "/sandbox/.venv/bin/openspace-mcp",
      "env": {
        "OPENSPACE_HOST_SKILL_DIRS": "/sandbox/.openclaw/skills",
        "OPENSPACE_WORKSPACE": "/sandbox/openspace-workspace"
      }
    }
  },
  "imports": []
}
```

**`/sandbox/.openclaw/skills/`** — host skills (ephemeral)
Must be re-transferred from MacBridge after every restart.

---

## MacBridge Systemd Services (Persistent)

These run on MacBridge (not inside the pod) and survive MacBridge reboots:

### openshell-forward.service
Forwards port 18789 from the adam pod to localhost:18789 on MacBridge.
```ini
[Service]
ExecStartPre=/bin/sleep 8
ExecStart=/bin/bash -c "PATH=/home/tonyg/.local/bin:$PATH openshell forward start 18789 adam"
Restart=on-failure
RestartSec=15
```
Manage: `systemctl --user status|restart openshell-forward`

### nemoclaw-gateway-proxy.service
Proxies MacBridge Tailscale IP (100.100.225.112:18790) → localhost:18789.
This exposes NemoClaw to the Tailscale mesh (e.g. accessible from MBP).
```ini
[Service]
ExecStart=/usr/bin/python3 /home/tonyg/tailscale-gateway-proxy.py
Restart=always
RestartSec=5
```
Manage: `systemctl --user status|restart nemoclaw-gateway-proxy`

---

## Ports

| Port | Location | Service | Notes |
|------|----------|---------|-------|
| 18789 | MacBridge localhost | OpenShell port forward → adam pod gateway | Primary access point |
| 18790 | MacBridge Tailscale IP | Tailscale proxy → 18789 | MBP access via Tailscale |
| 8080 | MacBridge | OpenShell management API | Do not expose externally |
| 2222 | Inside K3s pod | SSH proxy (inside openshell namespace) | Via openshell forward |

**NemoClaw gateway URL** (from MacBridge): `http://127.0.0.1:18789`
**NemoClaw gateway URL** (from Tailscale): `http://100.100.225.112:18790`
**Public URL**: `nemoclaw-macbridge.techstruction.co` (Cloudflare tunnel → 18789)

---

## Gateway Management

### Check if gateway is running
```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- ps aux" | grep openclaw
```

### Start gateway (after pod restart)
```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'nohup openclaw gateway run --allow-unconfigured > /tmp/gateway.log 2>&1 &'"
```

### Check gateway log
```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  tail -f /tmp/gateway.log"
```

### Check port forward is active
```bash
ssh macbridge "nc -z 127.0.0.1 18789; echo $?"  # 0 = connected
```

### Restart the port forward service
```bash
ssh macbridge "systemctl --user restart openshell-forward"
```

---

## Pod Management

### Check pod status
```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl get pods -n openshell"
```

### Delete and recreate adam pod (forces fresh TLS handshake certs)
```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl delete pod adam -n openshell"
# Wait ~15 seconds for pod to recreate, then start gateway manually
```
**WARNING:** Deleting the pod loses ALL ephemeral state in /sandbox/.

### Stop/start K3s container (breaks SSH handshake — avoid unless necessary)
```bash
ssh macbridge "~/.local/bin/openshell gateway stop"
ssh macbridge "docker start openshell-cluster-nemoclaw"  # 'gateway start' may not work
```

---

## Installing Packages in the Sandbox

The sandbox uses **Python 3.13** and a **uv-managed venv** at `/sandbox/.venv/`.
MacBridge has Python 3.12. This means wheels downloaded on MacBridge may not work.

**Always download wheels for cp313 + manylinux_2_17_x86_64:**
```bash
# On MacBridge (outside sandbox):
pip3 download \
  --python-version 3.13 \
  --platform manylinux_2_17_x86_64 \
  --abi cp313 \
  --only-binary=:all: \
  <package> -d /tmp/wheels/

# Transfer via SSH (NOT openshell upload — it creates directories):
cat /tmp/wheels/package-cp313.whl | ssh openshell-adam 'cat > /tmp/package.whl'

# Install inside sandbox:
ssh openshell-adam "/sandbox/.venv/bin/pip install /tmp/package.whl --no-deps"
```

**pip 26.0.1 bug:** Do NOT use `--find-links` + `--no-index` together in the sandbox.
Install wheels one at a time by explicit path to avoid `AssertionError`.

**openshell upload bug:** `openshell sandbox upload adam /local/file /remote/file`
creates a DIRECTORY named `file` with the file inside it. Always use the pipe-via-SSH
method above.

---

## Installing Skills (Ephemeral — Must Redo After Restart)

```bash
# Copy skill from MacBridge persistent location to sandbox:
cat ~/GzOpenBrain/open-claw/skills/delegate-task/SKILL.md | \
  ssh openshell-adam 'mkdir -p /sandbox/.openclaw/skills/delegate-task && \
  cat > /sandbox/.openclaw/skills/delegate-task/SKILL.md'

# Or for whole directories, tar it:
tar czf - ~/GzOpenBrain/open-claw/skills/delegate-task/ | \
  ssh openshell-adam 'mkdir -p /sandbox/.openclaw/skills && tar xzf - -C /sandbox/.openclaw/skills/'
```

---

## Accessing and Updating Rules/MD Files

NemoClaw's Rules live in `/sandbox/.openclaw/workspace/` (ephemeral) but the
canonical source is in this Claude project at `systems/nemoclaw/rules.md`.

**To read current deployed Rules:**
```bash
ssh openshell-adam "cat /sandbox/.openclaw/workspace/IDENTITY.md"
```

**To update Rules:**
```bash
# Edit: systems/nemoclaw/rules.md in this Claude project
# Deploy:
cat systems/nemoclaw/rules.md | ssh openshell-adam \
  'cat > /sandbox/.openclaw/workspace/IDENTITY.md'
# Gateway picks up on next interaction (may need restart)
```

**Important:** Because /sandbox/ is ephemeral, Rules must be re-deployed every time
the pod restarts. Until persistence is solved, this is a manual step.

---

## Adam's Cron Jobs (On MacBridge — Persistent)

| Schedule | Job | Log |
|----------|-----|-----|
| `*/2 * * * *` | Health monitor — self-heals NemoClaw, Telegram alerts | `~/adam-health-monitor.log` |
| `0 9 * * *` UTC | Daily brief — projects + todos + inbox via Telegram | `~/adam-daily-brief.log` |
| `0 2 * * *` | rclone backup → OneDrive (14-day retention) | ⚠️ BLOCKED: rclone OAuth not configured |

Check crons: `ssh macbridge "crontab -l"`

---

## Directus Access

Adam accesses Directus via HTTPS proxy (not direct HTTP to Zo:8922 — sandbox
egress blocks non-HTTPS ports):

- **URL:** `https://100.106.189.97:8923` (HTTPS proxy on Zo)
- **Token:** stored in `/home/tonyg/.nemoclaw-secrets` on MacBridge
- **Domains:** R/W access to CAPITAL + CANNAPY + CLAN; read-all
- **MCP:** `@directus/content-mcp` v0.1.0 (20 tools) — registered in sandbox mcporter

---

## OpenSpace — Current State

**Status:** ✅ SOLVED (2026-04-01). OpenSpace is baked into the custom Docker image.

**Custom image:** `docker.io/library/nemoclaw-custom:v2` in K3s containerd
**Dockerfile:** `~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom` on MacBridge

What the image provides (all under `/sandbox/`):
- `/sandbox/.venv/bin/openspace-mcp` — OpenSpace MCP binary ✅
- `/sandbox/.openclaw/skills/delegate-task/` — host skill ✅
- `/sandbox/.openclaw/skills/skill-discovery/` — host skill ✅
- `/sandbox/.openclaw/skills/cli-anything/` — CLI-Anything SKILL.md ✅
- `/sandbox/.mcporter/mcporter.json` — OpenSpace MCP registration ✅

**Key Dockerfile fix:** OpenSpace is installed as `USER sandbox` (not root), so all
venv files are owned by the sandbox user. This prevents potential landlock policy
failures on startup.

**mcporter.json content (baked in):**
```json
{
  "mcpServers": {
    "openspace": {
      "command": "/sandbox/.venv/bin/openspace-mcp",
      "env": {
        "OPENSPACE_HOST_SKILL_DIRS": "/sandbox/.openclaw/skills",
        "OPENSPACE_WORKSPACE": "/sandbox/openspace-workspace"
      }
    }
  },
  "imports": []
}
```

Note: the `mcporter.json` in the image is at `/sandbox/.mcporter/mcporter.json`.
After restart, you also need to copy it to `/root/.mcporter/mcporter.json` so the
openclaw gateway picks it up:
```bash
mkdir -p /root/.mcporter
cp /sandbox/.mcporter/mcporter.json /root/.mcporter/mcporter.json
```

## Directus MCP — Connectivity Issue (Unresolved)

**Status:** ⚠️ Not working — pod cannot reach Zo's Tailscale IP directly.

The sandbox (K3s pod) can reach MacBridge's Tailscale IP `100.100.225.112` but
cannot reach Zo's Tailscale IP `100.106.189.97`. The Directus HTTPS proxy at
`100.106.189.97:8923` is therefore unreachable from within the pod.

**Root cause:** K3s pods route through the Docker bridge network. Tailscale
routes for non-local IPs (Zo at 100.106.189.97) don't propagate through Docker
networking to K3s pods.

**Required fix (not yet implemented):** Set up a socat/SSH port relay on MacBridge
that exposes Zo's port 8923 on a local port accessible from the K3s pod:
```bash
# On MacBridge — run as systemd service
socat TCP-LISTEN:8924,bind=172.80.1.1,fork TCP:100.106.189.97:8923
```
Then update adam-sandbox.yaml policy to allow `172.80.1.1:8924` and update
`DIRECTUS_URL=https://172.80.1.1:8924` in the MCP config.

**Current workaround:** Directus MCP is registered but offline. The adam agent
can still access Directus via the SSH relay to Zo using the skill scripts directly.

---

## Known Quirks (Critical)

1. **Custom image bakes /sandbox/ — but /root/ is still ephemeral** — The custom
   image (`nemoclaw-custom:v2`) bakes OpenSpace and skills into `/sandbox/`. But
   `/root/.openclaw/` (openclaw.json, auth profiles) and gateway process are still
   lost on pod restart. After each restart: run `openclaw doctor --fix`, set model,
   write gateway config, copy `/sandbox/.mcporter/mcporter.json` to `/root/.mcporter/`,
   start gateway with `--allow-unconfigured`.

2. **Sandbox delete+recreate changes UUID** — Running `openshell sandbox delete adam`
   followed by `openshell sandbox create` gives a new UUID. The `openshell-forward`
   systemd service must be restarted to pick up the new UUID:
   `systemctl --user restart openshell-forward`

3. **`--type=merge` sandbox patch wipes container spec** — NEVER use
   `kubectl patch sandbox --type=merge` with a `containers` array. It replaces the
   entire entry, wiping all env vars and volumeMounts. Always use `--type=json` for
   surgical field replacement.

4. **CrashLoopBackOff from stale openshell-0 DB** — If the pod crashes immediately
   (exit code 0, < 1 second) even with the correct image and spec, the root cause is
   stale state in openshell-0's SQLite DB. Fix: `openshell sandbox delete adam` then
   `openshell sandbox create --name adam --from openclaw --policy <policy.yaml>`.

5. **NSSH1 handshake failure after K3s restart** — Stopping and starting the
   openshell K3s Docker container (`openshell gateway stop/start`) causes TLS cert
   rotation in the pod. Subsequent `ssh openshell-adam` fails with "handshake rejected".
   Fix: `kubectl delete pod adam -n openshell` to force pod recreation with fresh certs.

3. **`openshell gateway stop` kills management API** — After `openshell gateway stop`,
   `openshell gateway start` may say "already exists" but the container is dead.
   Workaround: `docker start openshell-cluster-nemoclaw`.

4. **openshell upload creates directories** — `openshell sandbox upload adam /file /dest`
   creates a DIRECTORY named `/dest` with the file inside. Always use pipe-via-SSH.

5. **pip 26.0.1 + Python 3.13** — Don't use `--find-links --no-index`. Install wheels
   individually by explicit path.

6. **cp312 vs cp313 wheels** — MacBridge is Python 3.12; sandbox is Python 3.13.
   Always download wheels with `--python-version 3.13 --abi cp313` for sandbox use.

7. **~/GzOpenBrain/open-claw/ is NOT mounted in the pod** — Skills and config in
   MacBridge's persistent GzOpenBrain directory are NOT automatically available in
   the sandbox. They must be explicitly transferred after each restart.

8. **Rate Queue Proxy is on Zo, not MacBridge** — Adam routes NVIDIA inference via
   the Rate Queue on Zo (`http://127.0.0.1:18792/v1`), reached through the SSH relay.
   Not via MacBridge's local Ollama (that's available but not primary).
