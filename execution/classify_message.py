#!/usr/bin/env python3
"""
classify_message.py — OpenBrain Sorter Agent

Classifies a raw text message into a domain, category, and structured JSON entry.
Supports Kimi k2.5 (Nvidia API) and Ollama backends via INTELLIGENCE_BACKEND env var.

Usage:
    python3 execution/classify_message.py "your raw message here"
    python3 execution/classify_message.py --stdin   (reads from stdin)
    python3 execution/classify_message.py --test    (runs built-in test cases)

Output (stdout):
    JSON object matching the OpenBrain Form schema.
    Exits with code 0 on success, 1 on error.
"""

import os
import sys
import json
import argparse
import datetime
from dotenv import load_dotenv

# ─── Load env ─────────────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

INTELLIGENCE_BACKEND = os.getenv('INTELLIGENCE_BACKEND', 'kimi').lower()

# ─── OpenBrain Schema ─────────────────────────────────────────────────────────
DOMAINS = ['Capital', 'Computers', 'Cars', 'Cannapy', 'Clan']
CATEGORIES = ['People', 'Projects', 'Ideas', 'Admin', 'Inbox Log']

CLASSIFICATION_PROMPT = """You are the Sorter agent for the OpenBrain personal second-brain system.

Your job is to classify a raw incoming message into a structured JSON entry.

## 🧭 Domains (pick exactly one)
- Capital: Finance, trading, investments, cash management, charts, money
- Computers: AI tools, coding, servers, scripts, tech projects, software, hardware
- Cars: Automotive, vehicles, parts, repairs, car research
- Cannapy: Cannabis industry, related research, operations, hydroponics, growth
- Clan: Family, personal relationships, health, personal development, social

## 📁 Categories (pick exactly one)
- People: Contacts, individuals, relationship notes
- Projects: Active or planned work, tasks, goals
- Ideas: Unvalidated thoughts, research seeds, concepts to explore
- Admin: Documents, logistics, processes, reminders, schedules
- Inbox Log: Use ONLY if the message is purely conversational or doesn't fit the above.

## 📝 Instructions
1. Read the message carefully.
2. If the user mentions a domain (e.g., 'for my car' or 'Cannapy'), prioritize that domain.
3. Choose the single best domain and category.
4. Write a concise title (max 8 words).
5. Write a 1-2 sentence summary that captures the core meaning.
6. Extract 3-5 relevant tags (lowercase, no spaces, use underscores).
7. Determine intent: capture (default) | execute (if it's a specific invitation for a specialist agent to perform a task, write/run code, research a topic, or solve a problem). Examples: "Write a script", "Search for the latest news on...", "Help me debug...", "Test this function" -> execute. "Idea for a new app", "Note about the car", "Buying BTC today" -> capture.
8. Set quality_score: high | medium | low (high = actionable/specific).
9. Return ONLY valid JSON – no code fences, no markdown, no explanation.

## Output schema
{
  "domain": "string",
  "category": "string",
  "intent": "capture|execute",
  "title": "string",
  "summary": "string",
  "source_raw": "string",
  "tags": ["string"],
  "quality_score": "high|medium|low",
  "created_at": "ISO8601"
}"""


# ─── Backend: Kimi (Nvidia API) ───────────────────────────────────────────────
def classify_with_kimi(message: str) -> dict:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")

    api_key = os.getenv('KIMI_API_KEY')
    base_url = os.getenv('KIMI_BASE_URL', 'https://integrate.api.nvidia.com/v1')
    model = os.getenv('KIMI_MODEL', 'moonshotai/kimi-k2-5')

    if not api_key or api_key == 'your_kimi_api_key_here':
        raise RuntimeError("KIMI_API_KEY not set in .env")

    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": f"Message to classify:\n\n{message}"}
        ],
        temperature=0.1,  # Low temp for consistent classification
        max_tokens=1024,
        timeout=120
    )

    raw = response.choices[0].message.content.strip()
    return json.loads(raw)


# ─── Backend: Ollama ──────────────────────────────────────────────────────────
def classify_with_ollama(message: str) -> dict:
    try:
        import requests
    except ImportError:
        raise RuntimeError("requests package not installed. Run: pip install requests")

    host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    model = os.getenv('OLLAMA_MODEL', 'qwen3:latest')

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": f"Message to classify:\n\n{message}"}
        ],
        "stream": False,
        "options": {"temperature": 0.1}
    }

    try:
        resp = requests.post(f"{host}/api/chat", json=payload, timeout=120)
        resp.raise_for_status()
    except requests.exceptions.ConnectionError:
        raise RuntimeError(f"Cannot connect to Ollama at {host}. Is the server running?")

    raw = resp.json()['message']['content'].strip()

    # Strip markdown code fences if model adds them
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


# ─── Main classifier ──────────────────────────────────────────────────────────
def classify(message: str) -> dict:
    """Classify a message using the configured backend."""
    if not message or not message.strip():
        raise ValueError("Cannot classify an empty message")

    backend = INTELLIGENCE_BACKEND

    try:
        if backend == 'kimi':
            print(f"[DEBUG] Using Kimi backend: {os.getenv('KIMI_MODEL')}", file=sys.stderr)
            result = classify_with_kimi(message)
        elif backend == 'ollama':
            print(f"[DEBUG] Using Ollama backend: {os.getenv('OLLAMA_MODEL')}", file=sys.stderr)
            result = classify_with_ollama(message)
        else:
            raise RuntimeError(f"Unknown INTELLIGENCE_BACKEND: '{backend}'. Use 'kimi' or 'ollama'.")
    except Exception as e:
        # If primary backend fails, attempt fallback
        fallback = 'ollama' if backend == 'kimi' else 'kimi'
        print(f"[WARN] {backend} backend failed: {e}. Attempting fallback to {fallback}...", file=sys.stderr)
        try:
            if fallback == 'ollama':
                result = classify_with_ollama(message)
            else:
                result = classify_with_kimi(message)
        except Exception as fallback_error:
            raise RuntimeError(f"Both backends failed. Primary: {e} | Fallback: {fallback_error}")

    # Validate and stamp required fields
    if result.get('domain') not in DOMAINS:
        result['domain'] = 'Clan'  # Safe fallback
    if result.get('category') not in CATEGORIES:
        result['category'] = 'Inbox Log'
    if result.get('intent') not in ['capture', 'execute']:
        result['intent'] = 'capture'

    result['source_raw'] = message
    result['created_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return result


# ─── Built-in tests ───────────────────────────────────────────────────────────
def run_tests():
    test_cases = [
        "BTC broke 100k again, might be time to rebalance the portfolio",
        "Need to fix the Ollama server on the Windows box, it keeps timing out",
        "Found a great deal on a used E46 M3 — only 80k miles, clean title",
        "Dad's birthday is next week, need to order something",
        "Interesting idea: use the Sorter agent to auto-tag emails too",
    ]
    print("Running built-in test cases...\n")
    for i, msg in enumerate(test_cases, 1):
        print(f"Test {i}: {msg[:60]}...")
        try:
            result = classify(msg)
            print(f"  → [{result['domain']}] [{result['category']}] — {result['title']}")
            print(f"     Quality: {result['quality_score']} | Tags: {result['tags']}")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
        print()


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain Sorter — classify a message')
    parser.add_argument('message', nargs='?', help='Raw message text to classify')
    parser.add_argument('--stdin', action='store_true', help='Read message from stdin')
    parser.add_argument('--test', action='store_true', help='Run built-in test cases')
    args = parser.parse_args()

    if args.test:
        run_tests()
        sys.exit(0)

    if args.stdin:
        raw_message = sys.stdin.read().strip()
    elif args.message:
        raw_message = args.message
    else:
        print("Error: provide a message argument or use --stdin", file=sys.stderr)
        sys.exit(1)

    try:
        output = classify(raw_message)
        print(json.dumps(output, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)
