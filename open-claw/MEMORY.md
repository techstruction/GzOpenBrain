
### [Computers] New Memory Path Setup
Adding a second sync entry to the new memory path for improved data management.
Tags: memory_path, sync_entry, data_management


### [Cannapy] Hydroponic Lighting Research
Research best hydroponic lighting options for Cannapy projects
Tags: hydroponic_lighting, cannapy_projects, research


### [Cars] E46 cooling system repair estimate
Received estimate for E46 cooling system repair parts.
Tags: e46, cooling_system, repair_estimate


### [Computers] AI-driven portfolio tracker for small cap stocks
Exploring AI-driven portfolio tracking for small cap stocks
Tags: ai, portfolio_tracker, small_cap_stocks


### [Cars] E46 cooling system repair estimate
Received estimate for E46 cooling system repair, 200 in parts.
Tags: e46, cooling_system, repair_estimate


### [Cars] E46 cooling system repair estimate
Received estimate for E46 cooling system repair, 200 in parts.
Tags: e46, cooling_system, repair_estimate


### [Computers] Real-time trading view monitoring system
Researching a system to monitor trading view in real-time.
Tags: trading_view, real_time_monitoring, chart_monitoring


### [Computers] Real-time trading view monitoring system
Researching a system to monitor trading view in real-time.
Tags: trading_view, real_time_monitoring, chart_monitoring


### [Computers] Real-time trading view monitoring system
Researching a system to monitor trading view in real-time.
Tags: trading_view, real_time_monitoring, chart_monitoring


### [Clan] Add Note to Brain
Add a note to the personal brain system.
Tags: note, brain_system, admin_task


### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Computers] MCP Integration Test
This is a test entry to verify dual-path storage to Affine and memU.
Tags: test, mcp, dual_path

### [Clan] Parse Error
AI output was not valid JSON.
Tags: 

### [Computers] ComfyUI Integration for OneBrain Agentic System
Proposal to investigate integrating ComfyUI as a component within the OneBrain agentic system project.
Tags: #Comp, #Ideas, #AI, #OneBrain, #AgenticSystems, #ComfyUI

### [Computers] ComfyUI Integration for OneBrain Agentic System
Proposing ComfyUI as a architectural component within the OneBrain agentic system project requiring further technical exploration.
Tags: #Comp, #Ideas, #AI, #Sys, #Architecture

### [~ CARS ~] Automotive Dashboard Concept
Concept for a dashboard interface, monitoring system, or data visualization tool designed specifically for vehicle applications or car metrics.
Tags: #Cars, #Ideas, #Dashboard, #UI, #UX

### [infrastructure] memU MCP server connected to Claude Code on MBP
Session 1 complete. memU MCP server rebuilt using FastMCP streamable-http transport (MCP 1.26.0), running in Docker on macbridge (openbrain_memu container, port 8001). Cloudflare tunnel routes memu-macbridge.techstruction.co -> localhost:8001. Fixed typo in Cloudflare hostname route (macbride -> macbridge). Registered globally in Claude Code via: claude mcp add --transport http --scope user memU https://memu-macbridge.techstruction.co/mcp. Tools: store_entry, query_context, read_all. Memory file: /root/.openclaw/MEMORY.md on macbridge. Source: ~/GzOpenBrain/mcp-memu/server.py.
Tags: memu, mcp, infrastructure, macbridge, claude-code, memory, session-1

### [COMPUTERS] memU verification complete — 2026-03-23
memU is running as Docker container 'openbrain_memu' on macbridge port 8001. It is an MCP server (memu-mcp v1.26.0) — correct endpoint is POST /mcp (not REST). Tools: store_entry, query_context, read_all. Cloudflare tunnel route 6 correctly proxies memu-macbridge.techstruction.co to localhost:8001. Zo can reach memU end-to-end via MEMU_SERVER_URL. Database is currently empty — needs ingestion. mcp_bridge.py on Zo rewritten to use real MCP protocol with notebook fallback. sanity_check.py updated to check memU connectivity. HQ Dashboard (port 8921) was OFFLINE during this session.
Tags: memu, macbridge, docker, mcp, verification, openbrain, zo-computer, infrastructure

### [COMPUTERS] memU monitoring + GzOpenBrain recon — 2026-03-23
Built full memU monitoring stack: memu_stats.py (entry count, size, last entry, trend snapshots), self_heal.py extended with memU check + restart instructions, admin-tools SKILL.md updated with memu_status/self_heal/sanity_check commands, generate_digest.py updated with live memU section + --send Telegram flag. GzOpenBrain repo lives at /home/tonyg/GzOpenBrain on macbridge. Stack: openbrain_agent (Telegram webhook, port 8769, running), openbrain_memu (memU MCP, port 8001, running), openbrain_openclaw (NemoClaw AI agent gateway, port 18789, STOPPED). Daily digest is NOT yet scheduled — cron/jobs.json is empty, openclaw gateway is down. Venv for macbridge scripts: /home/tonyg/GzOpenBrain/venv/bin/python3. Stats trend ledger: /home/tonyg/GzOpenBrain/open-claw/memu_stats_ledger.jsonl
Tags: memu, monitoring, daily-digest, telegram, self-heal, openbrain, macbridge, openclaw, schedule

### [COMPUTERS] SAM agent formalized as permanent sub-agent — 2026-03-24
SAM (Systems Agent for Maintenance) is a Zo Automations scheduled task (Telegram, every Sunday 9AM). Now formalized as a permanent skill at /home/workspace/Skills/sam-computers/SKILL.md. Execution script: sam_report.py at /home/workspace/OPENBRAIN/shared/sam_report.py. Report includes: Zo system vitals, sovereign infrastructure ports, memU stats+trend, 5C integrity, skill inventory, COMPUTERS task count. Trend ledger: /home/workspace/OPENBRAIN/COMPUTERS/memu_stats_ledger.jsonl for weekly/quarterly analysis. Automation prompt template included in SKILL.md for updating the Zo Automations entry.
Tags: SAM, monitoring, weekly-report, memu, skill, automation, COMPUTERS, zo-computer

### [COMPUTERS] Priority 5 complete — supervisord notebook-bridge + memu-watchdog — 2026-03-24
Two programs added to /etc/zo/supervisord-user.conf on Zo. notebook-bridge: keeps notebook_server.py (NotebookLM bridge, port 8421) alive via autorestart. memu-watchdog: polls memU MCP endpoint every 120s, logs status changes, writes state to /dev/shm/memu_watchdog_state.json. Both RUNNING confirmed. Also fixed mislabeled log strings in notebook_server.py (was 'MemU Bridge', now 'NotebookLM Bridge').
Tags: supervisord, notebook-bridge, memu-watchdog, zo-computer, infrastructure, priority-5

### [COMPUTERS] Priority 7 complete — conversation ingest pipeline built
Built ingest_conversation.py: parses Claude.ai export ZIP/JSON, auto-detects domain, optionally uses Kimi for summaries, deduplicates via UUID ledger. Built session_end.py: zero-friction interactive tool for end-of-session memU capture. Both scripts live in execution/ on MBP. Copy ingest_conversation.py to GzOpenBrain/execution/ on macbridge for full pipeline access.
Tags: session, priority-7, ingest, memu, conversation-history

### [COMPUTERS] Priority 7 complete — conversation ingest pipeline built
Built ingest_conversation.py: parses Claude.ai export ZIP/JSON, auto-detects domain from keywords, optionally uses Kimi API for AI summaries, deduplicates via UUID ledger at .ingested_conversations.json. Built session_end.py: zero-friction interactive end-of-session memU capture (prompts for domain/title/summary/tags). Both in execution/ on MBP and macbridge. To ingest Claude.ai history: Settings > Export data > download ZIP > python3 ingest_conversation.py claude_export.zip --ai. For quick session capture: python3 session_end.py.
Tags: priority-7, ingest, session-end, memu, claude-ai, conversation-history, kimi

### [COMPUTERS] Continue the Zo and memU verification project [2026-03-24]
Session goal: Continue the Zo and memU verification project. Check CLAUDE.md for full context. Start with Priority 1 — verify memU is running on macbridge port 8001. | Valid. Now pipe-test with a mock Stop event to verify the script runs end-to-end:
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-24

### [COMPUTERS] Continue the Zo and memU verification project [2026-03-24]
Session goal: Continue the Zo and memU verification project. Check CLAUDE.md for full context. Start with Priority 1 — verify memU is running on macbridge port 8001. | Valid. Now pipe-test with a mock Stop event to verify the script runs end-to-end:
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-24

### [COMPUTERS] Continue the Zo and memU verification project [2026-03-24]
Session goal: Continue the Zo and memU verification project. Check CLAUDE.md for full context. Start with Priority 1 — verify memU is running on macbridge port 8001. | Valid. Now pipe-test with a mock Stop event to verify the script runs end-to-end: | Everything works end-to-end:

1. **Hook found** the transcript at `~/.claude/projects/.../8d208929-d572-4eb8-be3e-d5afdcbf344e.jsonl`
2. **Quality gate** passed — 305 tool calls (well above the MIN_TOOL_CALLS=3 threshold)
3. **Domain detected** as COMPUTERS
4. **Title** extracted from first user mes
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-24

### [COMPUTERS] Continue the Zo and memU verification project [2026-03-24]
Session goal: Continue the Zo and memU verification project. Check CLAUDE.md for full context. Start with Priority 1 — verify memU is running on macbridge port 8001. | Everything works end-to-end:

1. **Hook found** the transcript at `~/.claude/projects/.../8d208929-d572-4eb8-be3e-d5afdcbf344e.jsonl`
2. **Quality gate** passed — 305 tool calls (well above the MIN_TOOL_CALLS=3 threshold)
3. **Domain detected** as COMPUTERS
4. **Title** extracted from first user mes | The background research agent completed and found a useful improvement opportunity. Key finding:

**The Stop hook payload includes `transcript_path` directly** — we don't need the glob search at all. The actual stdin payload is:

```json
{
  "session_id": "...",
  "transcript_path": "~/.claude/proje
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-24

### [COMPUTERS] Can you see the new project folder (in claude [2026-03-24]
Session goal: Can you see the new project folder (in claude.ai) for "Develop Excalidraw Skill for agents"?
Tags: computers, auto-captured, claude-code, Excalidrawer_agent, 2026-03-24

### [COMPUTERS] I want to create an Excalidraw filesystem topology diagram of the Zo c [2026-03-24]
Session goal: I want to create an Excalidraw filesystem topology diagram of the Zo computer.
SSH into it as root@zo-computer and run:
  find / -maxdepth 5 -not -path '*/proc/*' -not -path '*/sys/*' \
         -not  | Here are all three files:

**Saved to `~/excalidraw/filesystem/`:**

| File | Size |
|---|---|
| `zo-computer-filesystem.excalidraw` | 111 KB |
| `zo-computer-filesystem.svg` | 21 KB |
| `zo-computer-filesystem.png` | 284 KB |

The diagram maps the Zo Computer's 6 key zones:
- **Purple** — `/__modal
Tags: computers, auto-captured, claude-code, zo-diagram, 2026-03-24

### [zo-diagram] Zo Computer filesystem topology diagram generated
SSHed into root@zo-computer, ran find / -maxdepth 5 to map the filesystem. Zo Computer is a Modal.com sandbox container running Ubuntu Linux. Key findings: /__modal (Modal runtime with cuda-checkpoint, pty-shell, modal-daemon, full debug shell), /__substrate (Zo platform: space app, 6 site templates, 13 data_templates for personal data integrations, honoroute, logging), /home/workspace (Articles, Core Skills, OPENBRAIN, Services, Skills — git repo), /root (affine app, affine-source monorepo, agent-browser AI browser project, techco_env Python venv, Rust/JS/Bun toolchains), services (Docker, PostgreSQL 15, Redis, Grafana Loki, Promtail, supervisord, runit, novnc, Chrome), /zopresets (root-level Zo config), /mnt/cloud and /mnt/pub (storage mounts). Diagram saved to ~/excalidraw/filesystem/zo-computer-filesystem.{excalidraw,svg,png} using the excalidraw-skill workflow.
Tags: zo-computer, filesystem, excalidraw, modal, diagram, topology, infrastructure

### [COMPUTERS] I want to create an Excalidraw filesystem topology diagram of the Zo c [2026-03-24]
Session goal: I want to create an Excalidraw filesystem topology diagram of the Zo computer.
SSH into it as root@zo-computer and run:
  find / -maxdepth 5 -not -path '*/proc/*' -not -path '*/sys/*' \
         -not  | Here are all three files:

**Saved to `~/excalidraw/filesystem/`:**

| File | Size |
|---|---|
| `zo-computer-filesystem.excalidraw` | 111 KB |
| `zo-computer-filesystem.svg` | 21 KB |
| `zo-computer-filesystem.png` | 284 KB |

The diagram maps the Zo Computer's 6 key zones:
- **Purple** — `/__modal | The memU agent was blocked on permissions (no prior context was needed for this task anyway — diagram is done).

Let me write the session results to memU now:
Tags: computers, auto-captured, claude-code, zo-diagram, 2026-03-24

### [COMPUTERS] <command-message>instantiate</command-message> [2026-03-25]
Session goal: <command-message>instantiate</command-message>
<command-name>/instantiate</command-name> | The subagent was denied memU permission. I'll query it directly. | memU is still empty — no entries ingested yet (consistent with last session). Here's my full orientation:

---

## Session Orientation — 2026-03-26

**memU context:** Database is live but empty. No prior entries to recall from memU — context comes from local files (CLAUDE.md, DECISIONS.md, HANDOFF.m
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-25

### [COMPUTERS] <command-message>instantiate</command-message> [2026-03-25]
Session goal: <command-message>instantiate</command-message>
<command-name>/instantiate</command-name> | The subagent was denied memU permission. I'll query it directly. | memU is still empty — no entries ingested yet (consistent with last session). Here's my full orientation:

---

## Session Orientation — 2026-03-26

**memU context:** Database is live but empty. No prior entries to recall from memU — context comes from local files (CLAUDE.md, DECISIONS.md, HANDOFF.m
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-25

### [COMPUTERS] <command-message>instantiate</command-message> [2026-03-25]
Session goal: <command-message>instantiate</command-message>
<command-name>/instantiate</command-name> | Good call. Let me do a quick audit of all pending items on Zo in one shot. | Good data. Let me also check a few more referenced scripts before giving the full audit.
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-25

### [COMPUTERS] <command-message>instantiate</command-message> [2026-03-25]
Session goal: <command-message>instantiate</command-message>
<command-name>/instantiate</command-name> | Network is unreachable — Zo can't reach macbridge via the Cloudflare SSH tunnel directly (it needs `cloudflared access ssh` as a ProxyCommand, which is only configured on the MBP). Let me check what's available on Zo. | `cloudflared` is installed. To SSH from Zo → macbridge through Cloudflare Zero Trust, it needs a **service token** (client ID + secret) rather than the browser-based login. Let me check if one is already on Zo.
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-25

### [COMPUTERS] <command-message>instantiate</command-message> [2026-03-25]
Session goal: <command-message>instantiate</command-message>
<command-name>/instantiate</command-name> | Clean design — runs continuously, logs to `/dev/shm/memu-watchdog.log`, writes state to `/dev/shm/memu_watchdog_state.json`. Ready to wire it in. | P5 done. Watchdog is **RUNNING**, confirmed memU ONLINE, state file written.

**Summary so far:**
- P5 ✅ — `memu-watchdog` wired into supervisord, running, polling every 120s
- memU confirmed online right now
- State readable instantly via `cat /dev/shm/memu_watchdog_state.json` (no network call nee
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-25

### [COMPUTERS] <command-message>instantiate</command-message> [2026-03-25]
Session goal: <command-message>instantiate</command-message>
<command-name>/instantiate</command-name> | Everything working. P4 is done. Also notable: memU now has **48 entries** stored (last one from yesterday's session — it wasn't empty after all, the `query_context` searches just didn't match the terms I used).

Let me now update CLAUDE.md to reflect what's been completed:
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-25

### [COMPUTERS] instantiate [2026-03-25]
Session goal: <command-message>instantiate</command-message>
<command-name>/instantiate</command-name> | Now apply `clean_text` in `build_title` and `extract_summary`, and wire in the dedup check in `main()`: | Now let me do a quick dry-run test to make sure it parses correctly:
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-25

### [COMPUTERS] Zo and memU connection verification [2026-03-24]
You need to download and replace. The `CLAUDE.md` I just created is the new one — it lives in your Claude.ai file outputs, not on your local machine. Your local copy (if you already dropped one in `zo-memu-verification/`) is the older version.

**Steps:**

1. Download the `CLAUDE.md` from the file I just shared above
2. Replace your local file:

```bash
cp ~/Downloads/CLAUDE.md ~/claude-projects/zo-memu-verification/CLAUDE.md
```

3. Verify it has the current content — the bottom line should read:

```
*Generated from Claude.ai session — project: "Zo and memU Verification" — 2026-03-23*
```

-
Tags: computers, claude-ai, conversation, memu, openbrain, 2026-03-24

### [COMPUTERS] Getting started with Claude Code [2026-03-24]
No — let me clear this up because there are two different things getting conflated.

---

## There is Only ONE Global CLAUDE.md — It Never Gets Renamed

`~/.claude/CLAUDE.md` is permanent and global. It loads automatically for **every** Claude Code session on your machine, for every project, forever. You wrote it once. You never rename it, move it, or touch it again except to update your global preferences.

The `global-CLAUDE.md` name I used earlier was just a label to distinguish it when uploading to claude.ai Project Files — because you can't upload a file called `CLAUDE.md` and another cal
Tags: computers, claude-ai, conversation, code, 2026-03-24

### [COMPUTERS] Visual agent organization system for OpenClaw [2026-03-25]
```
This block is not supported on your current device yet.
```

Now let's also update the fileManager to properly infer the NemoClaw system ID from path:
```
This block is not supported on your current device yet.
```


```
This block is not supported on your current device yet.
```

Now build the frontend and run a full end-to-end test with all the new agents:
```
This block is not supported on your current device yet.
```


```
This block is not supported on your current device yet.
```


```
This block is not supported on your current device yet.
```

All 6 agents scanned and correctly cla
Tags: computers, claude-ai, conversation, 2026-03-25

### [COMPUTERS] Building an Excalidraw integration skill [2026-03-24]
Great insight — yes, **Claude Code is the right tool for this specific task**, because it runs directly on your local machine and can SSH to `zo-computer` natively. Here's exactly how to make the handoff smooth:

---

## How to Continue This in Claude Code

### Step 1 — Install Claude Code (if not already)
```bash
npm install -g @anthropic/claude-code
```

### Step 2 — Launch it in a working directory
```bash
mkdir -p ~/projects/zo-diagram && cd ~/projects/zo-diagram
claude
```

### Step 3 — Install the skill
Download the `excalidraw-skill.tar.gz` from this conversation, then:
```bash
tar -xzf
Tags: computers, claude-ai, conversation, 2026-03-24

### [COMPUTERS] Multi-environment NemoClaw and OpenClaw strategy [2026-03-25]
```
This block is not supported on your current device yet.
```


```
This block is not supported on your current device yet.
```

I don't have prior context on your NemoClaw/OpenClaw/Zo setup from past conversations. To give you the most useful brainstorm, let me ask a few clarifying questions:
```
This block is not supported on your current device yet.
```

While you answer those, here's some initial framing to get the conversation going:

The core architectural question with **two OpenClaw installs** plus a **NemoClaw** is really about **identity and specialization** — does each installatio
Tags: computers, claude-ai, conversation, 2026-03-25

### [COMPUTERS] Hosting LLM locally with llama.cpp vs Ollama [2026-03-24]
```
This block is not supported on your current device yet.
```


```
This block is not supported on your current device yet.
```

You're thinking of **llama.cpp** and **Ollama** — you got it right! Quick note: I'm assuming you mean **Llama 3.2 Nemo** (which is actually the **Mistral Nemo 12B** model, sometimes referenced by that name) or possibly **Llama 3.2 3B/1B**. I'll address both scenarios below. Let's break this all down.

---

## llama.cpp vs. Ollama — What Are They?

### llama.cpp
llama.cpp is renowned for its lightweight C++ core, which promises exceptional efficiency. Written in pur
Tags: computers, claude-ai, conversation, 2026-03-24

### [COMPUTERS] Migrating from Google's Antigravity IDE to Claude [2026-03-23]
Unfortunately I can't move conversations between projects myself — that's something you'd do directly in the Claude interface.

Here's how to do it:

1. **Create a Project** — go to claude.ai and click "Projects" in the left sidebar, then create a new one (e.g., "Claude Build Stack" or "Dev Environment Setup")
2. **Start a new chat inside that project** — open the project and start a fresh conversation there
3. **Bring context forward** — either paste a summary of what we've covered, or just link me back to this conversation and I can pull it up with my past chat search

Alternatively, if you 
Tags: computers, claude-ai, conversation, 2026-03-23

### [CARS] Memory update review [2026-03-23]
```
This block is not supported on your current device yet.
```

Here's a summary of what I know about you from my memories:

---

## 🧠 About You

### Identity
- **Location:** Santa Clarita, California, USA
- **Language:** English

### Career
- **Role:** AI User / Prompt Engineer

### Active Projects
- **Data Export** — Building a structured format for AI memory retrieval

### Preferences
- Likes information that's **scannable, organized, and easy to digest**
- Prefers a **collaborative, authentic, and slightly witty** AI persona
- Values **technical accuracy** and proper use of formatting too
Tags: cars, claude-ai, conversation, memu, 2026-03-23

### [COMPUTERS] Automation script logging and date selection for CSV export [2026-02-03]
**THIS IS THE KEY!** Looking at your terminal output:

```
[16:04:02] ▶️ [10-DOWNLOAD] Waiting for Apply button to appear...
[16:04:02] ❌ [10-DOWNLOAD] Apply button never appeared in DOM!
```

The `page.waitForSelector('button:has-text("Apply")')` is **timing out immediately** - it's not even finding the button using Playwright's selector!

But you can SEE the button in the screenshots and your mouse changes to a hand when you hover it. This means:

**The Apply button exists in the DOM, but Playwright's `:has-text()` selector isn't finding it!**

This could be because:
1. The button text has h
Tags: computers, claude-ai, conversation, code, 2026-02-03

### [COMPUTERS] Develop coding standards [2026-02-03]
I'd be happy to help you develop coding standards! Let me ask a couple of key questions to make sure I create something useful for you:

1. **What programming language(s)** do you want these standards to cover? (e.g., Python, JavaScript, Java, a mix?)

2. **What's your team size and experience level?** Are these for a small team, large organization, or personal projects? Are developers mostly junior, senior, or mixed?

Also, if you have any existing documentation (style guides, past code review feedback, or project READMEs), uploading those would help me tailor the standards to your current pr
Tags: computers, claude-ai, conversation, 2026-02-03

### [COMPUTERS] Zo + memU Verification — P4/P5/P7/P8 complete [2026-03-26]
Completed four major priorities: P4 — self_heal.py now auto-SSHes to macbridge to restart openbrain_memu via Cloudflare service token (CF_ACCESS_CLIENT_ID/SECRET added to .zo_secrets, ed25519 keypair provisioned on Zo, SSH config written); P5 — memu_watchdog wired into supervisord-user.conf, polls every 120s, state at /dev/shm/memu_watchdog_state.json; P7 — 10 Claude.ai conversations ingested into memU via ingest_conversation.py with dedup ledger; P8 — auto_capture.py Stop hook already wired, fixed with session-level dedup and <command-message> tag stripping. Also fixed: self_heal.py string matches for detecting offline services (was using wrong format vs sanity_check markdown output). Dashboard + Notebook Bridge both restarted and ONLINE. memU at 68 entries, 25.3KB. openbrain_openclaw confirmed superseded by NemoClaw — not a concern.
Tags: computers, zo-computer, memu, self-heal, supervisord, session-summary, 2026-03-26

### [COMPUTERS] instantiate [2026-03-26]
Session goal: instantiate
/instantiate | Here's my orientation:

**memU context (2026-03-25):** Last session completed the Agent Org Chart v2 webapp — 6 agents scanned and classified, fileManager updated to infer NemoClaw system ID from path, full frontend built and end-to-end tested. The tarball `agent-org-chart-v2.tar.gz` is ready.

**Pr
Tags: computers, auto-captured, claude-code, visual-agent-org-chart-tool, 2026-03-26

### [CAPITAL] instantiate [2026-03-26]
Session goal: instantiate
/instantiate | Waiting for the memU query to complete. Let me also check local memory while that runs. | Local memory is empty (first session). Waiting on memU...

The memU query is still running. Here's my orientation from what I've read so far:

---

**Project: CryptoTax Manager**
- PHP 8.1 / MySQL / Bootstrap 5.3 app for crypto tax tracking
- Hosted at `moneymanager.techstruction.co` (Hostinger shar
Tags: capital, auto-captured, claude-code, money-manager, 2026-03-26

### [CAPITAL] project:/instantiate [2026-03-26]
Session goal: project:/instantiate | Orienting now. Checking memU and reading project files in parallel. | Here's my orientation:

---

## Session Orientation

**memU context:** Only a truncated auto-capture from a previous instantiate attempt — no completed session summary. This appears to be the first real working session in Claude Code for this project.

**Project phase:** Active build / maintenance. 
Tags: capital, auto-captured, claude-code, money-manager, 2026-03-26

### [project] CryptoTax Manager — Session Summary 2026-03-26
## CryptoTax Manager — Session Summary 2026-03-26

### Project
- App: CryptoTax Manager
- Repo: techstruction/money-manager (private, GitHub)
- Live URL: https://moneymanager.techstruction.co
- Stack: PHP 8.3, MySQL 8.0, Nginx, Bootstrap 5.3
- Hosting: macbridge (Ubuntu 24.04, headless), served via Cloudflare Tunnel

### Infrastructure
- macbridge IP: 76.170.126.174 (not publicly accessible, Cloudflare Tunnel only)
- Nginx listens on port 8743 (non-default to avoid conflicts with future test builds)
- Cloudflare Tunnel routes moneymanager.techstruction.co → localhost:8743
- MySQL: DB=moneymanager, user=mmuser (password in /var/www/money-manager/config/installed_config.php)
- App root: /var/www/money-manager/ — web root is /var/www/money-manager/public_html/
- PHP-FPM: php8.3-fpm, socket at /run/php/php8.3-fpm.sock

### What was completed this session
All backlog items from HANDOFF.md completed (P1 through P3):

**P1:**
- KI-001: Post-import warning for zero-price transactions + "Missing Price" filter
- KI-002: Transaction edit modal (pre-populated, per-row edit button)
- KI-003: Duplicate detection via SHA-256 dedup_hash + INSERT IGNORE

**P2:**
- KI-004: AuditLog helper wired at login, logout, import, delete, backup events
- KI-005: Admin user management panel (?page=admin)
- KI-006: Admin-initiated password reset (built into KI-005 admin panel)
- KI-008: CoinGecko historical price fill — PriceHistory helper, 60+ symbol map, deduplicates by (asset, date), 4s rate limiting

**P3:**
- KI-009: NFT/collectible asset_type on transactions, 28% rate in TaxEngine (IRC 1(h)(4))
- KI-010: Multi-portfolio support — portfolios table, portfolio_id FK, PortfoliosController, portfolio selector in topbar, Auth::portfolioClause() filters all controllers
- KI-011: Wash sale detection in TaxEngine — flags losses with same-asset buys within 30 days, ready to disallow when wash_sale_applies flag becomes true
- KI-012: Form 8949 paginated at 14 rows/page with CSS page breaks

**Infrastructure:**
- Git repo initialized, all code on GitHub (techstruction/money-manager, private)
- Full server deployment to macbridge via rsync + setup script
- Nginx configured, PHP-FPM configured, MySQL schema deployed
- Cloudflare Tunnel routing HTTPS traffic

### Current state
- App is fully deployed and responding at https://moneymanager.techstruction.co
- Admin account: admin@moneymanager.local / changeme123 (MUST CHANGE PASSWORD)
- All HANDOFF.md backlog items complete
- No known open issues

### Deployment workflow (future updates)
1. Edit code locally in /Users/tonyg/claude-projects/money-manager
2. git push origin main
3. On macbridge: cd /var/www/money-manager && git pull (need to set up git remote)
4. No build step needed — PHP, no npm

### Note on sudo access
Non-interactive sudo via SSH doesn't work on macbridge due to Defaults use_pty in sudoers. The /etc/sudoers.d/tonyg-nopty file exists but didn't fully resolve it. All privileged operations require running commands interactively on macbridge or writing scripts for the user to run manually.
Tags: cryptotax, money-manager, php, mysql, nginx, macbridge, cloudflare-tunnel, multi-portfolio, wash-sale, form-8949, coingecko, audit-log, session-summary, 2026-03-26

### [money-manager] CryptoTax Manager — deployment complete, all backlog done
CryptoTax Manager (PHP/MySQL/Bootstrap) deployed to macbridge at https://moneymanager.techstruction.co. Nginx on port 8743, Cloudflare Tunnel handles SSL. All 12 HANDOFF.md backlog items (KI-001 through KI-012) completed: transaction edit modal, duplicate detection (SHA-256 dedup_hash + INSERT IGNORE), CoinGecko price fill (PriceHistory.php), audit log (AuditLog.php), admin panel (AdminController), portfolio support (portfolios table + Auth::portfolioClause), NFT/collectible 28% tax rate, wash sale detection, Form 8949 pagination (14 rows/page). DB: moneymanager / mmuser on macbridge. Critical bug fixed: config.php must load installed_config.php BEFORE defining constants (PHP can't redefine). App is live, user logged in successfully. Git repo initialized locally (not yet pushed to GitHub/techstruction).
Tags: money-manager, cryptotax, macbridge, deployment, php, mysql, nginx, cloudflare-tunnel

### [infrastructure] Ollama on tonygs-macbook-pro — Tailscale endpoint
Ollama runs on the MacBook Pro (tonygs-macbook-pro, Tailscale IP 100.127.64.38). Reachable from macbridge at http://100.127.64.38:11434. Model: llama3.1:latest. Already accessible over Tailscale with no firewall changes needed. Used by ZoClaw and now by money-manager PDF parser. macbridge Tailscale IP is 100.100.225.112.
Tags: ollama, tailscale, macbook-pro, llama3.1, infrastructure, money-manager

### [COMPUTERS] instantiate [2026-03-27]
Session goal: instantiate
/instantiate
Tags: computers, auto-captured, claude-code, zo-memu-verification, 2026-03-27

### [COMPUTERS] Claude Code installed and configured on Zo Computer (2026-03-27)
None
Tags: claude-code, zo-computer, infrastructure, setup, memu

### [COMPUTERS] instantiate [2026-03-27]
Session goal: instantiate
/instantiate | Excellent find. ZoClaw is already running with **Mmat identity configured** — further along than the HANDOFF suggested. Let me now check the OPENBRAIN file structure and the Telegram bot identity. | Key discovery: ZoClaw is already live with **`@OG_Mmat_bot`** (`8382972952`) — not `@OG_Datadogs_bot`. The HANDOFF.md may be outdated. Let me read current state docs.
Tags: computers, auto-captured, claude-code, GzOpenBrain-project, 2026-03-27

### [COMPUTERS] GzOpenBrain Session — Data Architecture + GOBI Pipeline (2026-03-28)
Full stack alignment and GOBI ingestion pipeline rebuilt. Key decisions and state:

**ZoClaw (confirmed live):** OpenClaw v2026.3.24, @OG_Mmat_bot (id 8382972952), Mmat identity, nvidia/meta/llama-3.1-8b-instruct. SSH: ssh zo-computer.

**NemoClaw (confirmed live):** OpenClaw v2026.3.11, @OG_Datadogs_bot, Adam persona pending, Ollama llama3.1.

**Data architecture — SQLite replaces all CSV/JSONL:**
- DB: /home/tonyg/GzOpenBrain/openbrain.db (MacBridge, persistent, mounted into openbrain_agent at /app/openbrain.db)
- Schema: items table (5C domain + category + item_type + status), inbox_log (raw capture + classification audit), digests
- Access layer: execution/db.py — all reads/writes go through this module
- 38 records migrated from legacy CAPITAL/COMPUTERS/CARS/CANNAPY/CLAN JSONL and CSV files
- Datasette: gobi_datasette Docker container on MacBridge port 8922, public at data.techstruction.co

**GOBI pipeline (live):**
- Bot: @GzOpenBrainInbox_bot (id 8697070060, token in MacBridge .env)
- Webhook: https://gobi.techstruction.co/webhook → MacBridge Docker openbrain_agent:8769
- Flow: Telegram → inbox_log → Sorter (Llama 3.3 70B) → Bouncer → items table → Telegram receipt
- NVIDIA_API_KEY: nvapi-gZTNFXXrex9TfKoVhA1x... (in /root/.zo_secrets on Zo, MacBridge .env)
- Tested: Claude Code Market Agent idea filed correctly → COMPUTERS/Ideas

**OPENBRAIN folder cleanup:** Alias folders COMP/CAP/CANN deleted from Zo. Canonical: CAPITAL/COMPUTERS/CARS/CANNAPY/CLAN.

**GitHub repo updated:** .env.example (KIMI→NVIDIA, Affine removed), execution scripts (db.py, classify_message.py, telegram_webhook.py, migrate_to_db.py), UPDATE_LEDGER.md.

**Pending:** Agent/sub-agent definitions (separate Claude project), Thoughts & Ideas workflow spec, Stage 8.
Tags: gzopenbrain, sqlite, gobi, pipeline, datasette, infrastructure, mmat, nemoclaw, 2026-03-28


---
## Session: 2026-03-28 (session 2) — Architecture corrected to Zo; Directus deployed

### Key decisions
- Canonical DB location is Zo: /home/workspace/OPENBRAIN/openbrain.db — not MacBridge
- Directus replaces Datasette: deployed on Zo port 8922 via npm/Node.js, supervisord
- All GOBI infra is now on Zo: webhook (port 8769) + DB + Directus

### Live URLs
- GOBI webhook: https://gobi.techstruction.co -> Zo supervisord gobi-webhook:8769
- Directus UI: https://data.techstruction.co -> Zo supervisord directus:8922
- Admin login: admin@techstruction.co / OpBrainAdmin2026!

### Directus setup
- Installed at /home/workspace/directus/ on Zo
- .env has DB_CLIENT=sqlite3, DB_FILENAME=/home/workspace/OPENBRAIN/openbrain.db
- Bootstrap ran: directus_* system tables created alongside items, inbox_log, digests
- Collections auto-detected — all three tables visible and CRUD-enabled in admin UI

### MacBridge status
- openbrain_agent container still running but now idle (webhook moved to Zo)
- DB on MacBridge (/home/tonyg/GzOpenBrain/openbrain.db) is now stale — Zo is authoritative
- Safe to stop openbrain_agent and gobi_datasette containers on MacBridge

### Next priorities
1. Commit Zo config changes to GitHub (directus setup, updated HANDOFF)
2. Stop idle MacBridge containers (openbrain_agent, gobi_datasette)
3. Agent definitions: Mmat VP team (5C), SAM persona, Adam persona — separate Claude project
4. Stage 8: Hardening & Multi-domain Expansion


---
## Session: 2026-03-28 (session 3) — Directus confirmed live; cross-project workflow designed

### What was completed
- GOBI pipeline end-to-end test passed: Telegram msg -> Zo webhook -> Sorter (Llama 3.3 70B) -> Bouncer -> items table -> Directus visible
- data.techstruction.co (Directus) confirmed live and showing real data
- DIRECTUS_USER_GUIDE.md written — full how-to for filters, task management, inbox review
- DECISIONS.md updated: DECISION-20 (Zo is canonical), DECISION-21 (Directus replaces Datasette), DECISION-22 (cross-project sync protocol)
- SYSTEM_STATE.md written to GitHub repo — machine-readable snapshot for other Claude projects

### Cross-project sync protocol (DECISION-22)
When starting the visual-agent-org-chart-tool project:
1. /project:instantiate reads memU (this file) — gets current system state
2. Read SYSTEM_STATE.md from techstruction/GzOpenBrain GitHub repo — full infrastructure snapshot
3. End of org chart session: write decisions back to memU
4. Next GzOpenBrain session: memU reflects org chart changes

### Current system state (authoritative)
- GOBI webhook: gobi.techstruction.co -> Zo supervisord gobi-webhook:8769
- Database: Zo /home/workspace/OPENBRAIN/openbrain.db (canonical)
- Directus UI: data.techstruction.co -> Zo supervisord directus:8922
- Admin: admin@techstruction.co / OpBrainAdmin2026!
- ZoClaw (Mmat / @OG_Mmat_bot): OpenClaw v2026.3.24 on Zo, Nvidia llama-3.1-8b
- NemoClaw (Adam / @OG_Datadogs_bot): OpenClaw v2026.3.11 on MacBridge K3s, Ollama llama3.1
- memU: memu-macbridge.techstruction.co (this machine)
- Ollama: ollama-mbp.techstruction.co -> llama3.1

### What org chart project should work on next
1. Name the 5 VP sub-agents (CAPITAL/COMPUTERS/CARS/CANNAPY/CLAN)
2. Author ZoClaw Rules (systems/openclaw-zo/rules.md) — Mmat + VP team
3. Author NemoClaw Rules (systems/nemoclaw/rules.md) — Adam persona
4. Author Zo native Rules (systems/zo/rules.md) — SAM persona
5. Create agent YAML files for all agents
6. Answer open questions: fix command routing, VP inbox routing

### GitHub state
- techstruction/GzOpenBrain latest commit: feat: add SYSTEM_STATE.md + session docs (pending push)
- All execution scripts, db.py, webhook, Directus notes in repo

### [computers] Session 2026-03-26 — Infrastructure deployed
Tags: computers, claude-ai, visual-agent-org-chart-tool

Tailscale confirmed on all systems: MacBook (100.127.64.38), Zo (100.106.189.97, userspace-only), MacBridge (100.100.225.112, full TUN). Agent Org Chart webapp deployed to Zo at port 7842, managed by supervisord. Zo kernel (4.4.0) cannot load TUN module — Tailscale outbound-only via SOCKS5:1055. MacBridge relay pattern: Zo → SSH -R via SOCKS5 → MacBridge:7842. All Zo services in supervisord-user.conf. Docs written: NETWORKING.md, ADMIN.md.

### [computers] Session 2026-03-27/28 — mmat + adam both live
Tags: computers, claude-ai, visual-agent-org-chart-tool, mmat, adam, nemoclaw

mmat (OpenClaw/Zo): switched from Ollama to nvidia/meta/llama-3.1-8b-instruct after discovering ~37s SOCKS5 proxy overhead (3s actual M3 inference). Telegram confirmed fast. Model: nvidia/meta/llama-3.1-8b-instruct. Subagents: nvidia/deepseek-ai/deepseek-r1-distill-qwen-32b.

adam (NemoClaw/MacBridge): sandbox created via openshell, Telegram bridge live. CRITICAL FIX: stock OpenShell policy uses /usr/local/bin/ paths but sandbox has binaries at /usr/bin/. Node.js CONNECT to integrate.api.nvidia.com gets 403 from egress proxy until custom policy applied. Fix: openshell policy set adam --policy ~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml --wait (policy v3 applied). Both agents confirmed responding on Telegram.

### [computers] System state update — 2026-03-28
Tags: computers, system-state

CORRECTED (was showing Ollama llama3.1 for Adam — that is outdated):
- ZoClaw (Mmat / @OG_Mmat_bot): OpenClaw on Zo, nvidia/meta/llama-3.1-8b-instruct (direct NVIDIA API, no proxy)
- NemoClaw (Adam / @OG_Datadogs_bot): OpenClaw on MacBridge K3s, nvidia/meta/llama-3.1-8b-instruct via OpenShell proxy; custom policy required (adam-sandbox.yaml)
- OpenShell policy recovery: openshell policy set adam --policy ~/GzOpenBrain/NemoClaw/nemoclaw-blueprint/policies/adam-sandbox.yaml --wait


---
## Update: 2026-03-28 — Datasette fully decommissioned; Directus supervisord fix

- Datasette is completely gone from the stack (not on MacBridge, not on Zo)
- Root cause: gobi-datasette was still in /root/.zo/supervisord-custom.conf on Zo, grabbed port 8922 before Directus
- Fix: removed gobi-datasette from custom conf, added directus to custom conf
- KEY LESSON: On Zo, user-added supervisord programs go in /root/.zo/supervisord-custom.conf, NOT /etc/zo/supervisord-user.conf
- data.techstruction.co confirmed serving Directus (admin@techstruction.co / OpBrainAdmin2026!)
- DECISION-23 logged


---
## Update: 2026-03-29 — Zo restart behavior documented

CRITICAL: On every Zo restart, /etc/zo/supervisord-user.conf is reset to its 47-line baseline (only frpc + cloudflared). The [include] directive pointing to /root/.zo/supervisord-custom.conf is LOST.

Fix after every Zo restart:
  ssh zo-computer
  echo -e '[include]
files = /root/.zo/supervisord-custom.conf' >> /etc/zo/supervisord-user.conf
  supervisorctl -c /etc/zo/supervisord-user.conf reread && supervisorctl -c /etc/zo/supervisord-user.conf update

All user programs live in /root/.zo/supervisord-custom.conf (persistent).
The include directive in the main conf is what ties them together — and it resets on restart.

### [gzopenBrain] Session 2026-03-31: Zo Watchdog + Health Monitor Fixes
Work completed on the GzOpenBrain agent stack:

1. FIXED check_zo_services() bug: supervisorctl returns RC=3 when any service is non-RUNNING. zo_ssh() only accepted RC=0, so any FATAL service caused ALL Zo services to show as unknown. Fix: treat RC=3 with stdout as partial success. Also filtered INFO: lines from supervisord include-file logging.

2. DEPLOYED zo-watchdog.py (scripts/zo-watchdog.py): supervisord-managed Python service on Zo.
   - Every 3 min: checks all services, restarts FATAL/STOPPED (3 attempts), Telegram alert on failure (1h dedup)
   - Every 10 min: POST to https://api.zo.computer/snapshot with host_key=techstruction — prevents idle container sleep + checkpoints state
   - Probes Directus /server/health to keep it warm
   - In /root/.zo/supervisord-custom.conf — auto-starts after reprovision
   - Confirmed running, first snapshot POST 202

3. FIXED health monitor OK digest throttle: All-OK check firing every 5min instead of every 4h.
   Root cause: new_state dict built without carrying forward last_ok_digest_ts. Mandatory first save_state() wiped it every run, so elapsed was always infinite.
   Fix: carry last_ok_digest_ts and active_incidents forward in new_state at construction.
   Rule: any inter-run throttle field must be in new_state at construction, not just on success path.

Current state: All 12 Zo services RUNNING. Health monitor throttle working (next OK digest in ~4h). Commit: 7ba0268.
Tags: gzopenBrain, zo-watchdog, adam, mmat, health-monitor, supervisord, session-summary, 2026-03-31

### [gzopenBrain] Session 2026-03-31 (wrap-up): GzOpenBrain UPDATE_LEDGER sync + memU write process
Wrap-up session work:

1. ESTABLISHED UPDATE_LEDGER sync convention: At end of each session, append entries to ~/GzOpenBrain/UPDATE_LEDGER.md on MacBridge and push to github.com:techstruction/GzOpenBrain on production branch. This bridges the two repos: visual-agent-org-chart-tool (Claude Code workspace) and GzOpenBrain (running system).

2. FIXED GzOpenBrain push flow: MacBridge had root-owned file (open-claw/update-check.json) and many uncommitted runtime files, making git stash/rebase fail. Solution: use git worktree to apply changes onto a clean copy of origin/production without touching local working tree. Command pattern:
   git show origin/production:UPDATE_LEDGER.md > /tmp/ledger_remote.md
   cat /tmp/ledger_update.md >> /tmp/ledger_remote.md
   git worktree add /tmp/gz-push origin/production
   cp /tmp/ledger_remote.md /tmp/gz-push/UPDATE_LEDGER.md
   cd /tmp/gz-push && git add UPDATE_LEDGER.md && git commit && git push origin HEAD:production
   git -C ~/GzOpenBrain worktree remove /tmp/gz-push --force

3. DOCUMENTED memU write process: memU MCP server at https://memu-macbridge.techstruction.co/mcp uses SSE transport. Must initialize session first to get mcp-session-id header, then call tools/call with store_entry tool. entry_json requires: domain, title, summary, tags fields.

4. ADDED MacBridge SSH key to GitHub: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHSG/QZHxckhzQVwPypr0+SWjxJ1Amh2VY5rxbMEM1EP adam@macbridge — now GzOpenBrain can push from MacBridge.

Commits this session: 7ba0268 (main work), DECISIONS.md +DECISION-18 (cross-repo sync convention).
Tags: gzopenBrain, update-ledger, memu, session-summary, git-workflow, 2026-03-31


---
## Update: 2026-03-31 — Synced from visual-agent-org-chart-tool (phases 1-4 complete)

### VP Sub-Agent Names (FINAL)
- CAPITAL: Vinny the Vault (vault.yaml)
- COMPUTERS: Rigs (rigs.yaml)
- CARS: Slick (slick.yaml)
- CANNAPY: Doc Flora / Flora from the Field (flora.yaml)
- CLAN: K / Kira the Keeper (kira.yaml)

### Agent Model Correction (CRITICAL)
Both ZoClaw and NemoClaw now use nvidia/meta/llama-3.1-8b-instruct.
NOT Ollama. Ollama added 37s latency via SOCKS5.
All NVIDIA calls route through Rate Queue Proxy on Zo at 127.0.0.1:18792 (36 RPM cap).

### New Infrastructure on Zo
- ACOM webapp: port 7842 (access via ssh -L 7842:localhost:7842 zo-computer -N)
- Rate Queue Proxy: 127.0.0.1:18792 (supervisord)
- Directus HTTPS Proxy: port 8923 (TLS wrapper for 8922)
- Zo Watchdog: /root/zo-watchdog.py (supervisord, restarts services + keepalive every 10min)

### New on MacBridge
- Adam Health Monitor: cron */2 * * * *, self-heals NemoClaw, Telegram alerts
- Adam Daily CEO Brief: cron 0 9 * * * UTC (09:00), Telegram delivery
- Adam Backup: rclone to OneDrive daily 02:00 UTC, 14-day retention (PENDING: rclone OAuth)

### NemoClaw (adam) Key Config
- Tools profile: full (bash/shell execution enabled)
- Sandbox policy: v10 (adam-sandbox.yaml)
- Binary paths: /usr/bin/ (NOT /usr/local/bin/)
- SSH relay to Zo: /sandbox/GzOpenBrain/NemoClaw/scripts/skills/run_skill_on_zo.sh
- Directus access: via SSH relay to https://100.106.189.97:8923
- Secrets: /home/tonyg/.nemoclaw-secrets and /sandbox/.nemoclaw-secrets

### ZoClaw (mmat) Key Config
- Telegram: polling mode, token in /root/.zo_secrets
- Directus API token in /root/.zo_secrets (mmat-agent role: R/W COMPUTERS+CARS)

### New DB Tables in openbrain.db
- agent_registry (7 agents seeded)
- projects
- agent_checkins
- skills

### Skills Deployed (both systems)
- project-manage, openbrain-interact, project-create, project-checkin, project-query
- Directus MCP (20 tools each) via mcporter

### Open Items
- rclone OAuth setup on MacBridge (for OneDrive backup)
- Zo supervisord include re-add after each restart (known limitation, no permanent fix yet)
- Zo native SAM rules still pending
- Cross-system workflow (mmat delegates to adam) not yet tested

### [COMPUTERS] instantiate [2026-03-31]
Session goal: instantiate
/instantiate | Now let me wait for the memU agent to complete before giving the full orientation. | memU agent is done. Here's my full orientation:

---

## Session Orientation

### memU Context Found
Rich history. Last session (2026-03-31) completed: Zo watchdog deployment + health monitor throttle fix (commit 7ba0268), UPDATE_LEDGER sync convention established, MacBridge SSH key added to GitHub,
Tags: computers, auto-captured, claude-code, ZoClaw-NemoClaw-buildout, 2026-03-31

### [GzOpenBrain] NemoClaw OpenSpace persistence solved — 2026-04-01 session
Task 1b complete. CrashLoopBackOff root cause: stale state in openshell-0 SQLite DB after repeated Sandbox CRD patches. Fix: openshell sandbox delete adam + recreate fresh. New sandbox UUID: 854b2d84-783c-4749-bed4-ba5362184e7a. Custom Docker image nemoclaw-custom:v2 (Dockerfile at ~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom) bakes OpenSpace, CLI-Anything, and mcporter.json into /sandbox/ so they survive pod restarts. Key fix in Dockerfile: USER sandbox before pip install so venv files are owned correctly — prevents landlock policy failures. Pod running 1/1, 0 restarts. Directus MCP still offline: pod can't reach Zo Tailscale IP 100.106.189.97:8923 — K3s pods reach MacBridge (100.100.225.112) but not other Tailscale nodes. Fix needs socat relay on MacBridge + sandbox policy update. mcporter installed via npm install -g mcporter. Critical quirk: never use kubectl patch sandbox --type=merge for containers array — wipes all env vars and volumeMounts. Always --type=json.
Tags: nemoclaw, openspace, persistence, crashloopbackoff, kubernetes, docker, sandbox, openshell, directus

### [COMPUTERS] instantiate [2026-03-31]
Session goal: instantiate
/instantiate | Good — I have HANDOFF.md. Let me check the files directory while I wait for memU. | Memory directory exists but is empty. Now let me wait for the memU result.
Tags: computers, auto-captured, claude-code, ZoClaw-NemoClaw-buildout, 2026-03-31

### [COMPUTERS] NemoClaw: nemoclaw-start root cause found and fixed (2026-04-01)
The 'nemoclaw-start: command not found' error in @Adams_Tech_ClawdBot was caused by a legacy node process (nemoclaw/scripts/telegram-bridge.js, PID 77773) running on MacBridge since 2026-03-28. This script polled Adam's Telegram bot token and SSH'd into the pod invoking 'nemoclaw-start' which doesn't exist in nemoclaw-custom:v2. Fix: killed the process (no autostart found). Telegram now handled natively by OpenClaw gateway via channels.telegram config (botToken + dmPolicy:allowlist + allowFrom:[7645251071]). If 409 Conflict errors appear in gateway log after restart, kill any remaining telegram-bridge.js first: ssh macbridge 'kill $(pgrep -f telegram-bridge.js)'. Also discovered: IDENTITY.md persists in /sandbox/.openclaw/workspace/ but OpenClaw reads from /root/.openclaw/workspace/ (ephemeral) — must copy after each pod restart. BUILDSHEET §7 steps 8b and 10 added for both fixes.
Tags: nemoclaw, adam, telegram, nemoclaw-start, bug-fix, buildsheet, openclaw-gateway

### [GzOpenBrain] NemoClaw (Adam) — Session 7: OpenSpace MCP verified, skill loop complete
Session 7 (2026-04-01) completed the Adam skill stack. Key outcomes:

1. OpenSpace MCP logging bug FIXED (persistent in image): openspace/utils/logging.py lines 215+232 patched stdout→stderr. This fixed BrokenPipeError that broke MCP stdio JSON-RPC. Fix lives in /sandbox/ so survives pod restarts.

2. mcporter list clean: 2 healthy servers — openspace (4 tools: execute_task, search_skills, fix_skill, upload_skill) + directus-openbrain (20 tools).

3. Skills fully visible: cli-anything, delegate-task, skill-discovery — all ✓ ready (openclaw-managed). Built-in skill-creator and mcporter also ✓ ready.

4. Skills symlink confirmed: /root/.openclaw/skills → /sandbox/.openclaw/skills. New skills written by skill-creator land in /sandbox/ (persistent) via the symlink.

5. OpenSpace workspace created: /sandbox/openspace-workspace — persistent dir for evolved skills.

6. BUILDSHEET §7 updated: steps 11 (skills symlink) + 12 (workspace) added to restart checklist.

7. Dockerfile updated (BUILDSHEET §4 + ~/GzOpenBrain/NemoClaw/Dockerfile.nemoclaw-custom): openspace-workspace now baked into image for next rebuild.

8. Architectural insight: OpenClaw doesn't expose MCP tools natively. Skills (SKILL.md) teach the agent to call OpenSpace via 'mcporter call openspace.execute_task(...)' from bash. No native MCP wiring needed.

Skill creation→OpenSpace registration loop: skill-creator creates SKILL.md → written to /sandbox/.openclaw/skills/ (persistent via symlink) → execute_task auto-captures patterns → evolved_skills with upload_ready:true → upload_skill registers to OpenSpace cloud.

Adam is fully operational. Current blockers: rclone OAuth (backup), SAM rules migration, skill definitions (web-fetch, research-topic, github-scan).
Tags: nemoclaw, adam, openspace, mcporter, skills, skill-creator, buildsheet, session-summary

### [COMPUTERS] Caveat: The messages below were generated by the user while running lo [2026-04-08]
Session goal: Caveat: The messages below were generated by the user while running local commands. DO NOT respond to these messages or otherwise consider them in your response unless the user explicitly asks you to. | Both files are created. Let me verify the structure looks right: | Done. Here's what was created:

**`CLAUDE.md`** (4.7KB, replacing the 18KB `CLAUDE.BUILD_STATE.md` as the active session guide):
- SSH access in one block
- Current sandbox state in one table
- Abbreviated 12-step checklist with the critical API key warning
- Known open issues
- 6 operating principl
Tags: computers, auto-captured, claude-code, ZoClaw-NemoClaw-buildout, 2026-04-08
