# Directive: Tap on the Shoulder (Digest)

> **Last updated:** 2026-03-09
> **Script:** `execution/generate_digest.py`
> **Stage:** 5 — Digest Layer

---

## Purpose

The "Tap on the Shoulder" mechanism ensures that captured information doesn't just sit in a database — it proactively surfaces relevant nodes to the user at a useful cadence.

## Cadence

| Type | Frequency | Goal |
|---|---|---|
| **Daily** | Morning (8 AM) | Review yesterday's captures and highlight actionable next steps. |
| **Weekly** | Sundays | High-level summary of themes and project progress across all 5 domains. |

## Inputs

- **Filing Cabinet (Affine/Inbox Log)**: The script queries recently created entries.
- **Bouncer Flags**: Flagged items needing human review are prioritized in the digest.

## Outputs

A formatted Markdown message sent to the user via Telegram.

## Usage

```bash
# Generate and print the daily digest
python3 execution/generate_digest.py --daily
```

## Implementation Flow

1.  **Foreman** (via cron or scheduler) triggers `execution/generate_digest.py`.
2.  Script queries the 5 domain databases for entries within the time window.
3.  Intelligence backend (Kimi/Ollama) summarizes the collection into key themes.
4.  Formatted message is sent to the `TELEGRAM_OWNER_CHAT_ID`.

## Known Edge Cases & Learnings

- **Silent Days:** If no items were captured, the digest reflects a "Rest Day" to maintain the cadence without being noisy.
- **Formatting:** Telegram Markdown V2 is picky; the script uses standard Markdown which the webhook server's `send_message` helper handles.

## Self-Heal Protocol

When the digest looks wrong or fails to send:
1.  Verify the query logic in `execution/generate_digest.py`.
2.  Check the Telegram bot status.
3.  Update the template or intelligence prompt in the script.
4.  Log the change in `UPDATE_LEDGER.md`.
