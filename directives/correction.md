# Directive: Fix Button (Correction)

> **Last updated:** 2026-03-09
> **Script:** `execution/apply_correction.py`
> **Stage:** 6 — Fix Button

---

## Purpose

The Fix Button is the human-in-the-loop mechanism that allows the user to override AI decisions. This ensures the system stays accurate and "trustworthy" by allowing easy corrections.

## Use Cases

1.  **Misclassification:** Sorter puts a "Car" noted into "Computers".
2.  **Quality Override:** User wants to file something the Bouncer flagged.

## Interface (Telegram)

Corrections are triggered by **replying** to a classification receipt:
- `/fix domain:Cars`
- `/fix category:Projects`
- `/fix move:Clan`

## Implementation Flow

1.  **Foreman** (webhook server) detects a `/fix` command in a reply message.
2.  Server extracts the ID of the original classification from the reply context.
3.  Invokes `execution/apply_correction.py` with the new parameters.
4.  Confirmation receipt sent back to user.
5.  *(Optional)* The correction is stored in a `Feedback` table to fine-tune the Sorter prompt later.

## Known Edge Cases & Learnings

- **Ambiguous IDs:** The original message or the receipt must contain a unique ID (currently relying on Telegram's internal message ID or a custom UUID).
- **Format:** The command parser must be flexible with whitespace and casing.

## Self-Heal Protocol

If corrections aren't "sticking":
1.  Verify the mapping between Telegram message IDs and Affine document IDs.
2.  Test the script locally with simulated IDs.
3.  Update the `apply_fix` logic in `execution/apply_correction.py`.
4.  Log the fix in `UPDATE_LEDGER.md`.
