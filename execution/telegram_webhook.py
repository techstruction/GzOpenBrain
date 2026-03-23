import os
import sys
import json
import logging
import requests
import subprocess
from flask import Flask, request
from dotenv import load_dotenv

# ─── Config ───────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger('telegram_webhook')

app = Flask(__name__)

BOT_TOKEN      = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_SECRET = os.getenv('TELEGRAM_WEBHOOK_SECRET')
HOST           = os.getenv('OPENBRAIN_HOST', '0.0.0.0')
PORT           = int(os.getenv('OPENBRAIN_PORT', 8769))

# ─── Helpers ──────────────────────────────────────────────────────────────────
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        log.error(f"Failed to send message: {e}")

def run_script(script_name, arg1, arg2=None):
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    cmd = ["python3", script_path, arg1]
    if arg2:
        cmd.append(arg2)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        log.error(f"Execution failed ({script_name}): {e}")
        if hasattr(e, 'stderr'): log.error(f"Stderr: {e.stderr}")
        return {"error": str(e)}

def store_context(chat_id, text):
    ctx_file = f"/tmp/openbrain_ctx_{chat_id}.txt"
    try:
        with open(ctx_file, 'w') as f:
            f.write(text[:2000]) # Cap at 2k chars
    except Exception as e:
        log.error(f"Failed to store context: {e}")

def get_context(chat_id):
    ctx_file = f"/tmp/openbrain_ctx_{chat_id}.txt"
    if os.path.exists(ctx_file):
        try:
            with open(ctx_file, 'r') as f:
                return f.read()
        except:
            pass
    return None

# ─── Message Processor ────────────────────────────────────────────────────────
def process_message(chat_id, text):
    log.info(f"Processing message from {chat_id}: {text}")
    
    # 1. Determine if we should use context
    context = None
    lower_text = text.lower()
    if len(text) < 30 or any(x in lower_text for x in ["save", "add", "this", "it", "keep"]):
        context = get_context(chat_id)
        if context: log.info("Using retrieved context for classification")

    # 2. Classify
    try:
        cmd = ["python3", os.path.join(os.path.dirname(__file__), 'classify_message.py'), text]
        if context:
            cmd.extend(["--context", context])
        
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        classified = json.loads(proc.stdout)
    except Exception as e:
        log.error(f"Classification failed: {e}")
        classified = {"domain": "Clan", "category": "Inbox Log", "intent": "capture"}

    # 3. Handle Intent
    if classified.get('intent') == 'execute':
        send_message(chat_id, "⚡️ *Handing off to Specialist (OpenClaw)...*")
        try:
            res = run_script('agent_dispatcher.py', text)
            if res.get('status') == 'success':
                data = res.get('data', {})
                payloads = data.get('result', {}).get('payloads', [])
                if payloads and 'text' in payloads[0]:
                    ans = payloads[0]['text']
                    send_message(chat_id, f"🤖 *OpenClaw responds:*\n\n{ans}")
                    store_context(chat_id, ans) # Store response for next "save"
                else:
                    send_message(chat_id, "🤖 Specialist processed the task but returned no text.")
            else:
                send_message(chat_id, f"❌ *Dispatch failed:* {res.get('message', 'Unknown')}")
        except Exception as e:
            log.error(f"Dispatch error: {e}")
        return

    # 4. Store (Dual-Path)
    stored_affine = False
    stored_memu = False
    
    # Path A: Affine (Database for Humans)
    try:
        log.info("Path A: Filing to Affine...")
        res = run_script('write_to_affine.py', json.dumps(classified))
        stored_affine = res.get('success', False)
    except Exception as e:
        log.error(f"Affine storage error: {e}")

    # Path B: memU (Memory for Agents)
    try:
        log.info("Path B: Syncing to memU memory...")
        # For now, we use the existing memu_sync.py logic which is compatible with the memU MCP backend
        res = run_script('memu_sync.py', json.dumps(classified))
        stored_memu = res.get('success', False)
    except Exception as e:
        log.error(f"memU storage error: {e}")

    # 5. Receipt
    domain = classified.get('domain', 'Clan')
    emoji = {'Capital':'💰','Computers':'💻','Cars':'🚗','Cannapy':'🌿','Clan':'👨‍👩‍👧'}.get(domain, '📁')
    
    if stored_affine and stored_memu:
        status = "✅ Filed to OpenBrain & memU"
    elif stored_affine:
        status = "✅ Filed to OpenBrain (memU error)"
    elif stored_memu:
        status = "✅ Synced to memU (OpenBrain error)"
    else:
        status = "❌ Storage Error"
        
    receipt = f"{emoji} *{domain}* → {classified.get('category','?')}\n📌 *{classified.get('title','Note')}*\n{status}"
    send_message(chat_id, receipt)

@app.route('/webhook', methods=['POST'])
def webhook():
    if WEBHOOK_SECRET:
        if request.headers.get('X-Telegram-Bot-Api-Secret-Token') != WEBHOOK_SECRET:
            return 'Forbidden', 403
    
    data = request.json
    if 'message' in data and 'text' in data['message']:
        chat_id = data['message']['chat']['id']
        text = data['message']['text']
        process_message(chat_id, text)
    
    return 'ok', 200

@app.route('/health')
def health():
    return json.dumps({"status": "ok"}), 200, {'Content-Type':'application/json'}

if __name__ == '__main__':
    log.info(f"OpenBrain Webhook active on {PORT}")
    app.run(host=HOST, port=PORT, debug=False)
