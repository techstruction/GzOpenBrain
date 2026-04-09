#!/usr/bin/env python3
"""
generate_digest.py — OpenBrain Tap on the Shoulder

Summarises recent activity across all domains and generates a proactive
digest message for the user.

Usage:
    python3 execution/generate_digest.py --daily
    python3 execution/generate_digest.py --weekly
"""

import os
import sys
import json
import uuid
import argparse
import datetime
import subprocess
from dotenv import load_dotenv

# ─── Load env ─────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

MEMU_SERVER_URL = os.getenv("MEMU_SERVER_URL", "https://memu-macbridge.techstruction.co")
MEMU_MCP_ENDPOINT = f"{MEMU_SERVER_URL}/mcp"
STATS_LEDGER = os.path.join(os.path.dirname(__file__), '..', 'open-claw', 'memu_stats_ledger.jsonl')


# ─── memU Stats ───────────────────────────────────────────────────────────────
def _memu_init_session():
    init_payload = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "digest", "version": "1.0"}}
    })
    cmd = ["curl", "-s", "--max-time", "10", "-X", "POST", MEMU_MCP_ENDPOINT,
           "-H", "Content-Type: application/json",
           "-H", "Accept: application/json, text/event-stream",
           "-D", "/tmp/digest_memu_headers.txt", "-d", init_payload]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    try:
        with open("/tmp/digest_memu_headers.txt") as f:
            for line in f:
                if line.lower().startswith("mcp-session-id:"):
                    return line.split(":", 1)[1].strip()
    except Exception:
        pass
    return None


def _memu_call(session_id, method, params):
    payload = json.dumps({"jsonrpc": "2.0", "id": str(uuid.uuid4()),
                           "method": method, "params": params})
    cmd = ["curl", "-s", "--max-time", "10", "-X", "POST", MEMU_MCP_ENDPOINT,
           "-H", "Content-Type: application/json",
           "-H", "Accept: application/json, text/event-stream",
           "-H", f"mcp-session-id: {session_id}", "-d", payload]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        if line.startswith("data:"):
            try:
                return json.loads(line[5:].strip())
            except Exception:
                pass
    return None


def get_memu_stats():
    """Query memU for live stats and append to local ledger for trend tracking."""
    stats = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "reachable": False,
        "entry_count": 0,
        "size_bytes": 0,
        "last_entry_domain": None,
        "last_entry_title": None,
    }
    try:
        session_id = _memu_init_session()
        if not session_id:
            return stats

        stats["reachable"] = True
        response = _memu_call(session_id, "tools/call",
                              {"name": "read_all", "arguments": {"limit": 9999}})
        if not response:
            return stats

        content = response.get("result", {}).get("content", [])
        raw = content[0].get("text", "") if isinstance(content, list) and content else ""
        entries = [e for e in raw.split("###") if e.strip()]
        stats["entry_count"] = len(entries)
        stats["size_bytes"] = len(raw.encode("utf-8"))

        if entries:
            first_line = entries[-1].strip().splitlines()[0] if entries[-1].strip() else ""
            if first_line.startswith("[") and "]" in first_line:
                bracket_end = first_line.index("]")
                stats["last_entry_domain"] = first_line[1:bracket_end].strip()
                stats["last_entry_title"] = first_line[bracket_end + 1:].strip()
    except Exception:
        pass

    # Append snapshot to local ledger for trend tracking
    try:
        os.makedirs(os.path.dirname(STATS_LEDGER), exist_ok=True)
        with open(STATS_LEDGER, "a") as f:
            f.write(json.dumps(stats) + "\n")
    except Exception:
        pass

    return stats


def format_memu_section(stats):
    """Format memU stats for inclusion in digest."""
    if not stats["reachable"]:
        return "🔴 *memU Memory Store:* OFFLINE — check macbridge"

    size_kb = stats["size_bytes"] / 1024
    lines = [f"🧠 *memU Memory Store:* {stats['entry_count']} entries · {size_kb:.1f} KB"]
    if stats["last_entry_domain"] and stats["last_entry_title"]:
        lines.append(f"   └ Last: [{stats['last_entry_domain']}] {stats['last_entry_title']}")
    return "\n".join(lines)


def load_memu_trend():
    """Load recent snapshots from ledger to show trend (last 7 days)."""
    if not os.path.exists(STATS_LEDGER):
        return None
    try:
        with open(STATS_LEDGER) as f:
            lines = [json.loads(l) for l in f if l.strip()]
        if len(lines) < 2:
            return None
        # Last 7 data points
        recent = lines[-7:]
        first_count = recent[0]["entry_count"]
        last_count = recent[-1]["entry_count"]
        delta = last_count - first_count
        if delta > 0:
            return f"   └ +{delta} entries added over last {len(recent)} checks"
        return None
    except Exception:
        return None


# ─── Domain Entries ───────────────────────────────────────────────────────────
def get_recent_entries(days=1):
    """
    Fetches recent entries from the 5 domain databases.
    Placeholder: returns simulated entries for now.
    """
    # In production, this would call Affine API or a local DB
    return [
        {"domain": "Capital", "category": "Ideas", "title": "BTC rebalancing", "summary": "Thinking about rebalancing after BTC hit 100k."},
        {"domain": "Computers", "category": "Projects", "title": "OpenBrain Sorter", "summary": "Sorter agent is now online and classifying Telegram messages."},
        {"domain": "Clan", "category": "Admin", "title": "Family Dinner", "summary": "Order food for next week's family gathering."}
    ]


def generate_daily_digest():
    """Generates the daily 'Tap on the Shoulder'."""
    entries = get_recent_entries(days=1)

    digest = f"🧠 *OpenBrain Daily Digest* — {datetime.date.today().strftime('%B %d')}\n\n"

    if not entries:
        digest += "Rest day! No new entries captured yesterday.\n\n"
    else:
        # Group by domain
        domains = {}
        for e in entries:
            d = e['domain']
            if d not in domains: domains[d] = []
            domains[d].append(e)

        for domain, items in domains.items():
            emoji = {'Capital': '💰', 'Computers': '💻', 'Cars': '🚗', 'Cannapy': '🌿', 'Clan': '👨‍👩‍👧'}.get(domain, '📁')
            digest += f"{emoji} *{domain}*\n"
            for item in items:
                digest += f"• *{item['title']}*: {item['summary']}\n"
            digest += "\n"

    digest += "🚀 *Next Actions:*\n• Review the BTC strategy in the Capital dashboard.\n\n"

    # ── memU Infrastructure Section ──────────────────────────────────────────
    digest += "─────────────────────\n"
    memu_stats = get_memu_stats()
    digest += format_memu_section(memu_stats) + "\n"
    trend = load_memu_trend()
    if trend:
        digest += trend + "\n"

    return digest




def send_telegram(text):
    """Send text to TELEGRAM_OWNER_CHAT_ID via the bot."""
    import requests
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_OWNER_CHAT_ID")
    if not bot_token or not chat_id:
        print("⚠️  TELEGRAM_BOT_TOKEN or TELEGRAM_OWNER_CHAT_ID not set — skipping send.", file=sys.stderr)
        return False
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        print(f"⚠️  Telegram send failed: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain — Generate Digest')
    parser.add_argument('--daily', action='store_true', help='Generate daily digest')
    parser.add_argument('--weekly', action='store_true', help='Generate weekly digest')
    parser.add_argument('--send', action='store_true', help='Send digest via Telegram')
    args = parser.parse_args()

    if args.daily:
        text = generate_daily_digest()
        print(text)
        if args.send:
            ok = send_telegram(text)
            print("✅ Sent to Telegram." if ok else "❌ Telegram send failed.")
    elif args.weekly:
        print("Weekly digest logic coming soon...")
    else:
        parser.print_help()
