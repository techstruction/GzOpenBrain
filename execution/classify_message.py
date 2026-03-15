#!/usr/bin/env python3
"""
OpenBrain Sorter — classify_message.py

Classifies incoming messages into Domain/Category using LLMs.
Supports context for better classification of short commands like "save it".

Usage:
    python3 execution/classify_message.py "Message text"
    python3 execution/classify_message.py "save it" --context "Trading charts research..."
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
2. If provided, use the CONTEXT to understand ambiguous messages (like "save this" or "add it").
3. Choose the single best domain and category.
4. Write a concise title (max 8 words).
5. Write a 1-2 sentence summary that captures the core meaning.
6. Extract 3-5 relevant tags (lowercase, no spaces, use underscores).
7. Determine intent: capture (default) | execute (if it's a specific invitation for a specialist agent to perform a task).
8. Set quality_score: high | medium | low.
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
def classify_with_kimi(message: str, context: str = None) -> dict:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai package not installed. Run: pip install openai")

    api_key = os.getenv('KIMI_API_KEY')
    base_url = os.getenv('KIMI_BASE_URL', 'https://integrate.api.nvidia.com/v1')
    model = os.getenv('KIMI_MODEL', 'meta/llama-3.1-405b-instruct')

    if not api_key or api_key == 'your_kimi_api_key_here':
        raise RuntimeError("KIMI_API_KEY not set in .env")

    client = OpenAI(api_key=api_key, base_url=base_url)
    
    user_content = f"Message to classify:\n\n{message}"
    if context:
        user_content = f"CONTEXT (previous research/output):\n{context}\n\n---\n\n{user_content}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": user_content}
        ],
        temperature=0.1,
        max_tokens=1024,
        timeout=120
    )

    raw = response.choices[0].message.content.strip()
    return json.loads(raw)


# ─── Backend: Ollama ──────────────────────────────────────────────────────────
def classify_with_ollama(message: str, context: str = None) -> dict:
    try:
        import requests
    except ImportError:
        raise RuntimeError("requests package not installed. Run: pip install requests")

    host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    model = os.getenv('OLLAMA_MODEL', 'qwen3:latest')

    user_content = f"Message to classify:\n\n{message}"
    if context:
        user_content = f"CONTEXT (previous research/output):\n{context}\n\n---\n\n{user_content}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": user_content}
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
    # Strip markdown
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0]
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0]
    
    return json.loads(raw.strip())


# ─── Main classifier ──────────────────────────────────────────────────────────
def classify(message: str, context: str = None) -> dict:
    """Classify a message using the configured backend."""
    if not message or not message.strip():
        raise ValueError("Cannot classify an empty message")

    backend = os.getenv('INTELLIGENCE_BACKEND', 'kimi').lower()

    try:
        if backend == 'kimi':
            print(f"[DEBUG] Using Kimi backend: {os.getenv('KIMI_MODEL')}", file=sys.stderr)
            result = classify_with_kimi(message, context)
        elif backend == 'ollama':
            print(f"[DEBUG] Using Ollama backend: {os.getenv('OLLAMA_MODEL')}", file=sys.stderr)
            result = classify_with_ollama(message, context)
        else:
            raise RuntimeError(f"Unknown INTELLIGENCE_BACKEND: '{backend}'")
    except Exception as e:
        fallback = 'ollama' if backend == 'kimi' else 'kimi'
        print(f"[WARN] {backend} failed: {e}. Falling back to {fallback}", file=sys.stderr)
        try:
            if fallback == 'ollama':
                result = classify_with_ollama(message, context)
            else:
                result = classify_with_kimi(message, context)
        except Exception as fe:
            raise RuntimeError(f"Both failed. Primary: {e} | Fallback: {fe}")

    # Defaults
    if result.get('domain') not in DOMAINS: result['domain'] = 'Clan'
    if result.get('category') not in CATEGORIES: result['category'] = 'Inbox Log'
    result['source_raw'] = message
    result['created_at'] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return result


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain Sorter')
    parser.add_argument('message', nargs='?')
    parser.add_argument('--context', help='Context for classification')
    parser.add_argument('--stdin', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    if args.test:
        # Simple test
        print(json.dumps(classify("BTC to the moon", "Trading charts research..."), indent=2))
        sys.exit(0)

    msg = sys.stdin.read().strip() if args.stdin else args.message
    if not msg:
        print("Error: Provide a message", file=sys.stderr)
        sys.exit(1)

    try:
        output = classify(msg, args.context)
        print(json.dumps(output, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)
