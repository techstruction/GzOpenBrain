#!/usr/bin/env python3
"""
telegram_webhook.py — OpenBrain Telegram Webhook Server

Receives incoming Telegram messages and routes them through the OpenBrain pipeline:
  Telegram message → classify_message.py → bouncer_check.py → write_to_affine.py
  → Send receipt back to user via Telegram

Usage:
    python3 execution/telegram_webhook.py

Requirements:
    pip install flask python-dotenv requests

Expose via ngrok (dev) or reverse proxy (prod):
    ngrok http 8765
    Then set webhook: https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://YOUR_URL/webhook
"""

import os
import sys
import json
import logging
import subprocess
import requests
from flask import Flask, request, abort
from dotenv import load_dotenv

# ─── Load env ─────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

BOT_TOKEN      = os.getenv('TELEGRAM_BOT_TOKEN', '')
WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET', '')
OWNER_CHAT_ID  = os.getenv('TELEGRAM_OWNER_CHAT_ID', '')
PORT           = int(os.getenv('OPENBRAIN_PORT', 8765))
HOST           = os.getenv('OPENBRAIN_HOST', '0.0.0.0')
SCRIPTS_DIR    = os.path.dirname(__file__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger('openbrain')

app = Flask(__name__)


# ─── Telegram helpers ─────────────────────────────────────────────────────────
def send_message(chat_id: str, text: str, parse_mode: str = 'Markdown'):
    """Send a message back to a Telegram chat."""
    if not BOT_TOKEN:
        log.error("TELEGRAM_BOT_TOKEN not set")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
    except Exception as e:
        log.error(f"Failed to send Telegram message to {chat_id}: {e}")
        # Proactively check DNS if it fails
        try:
            import socket
            log.info(f"DNS check for api.telegram.org: {socket.gethostbyname('api.telegram.org')}")
        except:
            log.error("DNS check failed: api.telegram.org is unreachable")


def run_script(script_name: str, *args) -> dict:
    """Run an execution script and return its parsed JSON stdout."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    cmd = [sys.executable, script_path, *args]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"Script exited {result.returncode}")
        return json.loads(result.stdout)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Script returned invalid JSON: {e}\nOutput: {result.stdout[:200]}")


# ─── Pipeline ─────────────────────────────────────────────────────────────────
def process_message(chat_id: str, raw_text: str):
    """Full pipeline: classify → bouncer → store → receipt."""
    log.info(f"Processing message from {chat_id}: {raw_text[:80]}")

    # Step 1: Classify
    try:
        classified = run_script('classify_message.py', raw_text)
        log.info(f"Classified → [{classified['domain']}] [{classified['category']}] Intent: {classified['intent']}")
    except Exception as e:
        log.error(f"Classify failed: {e}")
        send_message(chat_id, f"⚠️ *Sorter error* — couldn't classify your message.\n`{e}`")
        return

    # Step 1.5: Architect Review (Writer-Critic Loop)
    try:
        review = run_script('architect_critic.py', raw_text, json.dumps(classified))
        if review.get('verdict') == 'fail':
            log.info(f"Critic flagged classification: {review.get('reason')}")
            # Apply suggested fixes if provided
            fix = review.get('suggested_fix', {})
            if fix:
                for key, val in fix.items():
                    if val and key in classified:
                        log.info(f"Applying Critic fix: {key} -> {val}")
                        classified[key] = val
    except Exception as e:
        log.warning(f"Architect Critic failed, proceeding: {e}")

    # Step 2: Handle Intent
    if classified.get('intent') == 'execute':
        send_message(chat_id, "⚡️ *Handing off to Specialist (OpenClaw)...*")
        try:
            dispatch_result = run_script('agent_dispatcher.py', raw_text)
            if dispatch_result.get('status') == 'success':
                agent_name = dispatch_result.get('agent', 'Unknown')
                data = dispatch_result.get('data', {})
                payloads = data.get('result', {}).get('payloads', [])
                if payloads and 'text' in payloads[0]:
                    response_text = payloads[0]['text']
                    send_message(chat_id, f"🤖 *{agent_name} responds:*\n\n{response_text}")
                else:
                    send_message(chat_id, f"🤖 *{agent_name}* processed the task but returned no text.")
            else:
                error_msg = dispatch_result.get('message', 'Unknown error')
                send_message(chat_id, f"❌ *Dispatch failed:* {error_msg}")
        except Exception as e:
            log.error(f"Auto-dispatch failed: {e}")
            send_message(chat_id, f"❌ *System error:* {str(e)}")
        return

    # Step 3: Bouncer check
    try:
        bouncer = run_script('bouncer_check.py', json.dumps(classified))
        decision = bouncer.get('decision', 'flag')
        log.info(f"Bouncer decision: {decision}")
    except Exception as e:
        log.error(f"Bouncer failed: {e}")
        bouncer = {'decision': 'flag', 'reason': f"Bouncer error: {e}"}
        decision = 'flag'

    # Step 4: Store (if passed bouncer)
    stored = False
    if decision == 'pass':
        try:
            store_result = run_script('write_to_affine.py', json.dumps(classified))
            stored = store_result.get('success', False)
            log.info(f"Stored to Affine: {stored}")
        except Exception as e:
            log.error(f"Affine store failed: {e}")
            stored = False

    # Step A: memU Memory Sync (Keep specialists informed)
    try:
        run_script('memu_sync.py', json.dumps(classified))
        log.info("Synced to memU (OpenClaw Memory)")
    except Exception as e:
        log.error(f"memU sync failed: {e}")

    # Step 5: Confirm receipt to user
    domain = classified.get('domain', '?')
    category = classified.get('category', '?')
    title = classified.get('title', raw_text[:40])
    quality = classified.get('quality_score', '?')

    domain_emoji = {
        'Capital': '💰', 'Computers': '💻', 'Cars': '🚗',
        'Cannapy': '🌿', 'Clan': '👨‍👩‍👧'
    }.get(domain, '📁')

    if decision == 'pass':
        status = "✅ Filed" if stored else "🗂 Classified (Affine error)"
        msg = (
            f"{domain_emoji} *{domain}* → {category}\n"
            f"📌 *{title}*\n"
            f"Quality: `{quality}`\n"
            f"{status}"
        )
    else:
        reason = bouncer.get('reason', 'Quality too low')
        msg = (
            f"⚠️ *Flagged by Bouncer*\n"
            f"Reason: {reason}\n"
            f"Logged to Inbox for review."
        )

    send_message(chat_id, msg)
    log.info(f"Receipt sent to {chat_id}")


# ─── Webhook endpoint ─────────────────────────────────────────────────────────
@app.route('/webhook', methods=['POST'])
def webhook():
    # Validate secret header if configured
    if WEBHOOK_SECRET:
        secret = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
        if secret != WEBHOOK_SECRET:
            log.warning("Webhook received with invalid secret")
            abort(403)

    data = request.get_json(silent=True)
    if not data:
        abort(400)

    log.debug(f"Incoming webhook: {json.dumps(data)[:200]}")

    # Extract message
    message = data.get('message') or data.get('edited_message')
    if not message:
        return 'ok', 200  # Ignore non-message updates (channel posts, etc.)

    chat_id = str(message.get('chat', {}).get('id', ''))
    text = message.get('text', '').strip()

    if not text:
        send_message(chat_id, "ℹ️ Only text messages are supported right now. Send me a note!")
        return 'ok', 200

    # Handle commands
    if text.startswith('/start'):
        send_message(chat_id, (
            "👋 *OpenBrain is online.*\n\n"
            "Drop any thought, link, idea, or note here and I'll classify and file it for you.\n\n"
            "Commands:\n"
            "/status — System status\n"
            "/help — Show this message"
        ))
        return 'ok', 200

    if text.startswith('/status'):
        send_message(chat_id, (
            "🧠 *OpenBrain Status*\n\n"
            "✅ Capture layer: online\n"
            "✅ Sorter agent: online\n"
            "✅ Bouncer gate: online\n"
            "✅ Specialist: OpenClaw (Nvidia/Ollama)\n"
            "✅ Affine storage: connected\n"
            "🔲 Proactive digests: pending"
        ))
        return 'ok', 200

    if text.startswith('/help'):
        send_message(chat_id, (
            "*How to use OpenBrain:*\n"
            "Just type or paste anything — a thought, a link, a note.\n"
            "The Sorter will classify it into:\n"
            "• 💰 Capital | 💻 Computers | 🚗 Cars | 🌿 Cannapy | 👨‍👩‍👧 Clan\n\n"
            "🚀 *Specialists*:\n"
            "Use `/ask [task]` to summon a specialist agent (OpenClaw).\n"
            "Example: `/ask Write a script to scrape my stock portfolio.`"
        ))
        return 'ok', 200

    if text.startswith('/ask'):
        task_desc = text[len('/ask'):].strip()
        if not task_desc:
            send_message(chat_id, "🔍 Please provide a task description. Example: `/ask help me with...` ")
            return 'ok', 200
        
        send_message(chat_id, "⚡️ *Handing off to Specialist (OpenClaw)...*")
        try:
            # Use the existing run_script helper to call the dispatcher
            dispatch_result = run_script('agent_dispatcher.py', task_desc)
            
            if dispatch_result.get('status') == 'success':
                agent_name = dispatch_result.get('agent', 'Unknown')
                data = dispatch_result.get('data', {})
                
                # Extract text response from OpenClaw structure
                # We saw it in: result -> payloads -> [0] -> text
                payloads = data.get('result', {}).get('payloads', [])
                if payloads and 'text' in payloads[0]:
                    response_text = payloads[0]['text']
                    send_message(chat_id, f"🤖 *{agent_name} responds:*\n\n{response_text}")
                else:
                    send_message(chat_id, f"🤖 *{agent_name}* processed the task but returned no text.\n`{json.dumps(data)[:200]}...`")
            else:
                error_msg = dispatch_result.get('message', 'Unknown error')
                send_message(chat_id, f"❌ *Dispatch failed:* {error_msg}")
        except Exception as e:
            log.error(f"Manual ask failed: {e}")
            send_message(chat_id, f"❌ *System error:* {str(e)}")
        return 'ok', 200

    # Process the message through the pipeline
    process_message(chat_id, text)
    return 'ok', 200


@app.route('/health', methods=['GET'])
def health():
    return json.dumps({"status": "ok", "service": "OpenBrain"}), 200, {'Content-Type': 'application/json'}


# ─── Webhook registration helper ──────────────────────────────────────────────
def register_webhook(public_url: str):
    """Register the webhook URL with Telegram."""
    if not BOT_TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not set in .env")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    payload = {
        "url": f"{public_url}/webhook",
        "secret_token": WEBHOOK_SECRET or "",
        "allowed_updates": ["message", "edited_message"]
    }
    r = requests.post(url, json=payload, timeout=10)
    print(f"Webhook registration: {r.json()}")


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    if '--register' in sys.argv:
        idx = sys.argv.index('--register')
        if idx + 1 < len(sys.argv):
            register_webhook(sys.argv[idx + 1])
        else:
            print("Usage: python3 telegram_webhook.py --register https://your-public-url.ngrok.io")
        sys.exit(0)

    if not BOT_TOKEN or BOT_TOKEN == 'your_telegram_bot_token_here':
        print("⚠️  TELEGRAM_BOT_TOKEN not set in .env — server will start but Telegram won't connect.")
        print("   Get a token from @BotFather on Telegram, then update your .env file.")

    log.info(f"Starting OpenBrain webhook server on {HOST}:{PORT}")
    log.info(f"Intelligence backend: {os.getenv('INTELLIGENCE_BACKEND', 'kimi')}")
    app.run(host=HOST, port=PORT, debug=False)
