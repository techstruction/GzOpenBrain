# Directive: Sorter Agent

> **Last updated:** 2026-03-28
> **Script:** `execution/classify_message.py`
> **Stage:** 1 — Capture Layer

---

## Purpose

The Sorter classifies any raw incoming message (from GOBI Telegram bot or any other source) into a structured JSON entry matching the OpenBrain schema. Routes information to the correct 5C domain and sub-category.

## Inputs

| Input | Source | Notes |
|---|---|---|
| `message` | CLI arg or stdin | Raw text from Telegram or other capture source |
| `--context` | Optional CLI arg | Prior context for short/ambiguous messages |

## Outputs

JSON object (stdout):
```json
{
  "domain": "CAPITAL|COMPUTERS|CARS|CANNAPY|CLAN",
  "category": "People|Projects|Ideas|Admin",
  "intent": "capture|research|execute",
  "title": "Short descriptive title (max 8 words)",
  "summary": "1-2 sentence richer summary",
  "source_raw": "Original message text",
  "tags": ["tag1", "tag2"],
  "quality_score": "high|medium|low",
  "metadata": {},
  "created_at": "ISO8601 timestamp"
}
```

## Intelligence Backend

**Primary:** Nvidia API — `meta/llama-3.3-70b-instruct` at 40 RPM (free tier)
- Env vars: `NVIDIA_API_KEY`, `NVIDIA_BASE_URL`, `NVIDIA_MODEL`

**Fallback (no API key):** Returns domain=CLAN/category=Admin with quality_score=low

## Hashtag Overrides (deterministic, applied before LLM)

| Tag | Routes to |
|---|---|
| `$cap`, `#cash`, `#charts` | CAPITAL |
| `#comp`, `#sys`, `#tech` | COMPUTERS |
| `#cars` | CARS |
| `#cann`, `#plants` | CANNAPY |
| `#clan`, `#fam` | CLAN |
| `#people`, `#projects`, `#ideas`, `#admin` | Respective category |

## Usage

```bash
python3 execution/classify_message.py "BTC broke 100k"
python3 execution/classify_message.py --test
echo "Fix the NemoClaw config" | python3 execution/classify_message.py --stdin
```

## Storage

Output is consumed by `telegram_webhook.py`, which writes to SQLite via `db.py`:
- Raw message → `inbox_log` table
- Classified result → updates `inbox_log` row
- Bouncer PASS → promotes to `items` table

## Known Edge Cases

- **Markdown fences in LLM output:** Stripped automatically with regex.
- **Domain normalization:** `~ CAPITAL ~` style LLM output normalized to `CAPITAL`.
- **Empty messages:** Filtered by webhook before reaching Sorter.
- **API timeout:** 130s timeout; returns fallback dict on failure.

## Self-Heal Protocol

1. Read error from `/dev/shm/gobi-webhook_err.log` on Zo (or `docker logs openbrain_agent` on MacBridge)
2. Fix `execution/classify_message.py`
3. Run `python3 execution/classify_message.py --test`
4. Update **Known Edge Cases** above
5. Append to `UPDATE_LEDGER.md`
