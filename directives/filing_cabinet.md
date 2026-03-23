# Directive: Filing Cabinet (Storage)

> **Last updated:** 2026-03-21
> **Tool:** Zo Computer
> **Stage:** 2 — Storage Layer (Shifted from Affine)

---

## Purpose

The Filing Cabinet agent is responsible for persistent storage in **Zo Computer**. It takes a validated classification and writes it to the appropriate domain repository and dataset.

## Logic: Domain Routing

Entries are routed based on their `domain` and `category`:
- **Domains**: Capital, Computers, Cars, Cannapy, Clan.
- **Sub-Categories**: People, Projects, Ideas, Admin, Inbox Log.

## Integration Note

Zo Computer is utilized for its built-in functions to handle agents and various datasets out of the box. The integration layer will be built to interface with Zo Computer's native agentic functions.

## Self-Heal Protocol

When storage fails:
1. Check Zo Computer connectivity and repository status.
2. Verify API tokens or authentication required for Zo Computer.
3. Update this directive with any new schema or endpoint requirements.
4. Log the fix in `UPDATE_LEDGER.md`.
