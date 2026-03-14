# Directive: Filing Cabinet (Storage)

> **Last updated:** 2026-03-09
> **Script:** `execution/write_to_affine.py`
> **Stage:** 2 — Storage Layer

---

## Purpose

The Filing Cabinet agent is responsible for persistent storage. It takes a validated classification and writes it to the appropriate workspace and table in Affine.

## Inputs

| Input | Source | Notes |
|---|---|---|
| `entry` | Sorter JSON | Validated output from Sorter/Bouncer |

## Outputs

JSON object (stdout):
```json
{
  "success": true|false,
  "message": "Protocol confirmation or error details"
}
```

## Setup & Configuration

Requires values in `.env`:
- `AFFINE_API_URL`: Base URL of your self-hosted Affine instance.
- `AFFINE_API_TOKEN`: Integration token from Affine settings.
- `AFFINE_WORKSPACE_ID`: Target workspace UUID.

## Logic: Domain Routing

Entries are routed based on their `domain` and `category`:
- **Domains**: Capital, Computers, Cars, Cannapy, Clan.
- **Sub-Categories**: People, Projects, Ideas, Admin, Inbox Log.

The script currently maps these to `metadata` fields in an Affine collection. Depending on your Affine setup (tables vs. pages), you may need to adjust the `save_to_affine()` function in the script to point to specific database IDs.

## Usage

```bash
# Store an entry
python3 execution/write_to_affine.py '{"domain": "Computers", "category": "Projects", "title": "Setup OpenBrain", ...}'
```

## Status: MVP Simulation

The current script is a **functional template**. It requires the user to:
1.  Verify the specific API endpoint for their Affine version (e.g., `/api/v1/...`).
2.  Maps the `target_payload` to match their Affine database schema.

## Self-Heal Protocol

When storage fails:
1.  Check `AFFINE_API_URL` and `AFFINE_API_TOKEN` reachability.
2.  Verify the workspace ID in `MASTER_PLAN.md` vs `.env`.
3.  Update the `endpoint` or `target_payload` in `execution/write_to_affine.py`.
4.  Update this directive with any new schema requirements.
5.  Log the fix in `UPDATE_LEDGER.md`.
