# Directive: Bouncer Agent

> **Last updated:** 2026-03-28
> **Script:** `execution/bouncer_check.py`
> **Stage:** 3 — Quality Gate

---

## Purpose

The Bouncer acts as a quality filter between classification (Sorter) and storage (SQLite). Ensures only well-defined information is promoted to the `items` table; noise stays in `inbox_log` for human review in Datasette.

## Inputs

| Input | Source | Notes |
|---|---|---|
| `entry` | Sorter JSON | Output from `classify_message.py` |

## Outputs

```json
{
  "decision": "pass|flag",
  "reason": "String explaining the choice"
}
```

## Logic Gate Criteria

**FLAG if any of:**
1. `quality_score == "low"` — explicitly identified as low value by Sorter
2. `summary` has fewer than 3 words — too vague
3. `domain == "CLAN"` AND `category == "Admin"` — fallback classification, needs review

**PASS otherwise.**

## Storage Routing

| Decision | Action |
|---|---|
| PASS | `db.promote_to_items()` → row created in `items` table; `inbox_log.processed=1` |
| FLAG | `db.flag_inbox()` → stays in `inbox_log` with `bouncer_decision='flag'`; visible in Datasette unprocessed view |

Human reviews flagged items at `https://data.techstruction.co/openbrain/inbox_log?processed=0`

## Usage

```bash
python3 execution/bouncer_check.py '{"domain": "CAPITAL", "quality_score": "high", "summary": "Bitcoin investment strategy"}'
```

## Self-Heal Protocol

1. Update `evaluate_quality()` in `execution/bouncer_check.py`
2. Test with representative Sorter outputs
3. Update **Logic Gate Criteria** above
4. Append to `UPDATE_LEDGER.md`
