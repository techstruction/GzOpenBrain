# Directive: Sorter Agent

> **Last updated:** 2026-03-09
> **Script:** `execution/classify_message.py`
> **Stage:** 1 — Capture Layer

---

## Purpose

The Sorter classifies any raw incoming message (from Telegram or any other source) into a structured JSON entry matching the OpenBrain Form schema. It routes information to the correct domain and sub-category.

## Inputs

| Input | Source | Notes |
|---|---|---|
| `message` | CLI arg or stdin | Raw text from Telegram or other capture source |

## Outputs

JSON object (stdout):
```json
{
  "domain": "Capital|Computers|Cars|Cannapy|Clan",
  "category": "People|Projects|Ideas|Admin|Inbox Log",
  "title": "Short descriptive title (max 8 words)",
  "summary": "1-2 sentence richer summary",
  "source_raw": "Original message text",
  "tags": ["tag1", "tag2"],
  "quality_score": "high|medium|low",
  "created_at": "ISO8601 timestamp"
}
```

## Intelligence Backends

Configured via `INTELLIGENCE_BACKEND` in `.env`:
- `kimi` → **Kimi k2.5** via Nvidia API (`KIMI_API_KEY` required)
  - Disable Thinking mode if latency is too high (controlled by model parameters)
- `ollama` → **Local Ollama** on Windows server (`OLLAMA_HOST` + `OLLAMA_MODEL` required)
  - Ensure the Windows server is reachable from this machine

**Automatic fallback:** If the primary backend fails, the script automatically attempts the other backend and logs a warning to stderr.

## Usage

```bash
# Classify a message
python3 execution/classify_message.py "BTC broke 100k, thinking about rebalancing"

# From stdin
echo "Need to fix the Ollama timeout issue" | python3 execution/classify_message.py --stdin

# Run built-in tests
python3 execution/classify_message.py --test
```

## Domain Reference (quick lookup)

| Domain | Covers |
|---|---|
| Capital | Finance, trading, investments, charts, money |
| Computers | AI, coding, servers, tools, tech projects |
| Cars | Vehicles, parts, automotive projects |
| Cannapy | Cannabis industry research and operations |
| Clan | Family, personal, health, relationships |

## Known Edge Cases & Learnings

*(Updated by self-heal protocol — append here when issues are found)*

- **Model adds markdown fences to JSON output (Ollama):** Script strips ` ```json ` fences automatically in `classify_with_ollama()`.
- **Domain validation:** If model returns an unrecognised domain, defaults to `Clan`. If category unrecognised, defaults to `Inbox Log`.
- **Empty messages:** Script raises `ValueError` and exits with code 1. Telegram webhook filters these before they reach the script.
- **Kimi Thinking mode latency:** If Kimi is slow, check if Thinking is enabled by default on the API endpoint. Use `temperature=0.1` to minimise stochastic output.

## Troubleshooting

| Error | Likely Cause | Fix |
|---|---|---|
| `KIMI_API_KEY not set` | `.env` not populated | Copy `.env.example` → `.env` and add key |
| `Cannot connect to Ollama` | Server offline or wrong IP | Check `OLLAMA_HOST` in `.env`; verify server is running |
| `Invalid JSON from model` | Model output format drift | Check if model wraps response in markdown; update stripping logic in `classify_with_ollama()` |
| `Both backends failed` | Both services down | Check API keys and host connectivity |

## Self-Heal Protocol

When this script breaks in production:
1. Read the full error from logs
2. Fix `execution/classify_message.py`
3. Run `python3 execution/classify_message.py --test` to verify
4. Update the **Known Edge Cases** section above with what you learned
5. Append an entry to `UPDATE_LEDGER.md`
