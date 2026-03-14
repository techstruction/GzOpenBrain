# Directive: Bouncer Agent

> **Last updated:** 2026-03-09
> **Script:** `execution/bouncer_check.py`
> **Stage:** 3 — Quality Gate

---

## Purpose

The Bouncer act as a quality filter between classification and storage. It ensures that only high-quality, well-defined information makes it into the primary domain databases, while noise or ambiguous notes are flagged for review.

## Inputs

| Input | Source | Notes |
|---|---|---|
| `entry` | Sorter JSON | The output from `classify_message.py` |

## Outputs

JSON object (stdout):
```json
{
  "decision": "pass|flag",
  "reason": "String explaining the choice"
}
```

## Logic Gate Criteria

The Bouncer "Flags" an entry if:
1.  **Quality Score is 'low'**: Explicitly identified as low value by the Sorter.
2.  **Generic Fallback**: The domain is 'Clan' and category is 'Inbox Log' (indicates Sorter couldn't find a specific bucket).
3.  **Vague Summary**: The generated summary is fewer than 3 words.

## Usage

```bash
# Check a classification result
python3 execution/bouncer_check.py '{"domain": "Capital", "quality_score": "high", "summary": "Bitcoin investment strategy"}'
```

## Implementation Flow

1.  **Sorter** classifies message.
2.  **Foreman** (webhook server) passes JSON to Bouncer.
3.  If **PASS** -> Proceed to `write_to_affine.py` in the specific domain/category.
4.  If **FLAG** -> File in the domain's "Inbox Log" table with the flag metadata.

## Self-Heal Protocol

When quality logic needs adjustment:
1.  Update `evaluate_quality()` in `execution/bouncer_check.py`.
2.  Test with various Sorter outputs.
3.  Update this directive's **Logic Gate Criteria**.
4.  Log the change in `UPDATE_LEDGER.md`.
