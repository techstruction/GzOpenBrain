# Self-Healing Protocol & Troubleshooting Ledger

This document serves as the high-fidelity memory of the OpenBrain project. It captures architectural failures, "ghost-in-the-machine" bugs, and the surgical fixes required to resolve them. **Read this before attempting to modify the NemoClaw deployment, the Zo Computer pipeline, or the Classification engine.**

---

## ⚡️ Key Case Studies

### 1. The Affine Filing Visibility Crisis (March 2026)
**Symptom:** The `write_to_affine.py` script returns a 200 OK and a valid Comment ID, but the note is completely invisible in the Affine UI sidebar.

**The "War Room" Discovery:**
- **Initial Assumption:** Just sending text in the `content` field would work. **Result:** Failure.
- **Trial 2 (The Map):** Sending a "Flat Map" of Block IDs. **Result:** Failure (API accepts it, UI ignores it).
- **The Breakthrough:** Using browser-captured network requests, we discovered that Affine's frontend requires a **Nested Tree** snapshot structure. Even a single missing property (like `flavour` or `index`) renders the entire comment invisible.

**The Fix:**
- Implemented `generate_gold_standard_snapshot()` in `write_to_affine.py`. This function clones the exact, bit-for-bit JSON structure captured from a manual browser interaction.
- **Key Lesson:** In Affine/BlockSuite, **Structure is Visibility**. If the JSON schema isn't 100% compliant with the frontend's expectation, the data is "orphaned" in the database.

---

### 2. The "Poisoned Sidebar" (Frontend Corruption)
**Symptom:** Even after fixing the snapshot format, the Comments panel remained empty ("No comments yet") and the browser console reported:
`TypeError: Cannot read properties of undefined (reading 'type') at DocCommentStore.listComments`

**Root Cause:**
- One or more malformed comments (from earlier troubleshooting steps) contained data that the Affine frontend didn't know how to map.
- Because Affine fetches *all* comments for the sidebar, **a single malformed entry crashes the entire rendering loop.** This makes even perfectly formatted new comments invisible.

**The Fix:**
- Created a surgical cleanup script (`cleanup.py`) to delete the specific malformed IDs via GraphQL mutation (`deleteComment`).
- **Healing Rule:** If the UI crashes, assume data corruption in the document history. Purge the "poisoned" entries to restore the render loop.

---

### 3. Classification Accuracy & Domain Drift
**Symptom:** Technical messages mentioning "Affine", "OneBrain", or "Agentic System" were defaulting to the **Clan** domain instead of **Computers**.

**Root Cause:**
- The `CLASSIFICATION_PROMPT` had loosely defined boundaries.
- **Clan** was acting as a "catch-all" when the model was uncertain.
- Lack of specific "Anchors" for the project's own terminology.

**The Fix:**
- **Deep Definitions:** Explicitly anchored "Affine", "OpenClaw", and "Coding" to **Computers**.
- **Negative Constraints:** Explicitly told the model that **Clan** is strictly for *personal* life and MUST NOT contain work/tech.
- **Internal Reasoning:** Added a `_reasoning` field to the classification output. This allows the bot to explain its logic to the logs, making it easier to audit "why" a mis-classification happened.

---

### 4. Background: Nvidia API 404 Errors
**Symptom:** Internal classification failed with a 404 "Function Not Found" after a server-side script update.

**Root Cause:**
- Certain models (like `nemotron-70b`) may be deprecated or restricted for specific API keys in certain regions/accounts, even if they appear in standard lists.

**The Fix:**
- Verified model availability via direct `curl` from the server.
- Switched to `meta/llama-3.1-70b-instruct`, which proved most stable for the `macbridge` environment.

---

### 5. K3s Sandbox Ephemeral Storage Trap (March 2026)
**Symptom:** NemoClaw installation inside an OpenShell K3s Sandbox kept losing all data (skills, config, agent memory) whenever the pod was suspended or restarted.

**Root Cause:**
- OpenShell's K3s Sandboxes are **ephemeral by design**. The entire container filesystem (including `/sandbox/.openclaw/`) is destroyed when Kubernetes garbage-collects the pod.
- The `nemoclaw` pod had no `hostPath` volume mounts, so every restart was a fresh slate.
- Repeated `openshell sandbox create` invocations generated 89+ circular reinstalls.

**The Fix:**
- Abandoned in-sandbox-only persistence entirely.
- Created a **Hybrid Sandbox** strategy: a K3s Sandbox triggers OpenShell's Traefik ingress automatically, while `hostPath` volume mounts bind `/sandbox/.openclaw/` → `/home/tonyg/GzOpenBrain/open-claw/` on the host.
- **Healing Rule:** Never store critical state inside a K3s Sandbox without explicit volume mounts. The Sandbox is disposable; the Host volume is permanent.

---

### 6. Docker Compose vs OpenShell CRD Routing Conflict (March 2026)
**Symptom:** After deploying NemoClaw as a standalone Docker Compose service (bypassing K3s entirely), the gateway started cleanly on `localhost:18789`, but Cloudflare returned `502 Bad Gateway` when accessing the domain.

**Root Cause:**
- OpenShell's Cloudflare Tunnel routing is **not a dumb port-forward**. It is managed by a Kubernetes Custom Resource Definition (CRD) that only maps subdomains for pods within its K3s cluster.
- A Docker Compose container binding to `127.0.0.1:18789` was invisible to the CRD router, so Cloudflare's tunnel endpoint had nothing to proxy to.

**The Fix:**
- Abandoned standalone Docker Compose deployment.
- Re-deployed inside a K3s Sandbox (to trigger the CRD) but with `hostPath` volume mounts pointed at the same Docker Compose config directory. This gave us **Kubernetes-managed routing** with **host-level persistence**.
- **Healing Rule:** On OpenShell systems, you MUST use K3s Sandboxes/Pods for any service that needs to be routed through the managed Cloudflare Tunnel. Docker Compose services are invisible to the CRD.

---

### 7. The hostPath Inode Decoupling Bug (March 2026)
**Symptom:** Python scripts running on the Host OS successfully wrote new JSON values to `openclaw.json`, but the running gateway daemon inside the K3s container continued using the old configuration values.

**Root Cause:**
- When Python's `json.dump()` writes to a file, it performs an **atomic rewrite** (truncate + write). In K3s `hostPath` mounts, this can **decouple the file's inode** from the container's filesystem view.
- The container's mount table points to the original inode. The Host OS creates a new inode. The container keeps reading the ghost of the old file.
- Additionally, the OpenClaw CLI (`openclaw config set`) performs its own schema validation and **silently rejects** any key it doesn't recognize, producing no error output.

**The Fix:**
- Always modify `openclaw.json` from **inside the container** using the official `openclaw config set` CLI instead of external Python scripts.
- If Host-side mutations are absolutely required, restart the entire K3s pod (`kubectl replace --force`) to re-bind the volume mounts.
- **Healing Rule:** Never atomically rewrite a `hostPath`-mounted file from the Host OS while a container is running. Use the container's own CLI tools, or force a pod restart after external edits.

---

### 8. The Dashboard Device Pairing Deadlock (March 2026)
**Symptom:** The OpenClaw dashboard loaded successfully via Cloudflare, accepted the gateway token, but permanently displayed "pairing required" without ever generating a `requestId` for CLI approval. Tried: multiple browsers, Incognito mode, iPhone, password auth mode — all produced the same deadlock.

**Root Cause:**
- The `v2026.3.11` dashboard has a **client-side state machine bug** under token-only authentication. The WebSocket connects, receives a `pairing-required` close code (4008), but the frontend JavaScript fails to call `device.pair.create` to generate the approval request.
- The server log shows `close code=4008 reason=connect failed cause=pairing-required` but never receives the corresponding `device.pair.create` frame.
- Switching to `password` auth mode didn't help because the same state machine code path is shared.

**The Fix:**
- **Bypassed the dashboard entirely** by connecting NemoClaw via **Telegram** instead. The Telegram channel plugin (`@openclaw/telegram`) uses a completely different authentication flow (CLI-based `openclaw pairing approve telegram <code>`) that works flawlessly.
- **Healing Rule:** If the OpenClaw dashboard is stuck in a pairing loop, don't waste time debugging the frontend. Use Telegram or WhatsApp as a direct channel — they have their own pairing flows that bypass the web UI completely.

---

### 9. Ollama Provider Registration Maze (March 2026)
**Symptom:** After setting `ollama/llama3.1` as the default model, the Telegram bot replied with `No API key found for provider "anthropic"` or `Unknown model: ollama/llama3.1. Set OLLAMA_API_KEY`.

**Root Cause (Three Layers):**
1. **Wrong config path:** `openclaw config set providers.ollama.baseUrl ...` was rejected because the correct schema path is `models.providers.ollama.baseUrl`.
2. **Environment variables don't persist:** Setting `OLLAMA_API_KEY=ollama-local` in a `kubectl exec` bash session only lives for that session. The `nohup` background daemon launched in the same session inherits it, but once that session exits and the daemon is later killed/restarted, the variable is lost.
3. **Model ID syntax collision:** Using `ollama:llama3.1` (colon) instead of `ollama/llama3.1` (slash) caused OpenClaw to prefix it under the `anthropic` namespace, creating `anthropic/ollama:llama3.1` and triggering the Anthropic API key check.

**The Fix:**
- Used the official documented onboarding command:
  ```
  openclaw onboard --non-interactive \
    --auth-choice ollama \
    --custom-base-url https://ollama-mbp.techstruction.co \
    --custom-model-id llama3.1 \
    --accept-risk
  ```
- This single command properly: (a) wrote the API key to `auth-profiles.json` (persistent on disk), (b) registered the custom base URL, (c) set the default model with the correct provider prefix.
- **Healing Rule:** Always use `openclaw onboard --non-interactive` for provider setup. Never manually hack `openclaw.json` for provider credentials — use the CLI's auth flow which writes to `auth-profiles.json` and persists across daemon restarts.

---

## 🛠 Self-Healing Checklist (The "Golden Rules")

### Legacy (Affine Era)
1. **Verify the Target Doc ID:** Always check `.env` against the live browser URL. A doc ID mismatch is the #1 cause of "missing" data.
2. **Standardize Newlines:** BlockSuite's delta format hates literal `\\n` chars. Always use standard Python `\n` in JSON payloads.
3. **The STDIN Protocol:** When passing complex JSON records to scripts, use `sys.stdin.read()` + the `--stdin` flag. Shell passing of large JSON strings often breaks due to escaping/quote nesting.

### Current (NemoClaw / Zo Computer Era)
4. **Never store state in ephemeral K3s pods.** Always use `hostPath` volume mounts for any data that must survive pod restarts.
5. **OpenShell CRD controls Cloudflare routing.** Docker Compose services are invisible to the tunnel. Use K3s Sandboxes for anything that needs a public subdomain.
6. **Never atomically rewrite hostPath-mounted files from the Host OS.** Use the container's own CLI tools, or force a pod restart after external edits.
7. **Use `openclaw onboard --non-interactive` for provider setup.** Don't manually hack `openclaw.json` — the CLI writes persistent credentials to `auth-profiles.json`.
8. **If the dashboard is stuck in a pairing loop, bypass it.** Use Telegram or WhatsApp channels instead of debugging the web frontend.
9. **Environment variables don't persist in K3s exec sessions.** If a daemon needs env vars, bake them into the config file or use the official onboarding flow.
10. **Model IDs use `/` not `:` for provider prefixes.** `ollama/llama3.1` is correct; `ollama:llama3.1` creates a phantom Anthropic dependency.

---
*Capture every failure. Update the ledger. The system grows through scar tissue.*
