# Directive: Telegram Capture Layer

> **Last updated:** 2026-03-09
> **Script:** `execution/telegram_webhook.py`
> **Stage:** 1 — Capture Layer

---

## Purpose

Telegram is the primary input pane for OpenBrain. The webhook server receives messages and routes them through the full pipeline: Classify → Bouncer → Store → Receipt.

## Setup (One-Time)

### Step 1: Create a Telegram Bot
1. Open Telegram and message `@BotFather`
2. Send `/newbot` and follow the prompts
3. Copy the API token into `.env` as `TELEGRAM_BOT_TOKEN`
4. Get your personal Telegram user ID: message `@userinfobot` → copy the ID into `.env` as `TELEGRAM_OWNER_CHAT_ID`
5. Set a webhook secret (any random string) in `.env` as `TELEGRAM_WEBHOOK_SECRET`

### Step 2: Install Dependencies
```bash
pip3 install -r requirements.txt
```

### Step 3: Start the server
```bash
python3 execution/telegram_webhook.py
```

### Step 4: Expose publicly (for development)
Install ngrok (free tier is fine):
```bash
brew install ngrok
ngrok http 8765
```
Copy the `https://xxxx.ngrok.io` URL.

### Step 5: Register webhook with Telegram
```bash
python3 execution/telegram_webhook.py --register https://YOUR_NGROK_URL
```
Or manually:
```
https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://YOUR_URL/webhook&secret_token=YOUR_SECRET
```

### Step 6: Test
Send a message to your bot. You should receive a classification receipt reply.

## Commands Handled

| Command | Response |
|---|---|
| `/start` | Welcome message + instructions |
| `/status` | Pipeline component status |
| `/help` | Usage guide |
| (any text) | Full pipeline: classify → bouncer → store → receipt |

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/webhook` | POST | Telegram webhook receiver |
| `/health` | GET | Health check (returns `{"status": "ok"}`) |

## Configuration (`.env`)

```env
TELEGRAM_BOT_TOKEN=        # From @BotFather
TELEGRAM_WEBHOOK_SECRET=   # Any random string
TELEGRAM_OWNER_CHAT_ID=    # Your personal Telegram ID
OPENBRAIN_PORT=8765        # Server port
OPENBRAIN_HOST=0.0.0.0    # Bind address
```

## Pipeline Resilience

The webhook handles partial pipeline failures gracefully:
- If `classify_message.py` fails → sends error notice to user, pipeline stops
- If `bouncer_check.py` not found → defaults to `pass` (stores everything), logs warning
- If `write_to_affine.py` not found → classifies only, notifies user storage is not connected
- Always sends a Telegram receipt to the user so they know the message was received

## Production Deployment

For production (to survive reboots), run via pm2:
```bash
pm2 start "python3 /Users/tonyg/Documents/GzOpenBrain/execution/telegram_webhook.py" --name openbrain-webhook
pm2 save
pm2 startup
```

Use a stable public URL (e.g., Cloudflare Tunnel, or a VPS reverse proxy) instead of ngrok.

## Known Edge Cases & Learnings

*(Updated by self-heal protocol — append here when issues are found)*

- **Webhook secret validation:** If you change `TELEGRAM_WEBHOOK_SECRET`, you must re-register the webhook.
- **Non-text messages (photos, voice, etc.):** Currently not supported — server replies with a guidance message.
- **Edited messages:** Treated the same as new messages.

## Troubleshooting

| Error | Likely Cause | Fix |
|---|---|---|
| 403 on webhook | Secret mismatch | Re-register webhook with correct secret |
| Bot not responding | Webhook not registered | Run `--register` step above |
| Port already in use | Another process on 8765 | Change `OPENBRAIN_PORT` in `.env` |
| `classify_message.py` fails | API key missing | Check `.env` for `KIMI_API_KEY` or `OLLAMA_HOST` |

## Self-Heal Protocol

When this script breaks:
1. Read the server logs (`pm2 logs openbrain-webhook`)
2. Fix `execution/telegram_webhook.py`
3. Restart: `pm2 restart openbrain-webhook`
4. Test by sending a message to your bot
5. Update **Known Edge Cases** above
6. Append an entry to `UPDATE_LEDGER.md`
