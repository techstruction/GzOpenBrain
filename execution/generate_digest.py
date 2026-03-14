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
import argparse
import datetime
from dotenv import load_dotenv

# ─── Load env ─────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

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
    
    if not entries:
        return "🧠 *OpenBrain Daily Digest*\n\nRest day! No new entries captured yesterday."

    digest = f"🧠 *OpenBrain Daily Digest* — {datetime.date.today().strftime('%B %d')}\n\n"
    
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

    digest += "🚀 *Next Actions:*\n• Review the BTC strategy in the Capital dashboard."
    
    return digest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain — Generate Digest')
    parser.add_argument('--daily', action='store_true', help='Generate daily digest')
    parser.add_argument('--weekly', action='store_true', help='Generate weekly digest')
    args = parser.parse_args()

    if args.daily:
        print(generate_daily_digest())
    elif args.weekly:
        print("Weekly digest logic coming soon...")
    else:
        parser.print_help()
