import os
import json
import requests
import argparse
import sys
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

# ---------------------------------------------------------------------------
# Sorter prompt — 5C domains + action categories
# ---------------------------------------------------------------------------
CLASSIFICATION_PROMPT = """You are the OpenBrain Sorter, an expert information architect.
Your job is to classify raw incoming thoughts from a Telegram bot into a hierarchical "5C" framework for a personal Second Brain.

## Level 1: The 5C Domains
1. CAPITAL ($Cap, #Cash, #Charts): Financial data, investments, wealth, business assets.
2. COMPUTERS (#Comp, #Sys, #Tech): Coding, AI, architecture, automation, hardware/software.
3. CARS (#Cars): Vehicle maintenance, automotive logs, logistics, mobility.
4. CANNAPY (#Cann, #Plants): Botany, growth logs, research, harvests.
5. CLAN (#Clan, #Fam): Family, social, legacy, household, community.

## Level 2: Action Categories
1. People (#People): Contacts, relationship notes, networking.
2. Projects (#Projects): Multi-step endeavors, build logs, active work.
3. Ideas (#Ideas): Raw sparks, future concepts, "I have an idea..."
4. Admin (#Admin): Tasks, logistics, todos, receipts, reminders. (FALLBACK category)

## Intelligence Rules
1. Hashtag Priority: Prioritize specific tags ($Cap, #Sys, #People, etc.) over semantic guesses.
2. Intent Detection:
   - capture: Simple recording of facts/thoughts.
   - research: When the user says "look up", "search", "find out", "research".
   - execute: When the user says "do", "complete", "add to list", "remind me".
3. Ideas vs Tasks:
   - "I have an idea..." -> Category: Ideas
   - "I need <x> done/completed/looked up" -> Category: Admin
4. Generate fields that fit the respective Table View schemas.

## Output — return ONLY valid JSON, no markdown fences:
{
  "domain": "CAPITAL|COMPUTERS|CARS|CANNAPY|CLAN",
  "category": "People|Projects|Ideas|Admin",
  "intent": "capture|research|execute",
  "title": "Concise professional title (max 8 words)",
  "summary": "1-2 sentence richer summary",
  "metadata": {
    "status": "string (for Projects/Admin)",
    "priority": "string (for Ideas/Admin)",
    "notes": "string"
  },
  "tags": ["string"],
  "quality_score": "high|medium|low",
  "created_at": "ISO8601",
  "_reasoning": "1 sentence explanation"
}"""

# ---------------------------------------------------------------------------
# Hashtag overrides — deterministic routing before LLM
# ---------------------------------------------------------------------------
DOMAIN_TAGS = {
    "$cap": "CAPITAL", "#cash": "CAPITAL", "#charts": "CAPITAL",
    "#comp": "COMPUTERS", "#sys": "COMPUTERS", "#tech": "COMPUTERS",
    "#cars": "CARS",
    "#cann": "CANNAPY", "#plants": "CANNAPY",
    "#clan": "CLAN", "#fam": "CLAN"
}

CATEGORY_TAGS = {
    "#people": "People",
    "#projects": "Projects",
    "#ideas": "Ideas",
    "#admin": "Admin"
}

# Normalize whatever the LLM returns to our canonical domain names
DOMAIN_NORMALIZE = {
    "~ capital ~": "CAPITAL", "capital": "CAPITAL",
    "~ computers ~": "COMPUTERS", "computers": "COMPUTERS",
    "~ cars ~": "CARS", "cars": "CARS",
    "~ cannapy ~": "CANNAPY", "cannapy": "CANNAPY",
    "~ clan ~": "CLAN", "clan": "CLAN",
}


def _normalize_domain(raw: str) -> str:
    if not raw:
        return "CLAN"
    key = raw.strip().lower().replace("~", "").strip()
    return DOMAIN_NORMALIZE.get(key, raw.upper())


def classify(message, context=None):
    """Classify a message into 5C domain + category. Returns structured dict."""
    # 1. Hashtag overrides (deterministic)
    domain_override = None
    category_override = None
    msg_lower = message.lower()
    for tag, domain in DOMAIN_TAGS.items():
        if tag in msg_lower:
            domain_override = domain
            break
    for tag, cat in CATEGORY_TAGS.items():
        if tag in msg_lower:
            category_override = cat
            break

    # 2. LLM classification
    api_key = os.getenv("NVIDIA_API_KEY")
    base_url = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
    model = os.getenv("NVIDIA_MODEL", "meta/llama-3.3-70b-instruct")

    if not api_key:
        return {
            "domain": domain_override or "CLAN",
            "category": category_override or "Admin",
            "intent": "capture",
            "title": "Raw Message (No API Key)",
            "summary": message[:100],
            "source_raw": message,
            "quality_score": "low",
            "tags": [],
            "metadata": {},
            "created_at": datetime.now().isoformat(),
            "_reasoning": "NVIDIA_API_KEY missing — using fallback."
        }

    user_content = f"Message to classify:\n\n{message}"
    if context:
        user_content = f"CONTEXT:\n{context}\n\n---\n\n{user_content}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.1
    }

    try:
        resp = requests.post(
            f"{base_url}/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=120
        )
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"].get("content", "").strip()
    except Exception as e:
        return {
            "domain": domain_override or "CLAN",
            "category": category_override or "Admin",
            "intent": "capture",
            "title": "API Error",
            "summary": message[:100],
            "source_raw": message,
            "quality_score": "low",
            "tags": [],
            "metadata": {},
            "created_at": datetime.now().isoformat(),
            "_error": str(e)
        }

    # Strip markdown fences if present
    if "```" in raw:
        parts = re.split(r"```(?:json)?", raw)
        raw = parts[1].split("```")[0] if len(parts) > 1 else raw

    try:
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
        data = json.loads(raw)

        # Apply overrides
        if domain_override:
            data["domain"] = domain_override
        if category_override:
            data["category"] = category_override

        # Normalize and default
        data["domain"] = _normalize_domain(data.get("domain"))
        if not data.get("category"):
            data["category"] = "Admin"
        if not data.get("tags"):
            data["tags"] = []
        if not data.get("metadata"):
            data["metadata"] = {}

        data["source_raw"] = message
        data["created_at"] = datetime.now().isoformat()
        return data

    except Exception as e:
        return {
            "domain": domain_override or "CLAN",
            "category": category_override or "Admin",
            "intent": "capture",
            "title": "Parse Error",
            "summary": "AI output was not valid JSON.",
            "source_raw": message,
            "quality_score": "low",
            "tags": [],
            "metadata": {},
            "created_at": datetime.now().isoformat(),
            "_reasoning": f"JSON parse failed: {e}",
            "_raw": raw
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenBrain Sorter")
    parser.add_argument("message", nargs="?")
    parser.add_argument("--context", help="Context for classification")
    parser.add_argument("--stdin", action="store_true")
    parser.add_argument("--test", action="store_true")
    args = parser.parse_args()

    if args.test:
        print(json.dumps(classify("#Cash BTC broke 100k — thinking about rebalancing"), indent=2))
        print(json.dumps(classify("I have an idea for the NemoClaw VP routing"), indent=2))
        sys.exit(0)

    msg = sys.stdin.read().strip() if args.stdin else args.message
    if not msg:
        print("Error: provide a message", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(classify(msg, args.context), indent=2, ensure_ascii=False))
