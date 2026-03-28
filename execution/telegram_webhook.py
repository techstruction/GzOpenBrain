"""
telegram_webhook.py — GOBI ingestion webhook
Receives messages from @GzOpenBrainInbox_bot, runs Sorter + Bouncer,
writes to SQLite via db.py. No Affine. No external storage.
"""
import os
import sys
import json
import logging
import subprocess
import requests
from flask import Flask, request
from dotenv import load_dotenv

# Add execution dir to path so db.py is importable
sys.path.insert(0, os.path.dirname(__file__))
import db

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger('gobi_webhook')

app = Flask(__name__)

BOT_TOKEN      = os.getenv('GOBI_BOT_TOKEN')
WEBHOOK_SECRET = os.getenv('GOBI_WEBHOOK_SECRET', '')
HOST           = os.getenv('OPENBRAIN_HOST', '0.0.0.0')
PORT           = int(os.getenv('OPENBRAIN_PORT', '8769'))

DOMAIN_EMOJI = {
    'CAPITAL': '💰', 'COMPUTERS': '💻', 'CARS': '🚗',
    'CANNAPY': '🌿', 'CLAN': '👨‍👩‍👧'
}


def send_receipt(chat_id: str, text: str):
    if not BOT_TOKEN:
        log.warning("GOBI_BOT_TOKEN not set — cannot send receipt")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"},
            timeout=10
        )
    except Exception as e:
        log.error(f"Receipt send failed: {e}")


def run_sorter(message: str) -> dict:
    script = os.path.join(os.path.dirname(__file__), 'classify_message.py')
    try:
        result = subprocess.run(
            ['python3', script, message],
            capture_output=True, text=True, check=True, timeout=130
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        log.error(f"Sorter failed: {e.stderr}")
        return {"domain": "CLAN", "category": "Admin", "intent": "capture",
                "title": "Sorter Error", "summary": message[:100],
                "quality_score": "low", "tags": [], "metadata": {}}
    except Exception as e:
        log.error(f"Sorter exception: {e}")
        return {"domain": "CLAN", "category": "Admin", "intent": "capture",
                "title": "Sorter Exception", "summary": message[:100],
                "quality_score": "low", "tags": [], "metadata": {}}


def run_bouncer(classified: dict) -> tuple[str, str]:
    """Returns (decision, reason) — 'pass' or 'flag'."""
    script = os.path.join(os.path.dirname(__file__), 'bouncer_check.py')
    try:
        result = subprocess.run(
            ['python3', script, json.dumps(classified)],
            capture_output=True, text=True, check=True, timeout=15
        )
        out = json.loads(result.stdout)
        return out.get('decision', 'pass'), out.get('reason', '')
    except Exception as e:
        log.error(f"Bouncer exception: {e}")
        return 'pass', 'Bouncer error — defaulting to pass'


def process_message(chat_id: str, text: str):
    log.info(f"[{chat_id}] Received: {text[:80]}")

    # 1. Raw capture → inbox_log
    inbox_id = db.add_to_inbox(raw_content=text, source='telegram', sender_id=chat_id)
    log.info(f"[{chat_id}] inbox_log id={inbox_id}")

    # 2. Sorter
    classified = run_sorter(text)
    db.update_inbox_classification(inbox_id, classified)
    log.info(f"[{chat_id}] Classified → {classified.get('domain')} / {classified.get('category')}")

    # 3. Bouncer
    decision, reason = run_bouncer(classified)
    log.info(f"[{chat_id}] Bouncer → {decision} ({reason})")

    # 4. Route
    if decision == 'pass':
        item_id = db.promote_to_items(inbox_id, classified, source='telegram')
        domain = classified.get('domain', 'CLAN')
        category = classified.get('category', 'Admin')
        title = classified.get('title', 'Note')
        emoji = DOMAIN_EMOJI.get(domain, '📁')
        receipt = f"{emoji} *{domain}* → {category}\n📌 *{title}*\n✅ Filed to OpenBrain"
    else:
        db.flag_inbox(inbox_id, reason)
        receipt = (
            f"🚩 *Flagged for review*\n"
            f"_{reason}_\n"
            f"Your note is saved in the inbox. Check the dashboard to review."
        )

    send_receipt(chat_id, receipt)


@app.route('/webhook', methods=['POST'])
def webhook():
    if WEBHOOK_SECRET:
        token = request.headers.get('X-Telegram-Bot-Api-Secret-Token', '')
        if token != WEBHOOK_SECRET:
            return 'Forbidden', 403

    data = request.get_json(silent=True)
    if not data:
        return 'ok', 200

    msg = data.get('message', {})
    text = msg.get('text', '').strip()
    chat_id = str(msg.get('chat', {}).get('id', ''))

    if text and chat_id:
        process_message(chat_id, text)

    return 'ok', 200


@app.route('/health')
def health():
    return json.dumps({"status": "ok", "bot": "GzOpenBrainInbox_bot"}), 200, \
           {'Content-Type': 'application/json'}


if __name__ == '__main__':
    db.init_db()
    log.info(f"GOBI webhook starting on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=False)
