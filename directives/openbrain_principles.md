# Directive: OpenBrain Core Principles

> **Last updated:** 2026-03-09
> **Applies to:** All agents operating within the OpenBrain system

---

## Purpose

This directive defines the guiding principles all agents must follow when building, maintaining, or extending the OpenBrain system. These are not rules — they are principles. Apply judgement. When in doubt, refer back here.

---

## Principles

### 1. Architecture is Portable. Tools Are Not.
Build the workflow around the *process*, not the current tools. If Affine is replaced tomorrow, the agents, routing logic, and schemas should survive with minimal changes. Never hard-code a tool into the core logic — abstract it.

### 2. Principle-Based Guidance > Rule-Based Guidance
Agents should understand *why* something works, not just follow a checklist. Incorporate software development best practices:
- Separation of concerns
- Don't swallow errors
- Test-driven development where applicable
- Keep functions small and composable

### 3. If the Agent Builds It, the Agent Can Maintain It
All scripts in `execution/` are owned by the agent. If a script breaks:
1. Read the error message and stack trace carefully
2. Fix the script
3. Test the fix (without consuming paid tokens if avoidable — confirm with user if cost is involved)
4. Update the relevant directive with what was learned
5. Log the change in `UPDATE_LEDGER.md`

> **This is non-negotiable.** Never leave a broken script without updating the directive that references it.

### 4. Your System is Infrastructure, Not Just a Tool
Design for restartability. A system designed for "perfection" will fail. Design for:
- **Restartability:** The system should survive cold starts, gaps in use, and context loss
- **Maintainability over cleverness:** Prefer simple, well-documented pipelines over clever but fragile ones
- **Fewer parts = fewer failure points**

### 5. Reduce the Human's Job to One Behaviour
The user's only required action is to drop a message into Telegram. Everything downstream (classify, store, surface) is automatic. Any friction beyond that is a design failure.

### 6. Always Build a Trust Mechanism, Not Just a Capability
Every output must have a quality gate (Bouncer) and an audit trail (Receipt/Inbox Log). The system should default to safe behaviour when uncertain — flag for human review rather than silently mis-file.

### 7. Outputs: Small, Frequent, Actionable
Prefer short digests with concrete next actions over long reports. Use the "next action" as the unit of execution.

### 8. Prefer Routing Over Organizing
Let the Sorter agent route information to the right domain automatically. Do not require the user to manually organise.

### 9. Keep Schemas Small
3–5 fields per database table. Complexity accumulates — resist it.

### 10. Build One Workflow Then Attach Modules
MVP first:
```
Telegram → Sorter → Bouncer → Affine → Daily Digest → Telegram
```
Then extend. Never build modules without a working core.

---

## Self-Heal Protocol (When Scripts Break)

```
1. Error occurs
2. Read full error + stack trace
3. Diagnose root cause
4. Fix the script in execution/
5. Test the fix locally (no paid API calls without user confirmation)
6. Update the directive that references this script with:
   - What broke
   - What the fix was
   - Any new edge cases to watch for
7. Append an entry to UPDATE_LEDGER.md
8. System is now stronger than before
```

---

## Related Files
- `MASTER_PLAN.md` — Full build roadmap and stage checklist
- `UPDATE_LEDGER.md` — Append-only change history
- `directives/system_architecture.md` — Component breakdown
- `directives/agent_roster.md` — Agent roles and responsibilities
- `AGENTS.md` — Root orchestration instructions
