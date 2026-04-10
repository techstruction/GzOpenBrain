# NemoClaw — Complete Build & Operations Reference

> **This is the authoritative reference for NemoClaw.**
> Self-contained. No "see other files" — everything is here.
> Update this file whenever any component changes.
>
> Last updated: 2026-04-09
> RUNBOOK.md = operational procedures | BUILDSHEET.md = this file (complete spec)

---

## 1. What NemoClaw Is

NemoClaw is the second OpenClaw instance in the Claw Crew. Its persona is **Adam** —
the on-prem arm of the AI stack. Adam owns: private data, LAN access, infrastructure
monitoring, self-healing, backups, and compute tasks that Zo's 6-hour restart cycle
makes unreliable.

NemoClaw runs inside an NVIDIA OpenShell K3s sandbox on MacBridge. It is
fundamentally different from ZoClaw — it is NOT a plain Linux process; it is a
container runtime with a managed sandbox lifecycle, landlock filesystem policy,
and L7 network enforcement.

---

## 2. Current State Snapshot

| Field | Value |
|-------|-------|
| Persona | Adam |
| OpenClaw version | v2026.3.11 |
| Telegram bot | `@Adams_Tech_ClawdBot` |
| Inference model | `nvidia/meta/llama-3.1-8b-instruct` via Rate Queue Proxy on Zo |
| Host | MacBridge — headless Ubuntu, K3s via OpenShell |
| Sandbox UUID | `854b2d84-783c-4749-bed4-ba5362184e7a` |
| Active image | `docker.io/library/nemoclaw-custom:v3` (K3s containerd) — **v4 build pending** |
| Canonical Dockerfile | `~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom` on MacBridge |
| Sandbox policy version | v1 (adam-sandbox.yaml, applied at creation) |
| Gateway port (MacBridge) | `127.0.0.1:18789` |
| Gateway port (Tailscale) | `100.100.225.112:18790` |
| Public URL | `nemoclaw-macbridge.techstruction.co` |
| OpenSpace | ✅ Baked into image |
| CLI-Anything | ✅ Baked into image |
| web-fetch skill | ✅ Baked into image (v3) |
| research-topic skill | ✅ Baked into image (v3) |
| openbrain-interact | ✅ Baked into image (v3) |
| Directus MCP | ✅ Baked into mcporter.json (v3) — via directus-relay.service on MacBridge (172.80.1.1:8924 → Zo:8923) |
| Rules/IDENTITY | ✅ Baked into image (v3) — `/sandbox/.openclaw/workspace/IDENTITY.md` |

---

## 3. Full Stack Diagram

```
MacBook Pro (MBP)
└── ssh macbridge → MacBridge (Ubuntu, 192.168.1.26 / Tailscale 100.100.225.112)
    │
    ├── Docker container: openshell-cluster-nemoclaw
    │   └── K3s cluster (openshell namespace)
    │       ├── openshell-0 pod (OpenShell control plane)
    │       │   └── /var/openshell/openshell.db  ← sandbox registry (SQLite)
    │       │
    │       └── adam pod  ← THE SANDBOX
    │           Image: docker.io/library/nemoclaw-custom:v2
    │           PID 1: /opt/openshell/bin/openshell-sandbox  (from hostPath volume)
    │           Runtime: enforces landlock + L7 network policy
    │           │
    │           ├── /sandbox/  ← BAKED INTO IMAGE (persists pod restarts)
    │           │   ├── .venv/bin/openspace-mcp   ← OpenSpace binary
    │           │   ├── .openclaw/skills/          ← host skills + CLI-Anything
    │           │   └── .mcporter/mcporter.json   ← OpenSpace MCP config
    │           │
    │           └── /root/  ← EPHEMERAL (lost on pod restart, must restore)
    │               ├── .openclaw/openclaw.json    ← gateway + model config
    │               ├── .openclaw/agents/          ← NVIDIA auth profile
    │               └── .mcporter/mcporter.json   ← Directus MCP config
    │
    ├── systemd user services (persistent across MacBridge reboots)
    │   ├── openshell-forward.service
    │   │   openshell forward start 18789 adam
    │   │   → forwards adam pod port to localhost:18789
    │   │
    │   └── nemoclaw-gateway-proxy.service
    │       tailscale-gateway-proxy.py
    │       → proxies 100.100.225.112:18790 → 127.0.0.1:18789
    │
    ├── cron jobs (persistent)
    │   ├── */2 * * * * adam-health-monitor
    │   ├── 0 9 * * * adam-daily-brief
    │   └── 0 2 * * * rclone backup (BLOCKED: OAuth not configured)
    │
    └── ~/GzOpenBrain/  ← canonical source, NOT auto-mounted into pod
        ├── NemoClaw/Dockerfile.nemoclaw-custom
        ├── NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml
        └── open-claw/skills/  ← skill source of truth

Zo Computer (100.106.189.97 Tailscale)
├── Rate Queue Proxy :18792  ← ALL Adam inference routes here via SSH relay
├── Directus :8922 / :8923   ← ⚠️ NOT reachable from K3s pod directly
└── openbrain.db             ← canonical SQLite DB
```

---

## 4. The Custom Image (`nemoclaw-custom:v3`)

### What's in it

Everything under `/sandbox/` in the image is the persistence solution. The base
NVIDIA image has a clean `/sandbox/` — we bake our tools on top.

| Path | Content | Notes |
|------|---------|-------|
| `/sandbox/.venv/bin/openspace-mcp` | OpenSpace MCP binary | Installed as sandbox user |
| `/sandbox/.venv/lib/python3.13/site-packages/openspace/` | OpenSpace package | Owned by sandbox user |
| `/sandbox/.openclaw/skills/delegate-task/` | OpenSpace host skill | Copied from HKUDS/OpenSpace |
| `/sandbox/.openclaw/skills/skill-discovery/` | OpenSpace host skill | Copied from HKUDS/OpenSpace |
| `/sandbox/.openclaw/skills/cli-anything/SKILL.md` | CLI-Anything skill | Copied from HKUDS/CLI-Anything |
| `/sandbox/.openclaw/skills/web-fetch/SKILL.md` | Core skill — Jina Reader | Added v3 |
| `/sandbox/.openclaw/skills/research-topic/SKILL.md` | Workflow skill | Added v3 |
| `/sandbox/.openclaw/skills/openbrain-interact/openbrain_interact.py` | DB write script | Added v3 |
| `/sandbox/.openclaw/workspace/IDENTITY.md` | Adam persona/rules | Added v3 |
| `/sandbox/.mcporter/mcporter.json` | OpenSpace + Directus MCP registration | v3: Directus entry added |
| `/usr/lib/node_modules/mcporter/` | mcporter binary | **v4: baked via `npm install -g mcporter`** |
| `/usr/lib/node_modules/@directus/content-mcp/` | Directus MCP package | **v4: baked via `npm install -g @directus/content-mcp`** |

### Dockerfile (canonical — `~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom`)

See the actual file: `~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom` on MacBridge.

v3 changes vs v2:
- COPY web-fetch, research-topic SKILL.md files (from build context `skills/`)
- COPY openbrain_interact.py (from build context `skills/openbrain-interact/`)
- COPY IDENTITY.md → `/sandbox/.openclaw/workspace/` (from build context `workspace/`)
- mcporter.json now includes both OpenSpace + Directus entries
- `@directus/content-mcp` and `mcporter` — **baked into v4** via `RUN npm install -g openclaw@latest mcporter @directus/content-mcp` at top of Dockerfile
- v3 pods still require manual `npm install -g mcporter @directus/content-mcp` in §7 step 7

### How to rebuild the image (v3+)

```bash
ssh macbridge

# 1. Edit the Dockerfile if needed
nano ~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom

# 2. Set up build context (copy files Dockerfile will COPY)
cd ~/nemoclaw-image-build/
cp ~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom ./Dockerfile
mkdir -p skills/web-fetch skills/research-topic skills/openbrain-interact workspace
cp ~/GzOpenBrain/open-claw/skills/core/web-fetch/SKILL.md skills/web-fetch/
cp ~/GzOpenBrain/open-claw/skills/workflow/research-topic/SKILL.md skills/research-topic/
cp ~/GzOpenBrain/NemoClaw/scripts/skills/openbrain-interact/openbrain_interact.py skills/openbrain-interact/
cp ~/GzOpenBrain/systems/nemoclaw/rules.md workspace/IDENTITY.md

# 3. Build
docker build -t nemoclaw-custom:v4 .  # increment version each build

# Import into K3s (SLOW — 10-15 min for ~5.5GB image)
docker save nemoclaw-custom:v4 | \
  docker exec -i openshell-cluster-nemoclaw ctr images import -

# Verify import
docker exec openshell-cluster-nemoclaw ctr images ls | grep nemoclaw-custom

# Patch the sandbox to use the new image (DO NOT use --type=merge, see §10)
# Replace v4 with the actual version tag you built
openshell doctor exec -- kubectl patch sandbox adam -n openshell --type=json -p '[
  {"op":"replace","path":"/spec/podTemplate/spec/containers/0/image",
   "value":"docker.io/library/nemoclaw-custom:v4"},
  {"op":"replace","path":"/spec/podTemplate/spec/containers/0/imagePullPolicy",
   "value":"IfNotPresent"}
]'

# Delete pod to trigger recreation with new image
openshell doctor exec -- kubectl delete pod adam -n openshell

# Wait ~15s, verify
openshell doctor exec -- kubectl get pods -n openshell

# Restart port forward (UUID didn't change, pod just recreated — should auto-recover)
systemctl --user restart openshell-forward
```

> **Alternative (faster for testing):** `openshell sandbox create --from <dir>` builds
> and pushes automatically, BUT times out for large images (~5.5GB). Use only for
> small image changes. For our image, always use the manual `docker save | ctr import` method.

---

## 5. Sandbox Lifecycle

### Create sandbox from scratch

Use this when the sandbox doesn't exist or after a full delete.

```bash
ssh macbridge

# Policy file is at:
# ~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml

openshell sandbox create \
  --name adam \
  --from openclaw \
  --policy ~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml \
  -- true

# Wait for "Created sandbox: adam" and pod to reach Running
openshell doctor exec -- kubectl get pods -n openshell

# Patch image to custom version (if image already imported in K3s)
openshell doctor exec -- kubectl patch sandbox adam -n openshell --type=json -p '[
  {"op":"replace","path":"/spec/podTemplate/spec/containers/0/image",
   "value":"docker.io/library/nemoclaw-custom:v2"},
  {"op":"replace","path":"/spec/podTemplate/spec/containers/0/imagePullPolicy",
   "value":"IfNotPresent"}
]'
openshell doctor exec -- kubectl delete pod adam -n openshell

# Restart port forward for new UUID
systemctl --user restart openshell-forward
sleep 15 && nc -z 127.0.0.1 18789 && echo PORT_OPEN
```

### Full delete + recreate (nuclear option — fixes stale DB crashes)

```bash
ssh macbridge
openshell sandbox delete adam
# Wait for cleanup
openshell doctor exec -- kubectl get sandbox -n openshell  # expect: "No resources found"

# Recreate (see above)
openshell sandbox create --name adam --from openclaw \
  --policy ~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml \
  -- true
```

### Patch sandbox image only (no delete/recreate of sandbox, only pod)

```bash
ssh macbridge
openshell doctor exec -- kubectl patch sandbox adam -n openshell --type=json -p '[
  {"op":"replace","path":"/spec/podTemplate/spec/containers/0/image",
   "value":"docker.io/library/nemoclaw-custom:v2"},
  {"op":"replace","path":"/spec/podTemplate/spec/containers/0/imagePullPolicy",
   "value":"IfNotPresent"}
]'
openshell doctor exec -- kubectl delete pod adam -n openshell
# Pod recreates automatically — wait ~15s
```

---

## 6. The 10 Required openshell-sandbox Env Vars

These env vars are set by the Sandbox CRD controller. They MUST be present or
`openshell-sandbox` exits immediately (exit code 0, no logs). If they go missing
(e.g. after a bad `--type=merge` patch), the pod crashes silently.

| Env Var | Value (current) | Purpose |
|---------|----------------|---------|
| `OPENSHELL_SANDBOX_ID` | `854b2d84-783c-4749-bed4-ba5362184e7a` | Sandbox UUID — changes on delete+recreate |
| `OPENSHELL_SANDBOX` | `adam` | Sandbox name |
| `OPENSHELL_ENDPOINT` | `https://openshell.openshell.svc.cluster.local:8080` | Management API |
| `OPENSHELL_SANDBOX_COMMAND` | `sleep infinity` | Command the sandbox supervisor runs |
| `OPENSHELL_SSH_LISTEN_ADDR` | `0.0.0.0:2222` | SSH proxy listen address |
| `OPENSHELL_SSH_HANDSHAKE_SECRET` | (in K3s secret) | NSSH1 handshake key |
| `OPENSHELL_SSH_HANDSHAKE_SKEW_SECS` | `300` | Clock skew tolerance |
| `OPENSHELL_TLS_CA` | `/etc/openshell-tls/client/ca.crt` | From openshell-client-tls secret |
| `OPENSHELL_TLS_CERT` | `/etc/openshell-tls/client/tls.crt` | From openshell-client-tls secret |
| `OPENSHELL_TLS_KEY` | `/etc/openshell-tls/client/tls.key` | From openshell-client-tls secret |

**Volume mounts that must also be present:**

| Mount | Source | Target | Why |
|-------|--------|--------|-----|
| `openshell-client-tls` | K3s Secret | `/etc/openshell-tls/client` | TLS certs for openshell-0 connection |
| `openshell-supervisor-bin` | hostPath `/opt/openshell/bin` | `/opt/openshell/bin` | `openshell-sandbox` binary (PID 1) |

Verify current spec is intact:
```bash
ssh macbridge "openshell doctor exec -- kubectl get sandbox adam -n openshell -o json | \
  python3 -c \"import json,sys; c=json.load(sys.stdin)['spec']['podTemplate']['spec']['containers'][0]; print(len(c.get('env',[])), 'env vars,', len(c.get('volumeMounts',[])), 'mounts')\""
# Expected: 10 env vars, 2 mounts (plus 1 k8s service account mount)
```

---

## 7. After-Pod-Restart Checklist

When the adam pod is recreated (for any reason), the `/root/` tree is wiped. Run
these steps in order to restore NemoClaw to full operation.

```bash
# 1. Verify pod is running
ssh macbridge "openshell doctor exec -- kubectl get pods -n openshell"
# Expected: adam 1/1 Running 0 <age>

# 2. Restart port forward (always safe to do)
ssh macbridge "systemctl --user restart openshell-forward && sleep 12 && \
  nc -z 127.0.0.1 18789 && echo PORT_OPEN"

# 3. Fix openclaw base config
ssh macbridge "openshell doctor exec -- kubectl exec -n openshell adam -- \
  openclaw doctor --fix > /dev/null 2>&1 && echo doctor OK"

# 4. Set inference model (step 5 also sets the model — but run this first so doctor doesn't complain)
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  openclaw models set nvidia/meta/llama-3.1-8b-instruct 2>&1 | tail -1"

# 5. Write full openclaw.json (model + provider + gateway + Telegram channel)
# ← CRITICAL: models.providers must include Rate Queue base URL or inference fails with "Unknown model"
# ← CRITICAL: apiKey must be the LITERAL key string, NOT "NVIDIA_API_KEY" env var reference.
#             OpenClaw has Shell env: off — env var refs are not resolved. If you use the var name,
#             models.json will inherit it and effective key will show as "missing".
# ← SCHEMA NOTE (v2026.3.11+): Keys changed from earlier versions:
#   - `baseUrl` (lowercase u) not `baseURL`
#   - `models` is required array of {id, name} objects — NOT a string
#   - `gateway.mode` = "local" required (not `gateway.host`)
#   - No `models.default` at top level
#   Pipe approach works reliably (heredoc quoting in kubectl exec is unreliable):
#     NVIDIA_KEY=$(ssh macbridge "grep NVIDIA_API_KEY ~/.nemoclaw-secrets | cut -d= -f2")
#     BOT_TOKEN=$(ssh macbridge "grep TELEGRAM_BOT_TOKEN ~/.nemoclaw-secrets | cut -d= -f2")
#     CONFIG=$(cat << EOF
#     {"gateway":{"mode":"local","port":18789},"models":{"providers":{"nvidia":{"baseUrl":"http://100.106.189.97:18792/v1","apiKey":"${NVIDIA_KEY}","models":[{"id":"nvidia/meta/llama-3.1-8b-instruct","name":"nvidia/meta/llama-3.1-8b-instruct"}]}}},"channels":{"telegram":{"botToken":"${BOT_TOKEN}","dmPolicy":"allowlist","allowFrom":[7645251071]}}}
#     EOF)
#     echo "$CONFIG" | ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -i -n openshell adam -- bash -c 'cat > /root/.openclaw/openclaw.json'"
NVIDIA_KEY="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"
BOT_TOKEN="8529665233:AAF5G63jCELEdeZximg4khz_GKz4_Z8VPwE"
SCRIPT="import json
cfg_path = '/root/.openclaw/openclaw.json'
with open(cfg_path) as f:
    cfg = json.load(f)
cfg['models'] = {
    'mode': 'merge',
    'providers': {
        'nvidia': {
            'baseUrl': 'http://100.106.189.97:18792/v1',
            'api': 'openai-completions',
            'apiKey': '${NVIDIA_KEY}',
            'models': [{'id': 'meta/llama-3.1-8b-instruct', 'name': 'meta/llama-3.1-8b-instruct', 'reasoning': False, 'input': ['text'], 'cost': {'input': 0, 'output': 0, 'cacheRead': 0, 'cacheWrite': 0}, 'contextWindow': 131072, 'maxTokens': 8192}]
        }
    }
}
cfg.setdefault('agents', {}).setdefault('defaults', {}).setdefault('model', {})['primary'] = 'nvidia/meta/llama-3.1-8b-instruct'
cfg['channels'] = {
    'telegram': {
        'enabled': True,
        'dmPolicy': 'allowlist',
        'allowFrom': [7645251071],
        'botToken': '${BOT_TOKEN}',
        'groupPolicy': 'allowlist',
        'streaming': 'partial'
    }
}
with open(cfg_path, 'w') as f:
    json.dump(cfg, f, indent=2)
print('OK')"
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- python3 -c \"${SCRIPT}\""

# 6. Write NVIDIA auth profile  ← CRITICAL: must be done before gateway starts or model is "unknown"
# IMPORTANT: Use stdin pipe (heredoc quoting in kubectl exec is unreliable)
AUTH_JSON='{"nvidia:manual":{"type":"api_key","provider":"nvidia","keyRef":{"source":"literal","value":"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"},"profileId":"nvidia:manual"}}'
echo "$AUTH_JSON" | ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -i -- bash -c '
mkdir -p /root/.openclaw/agents/main/agent
cat > /root/.openclaw/agents/main/agent/auth-profiles.json
chmod 600 /root/.openclaw/agents/main/agent/auth-profiles.json
echo auth OK
'"
# Verify:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- python3 -c \"import json; d=json.load(open('/root/.openclaw/agents/main/agent/auth-profiles.json')); print('auth profiles:', list(d.keys()))\""

# 7. Install mcporter + @directus/content-mcp + copy mcporter.json
# NOTE: These are NOT baked in the v3 image. They are /root/ ephemeral. Must reinstall after pod restart.
# TODO for v4 Dockerfile: RUN npm install -g mcporter @directus/content-mcp
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  npm install -g mcporter @directus/content-mcp 2>&1 | grep 'added'"
# Copy baked mcporter.json to /root/.mcporter/ (gateway reads this location)
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'mkdir -p /root/.mcporter && cp /sandbox/.mcporter/mcporter.json /root/.mcporter/mcporter.json && echo mcporter.json copied'"
# Verify:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- mcporter list"
# Expected: openspace (4 tools) + directus-openbrain (20 tools)

# 8. Write secrets to sandbox
ssh macbridge "openshell doctor exec -- kubectl exec -n openshell adam -- bash -c '
cat > /sandbox/.nemoclaw-secrets << EOF
export TELEGRAM_BOT_TOKEN=8529665233:AAF5G63jCELEdeZximg4khz_GKz4_Z8VPwE
export NVIDIA_API_KEY=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
export TELEGRAM_CHAT_ID=7645251071
export DIRECTUS_URL=https://172.80.1.1:8924
export DIRECTUS_API_TOKEN=openbrain-adam-agent-2026-capital-cannapy-clan
EOF
chmod 600 /sandbox/.nemoclaw-secrets
echo secrets OK'"

# 9. Start gateway  ← MUST use nohup + disown so process survives kubectl exec session ending
# NOTE: `openclaw gateway start` tries to use systemd (not available in container) — don't use it.
# NOTE: `openclaw gateway run` is the old subcommand — use `openclaw gateway --port 18789` directly.
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'nohup openclaw gateway --port 18789 </dev/null >>/tmp/gw.log 2>&1 & disown; sleep 1; echo PID:\$(pgrep -f \"openclaw gateway\")'"
# Wait for gateway to start
sleep 8
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'pgrep -f \"openclaw gateway\" && echo RUNNING; tail -5 /tmp/gw.log'"
# Expected in log: "[gateway] listening on ws://127.0.0.1:18789" + "[telegram] starting provider (@Adams_Tech_ClawdBot)"
# Verify Telegram connected:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  openclaw channels status"
# Expected: "Telegram default: enabled, configured, running, mode:polling"
# NOTE: 409 Conflict errors are expected if another process was polling. They clear in ~30s.
# NOTE: Kill any stale telegram-bridge.js first: ssh macbridge 'kill $(pgrep -f telegram-bridge.js) 2>/dev/null'

# 10. Copy IDENTITY.md from persistent to active workspace (still needed — /root is ephemeral)
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'cp /sandbox/.openclaw/workspace/IDENTITY.md /root/.openclaw/workspace/IDENTITY.md && echo Identity copied'"
# NOTE: IDENTITY.md source at /sandbox/.openclaw/workspace/IDENTITY.md is baked in v3.
# The /root/... copy is still needed because openclaw reads from /root/.openclaw/workspace/ at runtime.

# 11. Recreate skills symlink (ephemeral /root/.openclaw/skills → persistent /sandbox/.openclaw/skills)
# Without this, Adam sees "none of the skills have a SKILL.md file" and openclaw skills list shows empty.
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'rm -rf /root/.openclaw/skills 2>/dev/null; ln -sfn /sandbox/.openclaw/skills /root/.openclaw/skills && ls /root/.openclaw/skills/ | head -3 && echo symlink OK'"
# Expected: cli-anything, delegate-task, skill-discovery  ...symlink OK

# 12. [BAKED IN v3] OpenSpace workspace dir — no action needed
# /sandbox/openspace-workspace is created and chowned in the Dockerfile.
# Skip this step on v3+ images.
```

---

## 8. How to Update Individual Components

### Update gateway config (model, origins, etc.)
```bash
# Edit the python3 block in step 5 of §7, then:
# Kill gateway → rerun step 5 → rerun step 9
ssh macbridge "openshell doctor exec -- kubectl exec -n openshell adam -- pkill -f openclaw"
sleep 3
# Re-run steps 5 and 9 from §7
```

### Update sandbox policy (network rules, filesystem access)
```bash
# Edit the policy file on MacBridge:
nano ~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml

# Apply via openshell:
ssh macbridge "~/.local/bin/openshell policy set \
  ~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml"

# Verify new version loaded:
ssh macbridge "~/.local/bin/openshell policy list"
```

### Update Adam's IDENTITY/Rules
```bash
# Edit canonical source:
# systems/nemoclaw/rules.md  (in this Claude project)

# Deploy to running pod:
cat systems/nemoclaw/rules.md | ssh macbridge "cat | \
  ~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -i -- \
  bash -c 'mkdir -p /sandbox/.openclaw/workspace && cat > /sandbox/.openclaw/workspace/IDENTITY.md'"

# TODO: Add rules.md to custom image so it persists pod restarts
```

### Add a new skill to the image
```bash
# 1. Create skill in MacBridge canonical location:
#    ~/GzOpenBrain/open-claw/skills/<skill-name>/SKILL.md

# 2. Add to Dockerfile (before the chown RUN step):
RUN git clone --depth=1 https://github.com/<org>/<repo>.git /tmp/newskill && \
    cp /tmp/newskill/SKILL.md /sandbox/.openclaw/skills/<skill-name>/ && \
    rm -rf /tmp/newskill
# Or COPY if it's a local file

# 3. Rebuild and deploy image (see §4 "How to rebuild")

# Quick option (current session only — lost on pod restart):
cat ~/GzOpenBrain/open-claw/skills/<skill-name>/SKILL.md | \
  ssh macbridge "cat | ~/.local/bin/openshell doctor exec -- \
  kubectl exec -n openshell adam -i -- \
  bash -c 'mkdir -p /sandbox/.openclaw/skills/<skill-name> && \
  cat > /sandbox/.openclaw/skills/<skill-name>/SKILL.md'"
```

### Add a new MCP server (Directus, etc.)
```bash
# Install mcporter if not present:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  npm install -g mcporter 2>&1 | grep added"

# Register the MCP:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  mcporter config add <name> \
    --command '<cmd>' \
    --env KEY=value"

# Copy to root .mcporter so gateway picks it up:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'mkdir -p /root/.mcporter && cp /sandbox/config/mcporter.json /root/.mcporter/mcporter.json'"

# Restart gateway to load new MCP
```

### Rotate NVIDIA API key
```bash
NEW_KEY="nvapi-..."

# 1. Update auth profile in pod:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'cat > /root/.openclaw/agents/main/agent/auth-profiles.json << EOF
{\"nvidia:manual\":{\"type\":\"api_key\",\"provider\":\"nvidia\",\"keyRef\":{\"source\":\"literal\",\"value\":\"$NEW_KEY\"},\"profileId\":\"nvidia:manual\"}}
EOF'"

# 2. Update secrets file:
# Update /sandbox/.nemoclaw-secrets (and ~/.nemoclaw-secrets on MacBridge)

# 3. Update §7 Step 6 in THIS FILE with the new key
```

---

## 9. Directus MCP — Connectivity Fix (✅ RESOLVED 2026-04-01)

**Problem:** K3s pods can reach MacBridge's Tailscale IP (`100.100.225.112`) but
not Zo's Tailscale IP (`100.106.189.97`). Docker bridge networking doesn't propagate
Tailscale routes to other mesh nodes.

**Network reachability from adam pod:**
```
100.100.225.112 (MacBridge Tailscale) → REACHABLE ✅
172.80.1.1      (Docker host bridge)   → REACHABLE ✅
100.106.189.97  (Zo Tailscale)         → NOT REACHABLE ❌
```

**Solution implemented:**

A Python TCP relay runs on MacBridge as a systemd user service. It listens on the
Docker bridge IP `172.80.1.1:8924` (reachable from the K3s pod) and forwards all
traffic to Zo's Directus HTTPS proxy at `100.106.189.97:8923`.

> Note: socat would have been the simplest relay, but MacBridge lacks passwordless
> sudo so `apt-get install socat` isn't possible. A Python script is equivalent.

**Deployed components:**

- **Relay script:** `~/directus-relay.py` on MacBridge
- **Systemd service:** `~/.config/systemd/user/directus-relay.service` (enabled, auto-starts)
- **Policy:** `adam-sandbox.yaml` v2 — `openbrain_directus` endpoint updated to `172.80.1.1:8924`
- **MCP:** `directus-openbrain` registered in `/root/.mcporter/mcporter.json` with `NODE_TLS_REJECT_UNAUTHORIZED=0`
- **Secrets:** `DIRECTUS_URL=https://172.80.1.1:8924` in `/sandbox/.nemoclaw-secrets` and `~/.nemoclaw-secrets`

**Verify relay is working:**
```bash
# From MacBridge host
curl -sk https://172.80.1.1:8924/server/health
# Expected: {"status":"ok"}

# From inside adam pod
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'NODE_TLS_REJECT_UNAUTHORIZED=0 node -e \"
    const https = require(\\\\\"https\\\\\");
    https.get({hostname:\\\\\"172.80.1.1\\\\\",port:8924,path:\\\\\"/server/health\\\\\",rejectUnauthorized:false},
      r=>{let d=\\\\\"\\\\\";r.on(\\\\\"data\\\\\",c=>d+=c);r.on(\\\\\"end\\\\\",()=>console.log(r.statusCode,d))});
  \"'"

# Check both MCPs are registered and healthy
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- mcporter list"
# Expected: directus-openbrain (20 tools) + openspace (4 tools), both healthy

# Restart relay if it stops
ssh macbridge "systemctl --user restart directus-relay && systemctl --user status directus-relay"
```

**After pod restart — add to §7 checklist (Step 7b):**
```bash
# Write mcporter config with both MCPs (including Directus)
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- bash -c '
mkdir -p /root/.mcporter
cat > /root/.mcporter/mcporter.json << MCPEOF
{
  \"mcpServers\": {
    \"openspace\": {
      \"command\": \"/sandbox/.venv/bin/openspace-mcp\",
      \"env\": {
        \"OPENSPACE_HOST_SKILL_DIRS\": \"/sandbox/.openclaw/skills\",
        \"OPENSPACE_WORKSPACE\": \"/sandbox/openspace-workspace\"
      }
    },
    \"directus-openbrain\": {
      \"command\": \"node\",
      \"args\": [\"/usr/lib/node_modules/@directus/content-mcp/dist/index.js\"],
      \"env\": {
        \"DIRECTUS_URL\": \"https://172.80.1.1:8924\",
        \"DIRECTUS_TOKEN\": \"openbrain-adam-agent-2026-capital-cannapy-clan\",
        \"NODE_TLS_REJECT_UNAUTHORIZED\": \"0\"
      }
    }
  },
  \"imports\": []
}
MCPEOF
echo mcporter OK'"
```

> **Future hardening:** Bake this mcporter.json into the custom image so it also
> survives pod restarts without manual intervention. Requires image rebuild (§4).

---

## 10. Critical DO-NOTs

| DO NOT | Why | Do This Instead |
|--------|-----|-----------------|
| `kubectl patch sandbox --type=merge` with containers | Wipes ALL env vars and volumeMounts from the container entry | `--type=json` with specific `op:replace` paths |
| `openshell sandbox upload adam /file /dest` | Creates a DIRECTORY named `file` at dest | Pipe via SSH: `cat file \| ssh openshell-adam 'cat > /dest/file'` |
| pip install as root in Dockerfile | Root-owned venv files can trigger landlock policy failures | `USER sandbox` before pip, `USER root` after |
| `pip install --find-links --no-index` in sandbox | pip 26.0.1 AssertionError bug | Install wheels one at a time by explicit path |
| Download MacBridge wheels for sandbox | MacBridge=cp312, sandbox=cp313 | `pip3 download --python-version 3.13 --abi cp313 --platform manylinux_2_17_x86_64` |
| Modify Sandbox CRD env vars without checking all 10 are present | Missing env = immediate crash (exit code 0, no logs) | `kubectl get sandbox adam -n openshell -o json` and count env vars first |
| Use `openshell gateway stop` to reset | Kills management API; `gateway start` won't work | `docker start openshell-cluster-nemoclaw` to recover |
| Use direct `integrate.api.nvidia.com` for inference | 40 RPM hard cap; bypasses Rate Queue | All inference via Rate Queue Proxy on Zo `:18792` |
| Start gateway before writing NVIDIA auth profile | "FailoverError: Unknown model" on first message | Always complete §7 step 6 (auth profile) BEFORE step 9 (gateway start) |
| Start gateway without sourcing `/sandbox/.nemoclaw-secrets` | "No API key found for provider 'nvidia'" — models.providers uses `"apiKey": "NVIDIA_API_KEY"` env var reference which is empty | Always use `source /sandbox/.nemoclaw-secrets &&` before `openclaw gateway run` (step 9) |
| Run `nemoclaw` npm package telegram-bridge.js | It's a legacy pre-OpenClaw integration (`/home/tonyg/.nvm/.../nemoclaw/scripts/telegram-bridge.js`). It polls Adam's bot token and invokes `nemoclaw-start` (which doesn't exist). This causes `nemoclaw-start: command not found` in Telegram. **DECOMMISSIONED 2026-04-01.** | Kill PID if running: `ssh macbridge 'kill $(pgrep -f telegram-bridge.js)'`. OpenClaw gateway handles Telegram natively via `channels.telegram` config. |
| Rely on old `nemoclaw-start` script | It was from the NemoClaw plugin (not installed in custom image). `"commands.native"` was set to `nemoclaw-start` by the plugin; after `openclaw doctor --fix` it resets to `"auto"`. If you see this error, also check if `telegram-bridge.js` is running on MacBridge (see above). | `openclaw doctor --fix` resets `native` to `auto` |
| Assume the sandbox UUID is stable | UUID changes on `openshell sandbox delete`+recreate | Always check UUID after nuclear operations; restart openshell-forward |

---

## 11. Troubleshooting

### Pod in CrashLoopBackOff (exit code 0, < 1 second)

**Symptom:** `adam 0/1 CrashLoopBackOff`. No logs. openshell-0 shows rapid
`Ready → Provisioning` cycles (pod registers, then exits).

**Cause:** Stale openshell-0 SQLite DB state OR missing/corrupted env vars.

**Diagnose:**
```bash
# Check env var count (should be 10):
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl get pod adam -n openshell \
  -o json | python3 -c \"import json,sys; print(len(json.load(sys.stdin)['spec']['containers'][0]['env']), 'env vars')\""

# Check openshell-0 logs for context:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl logs openshell-0 -n openshell 2>&1 | tail -20"
```

**Fix A — env vars corrupted:** Restore with json patch (see §6 for full list).

**Fix B — stale DB (env vars are correct but pod still crashes):**
```bash
ssh macbridge "~/.local/bin/openshell sandbox delete adam && sleep 5"
# Then recreate from §5
```

---

### Port 18789 not reachable

```bash
ssh macbridge "systemctl --user status openshell-forward"
# If active but port still closed — openshell-forward is using old UUID
ssh macbridge "systemctl --user restart openshell-forward && sleep 12 && \
  nc -z 127.0.0.1 18789 && echo OPEN || echo STILL_CLOSED"
```

If still closed after restart, check that the pod is actually running:
```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl get pods -n openshell"
```

---

### SSH handshake rejected (`ssh openshell-adam`)

Caused by K3s container stop/start rotating TLS certs.
```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl delete pod adam -n openshell"
# Wait 15s for pod to recreate, then try ssh again
```

---

### Gateway not starting (config invalid)

```bash
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  openclaw doctor --fix > /dev/null 2>&1"
# Then try gateway with --allow-unconfigured:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  bash -c 'nohup openclaw gateway run --allow-unconfigured > /tmp/gateway.log 2>&1 &'"
sleep 8
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl exec -n openshell adam -- \
  tail -8 /tmp/gateway.log"
```

---

### K3s management API dead (`openshell gateway stop` was run)

```bash
ssh macbridge "docker start openshell-cluster-nemoclaw"
# Wait 20s then check:
ssh macbridge "~/.local/bin/openshell doctor exec -- kubectl get pods -n openshell"
```

---

## 12. Ports & Network

| Port | Host | Service | Access |
|------|------|---------|--------|
| 18789 | MacBridge localhost | openshell port forward → adam pod gateway | From MacBridge or SSH tunnel |
| 18790 | MacBridge Tailscale | Tailscale proxy → 18789 | From any Tailscale node |
| 8080 | MacBridge localhost | OpenShell management API | Do NOT expose |
| 2222 | Inside K3s | SSH proxy | Via openshell forward |

**Pod networking:**
- Pod IP: `10.42.0.x` (changes on recreate)
- Pod can reach: MacBridge `100.100.225.112`, docker host `172.80.0.1`
- Pod CANNOT reach: Zo `100.106.189.97` (Tailscale routing doesn't propagate through Docker bridge)
- Internet: allowed per policy (HTTPS only, specific hosts)

---

## 13. Sandbox Policy Reference

Policy file: `~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml`

Current policy version: **v1** (applied at sandbox creation 2026-04-01)

Filesystem:
- Read-only: `/usr`, `/lib`, `/proc`, `/dev/urandom`, `/app`, `/etc`, `/var/log`
- Read-write: `/sandbox`, `/tmp`, `/dev/null`
- Landlock: `best_effort` (doesn't block if kernel unsupported)
- Process user: `sandbox:sandbox`

Network policies (key ones):
| Policy | Host | Port | Binaries |
|--------|------|------|----------|
| `nvidia` | integrate.api.nvidia.com | 443 | `/usr/bin/curl`, `/bin/bash`, `/usr/local/bin/opencode` |
| `claude_code` | api.anthropic.com + 4 others | 443 | `/usr/local/bin/claude`, `/usr/bin/node` |
| `github` | github.com, api.github.com | 443 | `/usr/bin/gh`, `/usr/bin/git` |
| `telegram` | api.telegram.org | 443 | (all) |
| `openbrain_directus` | 100.106.189.97 | 8923 | (none — fix needed, see §9) |
| `zo_ssh` | ts3.zocomputer.io | 10220 | `/sandbox/.venv/bin/python3`, `/usr/bin/ssh` |

Apply policy changes:
```bash
ssh macbridge "~/.local/bin/openshell policy set \
  ~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml"
ssh macbridge "~/.local/bin/openshell policy list"
```

---

## 14. Cron Jobs (MacBridge — Persistent)

```bash
ssh macbridge "crontab -l"
```

| Schedule | Script | Log | Status |
|----------|--------|-----|--------|
| `*/2 * * * *` | `~/adam-health-monitor.py` | `~/adam-health-monitor.log` | ✅ Running |
| `0 9 * * *` UTC | `~/adam-daily-brief.py` | `~/adam-daily-brief.log` | ✅ Running |
| `0 2 * * *` | `rclone copy ...` | — | ⚠️ BLOCKED: `rclone config` OAuth not done |

---

## 15. Secrets Reference

All secrets stored on MacBridge at `~/.nemoclaw-secrets`. Deploy to sandbox at
`/sandbox/.nemoclaw-secrets` after each pod restart (see §7 step 8).

| Secret | Value location | Purpose |
|--------|---------------|---------|
| `TELEGRAM_BOT_TOKEN` | `~/.nemoclaw-secrets` | `@Adams_Tech_ClawdBot` |
| `TELEGRAM_CHAT_ID` | `~/.nemoclaw-secrets` | Owner chat: `7645251071` |
| `NVIDIA_API_KEY` | `~/.nemoclaw-secrets` | Inference — via Rate Queue Proxy |
| `DIRECTUS_URL` | `~/.nemoclaw-secrets` | `https://100.106.189.97:8923` |
| `DIRECTUS_API_TOKEN` | `~/.nemoclaw-secrets` | `openbrain-adam-agent-2026-capital-cannapy-clan` |

Directus access: R/W on CAPITAL + CANNAPY + CLAN; read-all other domains.

---

## 16. Open Items (as of 2026-04-08)

| Item | Priority | Notes |
|------|----------|-------|
| **Zo supervisord cold-start fix** | **Critical** | Every Zo restart kills Rate Queue → Adam silent. Watchdog can't self-heal cold (DECISION-33). Fix: @reboot cron on Zo outside supervisord. Next session. |
| Bake Directus mcporter.json into image | Medium | Currently written manually after restart; add to Dockerfile (see §9) |
| Bake gateway startup into image | Medium | Currently manual after every restart; consider entrypoint script in Dockerfile |
| rclone OAuth config | Medium | Backup cron is silently failing |
| Bake `rules.md` into image | Low | IDENTITY.md in `/sandbox/.openclaw/workspace/` — currently ephemeral |

> `systems/nemoclaw/rules.md` ✅ Written and deployed (2026-04-01, Session 3)

**Diagnosing Adam silence (updated 2026-04-08):**
When Adam stops responding, check Zo services FIRST before touching the pod:
```bash
ssh zo-computer "curl -s http://127.0.0.1:18792/health"
# {"ok":true,...} = Rate Queue healthy, look elsewhere
# connection refused or timeout = Zo restarted, restore supervisord include:
ssh zo-computer "echo -e '\n[include]\nfiles = /root/.zo/supervisord-custom.conf' >> /etc/zo/supervisord-user.conf && supervisorctl -c /etc/zo/supervisord-user.conf reread && supervisorctl -c /etc/zo/supervisord-user.conf update"
```
