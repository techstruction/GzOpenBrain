#!/usr/bin/env python3
"""
test_pipeline.py — End-to-End Pipeline Simulator
Simulates the OpenBrain pipeline from message receipt to storage.
"""

import os
import sys
import json
import logging
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import from the webhook server script
# We avoid running the Flask app, just the logic
import execution.telegram_webhook as webhook

# Configure logging
logging.basicConfig(level=logging.INFO)

def simulate_pipeline(text: str):
    print(f"\n--- Simulating Pipeline for: '{text}' ---")
    
    # Mock send_message to avoid actual Telegram calls
    webhook.send_message = lambda chat_id, text, **kwargs: print(f"  [TELEGRAM OUT] {text}")
    
    try:
        # We manually call process_message
        # chat_id '12345' is our test user
        webhook.process_message('12345', text)
    except Exception as e:
        print(f"  [PIPELINE ERROR] {e}")

if __name__ == "__main__":
    # Test cases
    test_messages = [
        "Plan for the new car project: redo the engine block.",
        "Buy BTC if it drops below 95k",
        "/ask help me write a python script for scraping"
    ]
    
    for msg in test_messages:
        simulate_pipeline(msg)
        print("-" * 40)
