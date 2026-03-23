import os
import json
import requests
import argparse
import sys
import re
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Configuration ---
CLASSIFICATION_PROMPT = """You are the OpenBrain Sorter, an expert information architect. 
Your job is to classify raw incoming thoughts from a Telegram bot into a hierarchical "5 C" framework for a personal Second Brain.

## 🗂 Level 1: The "5 C" Domains (Folders)
1. **~ CAPITAL ~** ($Cap, #Cash, #Charts): Financial data, investments, wealth, business assets.
2. **~ COMPUTERS ~** (#Comp, #Sys, #Tech): Coding, AI, architecture, automation, hardware/software.
3. **~ CARS ~** (#Cars): Vehicle maintenance, automotive logs, logistics, mobility.
4. **~ CANNAPY ~** (#Cann, #plants): Botany, growth logs, research, harvests.
5. **~ CLAN ~** (#Clan, #Fam): Family, social, legacy, household, community.

## 📁 Level 2: The Action Categories (Tables)
1. **People** (#People): Contacts, relationship notes, networking.
2. **Projects** (#Projects): Multi-step endeavors, build logs, active work.
3. **Ideas** (#Ideas): Raw sparks, future concepts, "I have an idea..."
4. **Admin** (#Admin): Tasks, logistics, "Todo", receipts, reminders. (FALLBACK domain).

## 🛠 Intelligence Rules
1. **Hashtag Priority**: Prioritize specific tags ($Cap, #Sys, #People, etc.) over semantic guesses.
2. **Intent Detection**: 
   - `capture`: Simple recording of facts/thoughts.
   - `research`: When the user says "look up", "search", "find out", "research".
   - `execute`: When the user says "do", "complete", "add to list", "remind me".
3. **Ideas vs Tasks**: 
   - If user says "I have an idea..." -> Category: Ideas.
   - If user says "I need <x> done/completed/looked up" -> Category: Admin.
4. **Table-Ready Output**: Generate fields that fit the respective Table View schemas (e.g., status, priority, site).

## Output schema
{
  "domain": "~ CAPITAL ~|~ COMPUTERS ~|~ CARS ~|~ CANNAPY ~|~ CLAN ~",
  "category": "People|Projects|Ideas|Admin",
  "intent": "capture|research|execute",
  "title": "Concise professional title",
  "summary": "1-sentence summary",
  "metadata": {
     "status": "string (for Projects/Admin)",
     "priority": "string (for Ideas/Admin)",
     "notes": "string",
     "folder": "string"
  },
  "tags": ["string"],
  "quality_score": "high|medium|low",
  "created_at": "ISO8601",
  "_reasoning": "1 sentence explanation"
}"""

# --- Hashtag Mapping ---
DOMAIN_TAGS = {
    "$cap": "~ CAPITAL ~", "#cash": "~ CAPITAL ~", "#charts": "~ CAPITAL ~",
    "#comp": "~ COMPUTERS ~", "#sys": "~ COMPUTERS ~", "#tech": "~ COMPUTERS ~",
    "#cars": "~ CARS ~",
    "#cann": "~ CANNAPY ~", "#plants": "~ CANNAPY ~",
    "#clan": "~ CLAN ~", "#fam": "~ CLAN ~"
}

CATEGORY_TAGS = {
    "#people": "People",
    "#projects": "Projects",
    "#ideas": "Ideas",
    "#admin": "Admin"
}

def classify(message, context=None):
    """
    Classifies a message into Domain + Category hierarchy with hard-coded hashtag overrides.
    """
    # 1. Hard-coded Overrides
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

    # 2. Call NVIDIA NIM API
    api_key = os.getenv('KIMI_API_KEY')
    base_url = "https://integrate.api.nvidia.com/v1"
    model = "moonshotai/kimi-k2.5"

    if not api_key:
        return {
            "domain": domain_override or "Clan",
            "category": category_override or "Admin",
            "intent": "capture",
            "title": "Raw Message (No AI Key)",
            "summary": message[:100],
            "source_raw": message,
            "created_at": datetime.now().isoformat(),
            "_reasoning": "KIMI_API_KEY missing - using fallback path."
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
        message_obj = resp.json()['choices'][0]['message']
        raw = message_obj.get('content') or message_obj.get('reasoning') or message_obj.get('reasoning_content') or ""
        raw = raw.strip()
    except Exception as e:
        return {
            "domain": domain_override or "Clan",
            "category": category_override or "Admin",
            "intent": "capture",
            "title": "API Error",
            "summary": message[:100],
            "source_raw": message,
            "created_at": datetime.now().isoformat(),
            "_error": str(e)
        }

    # Clean JSON
    if "```" in raw:
        raw = re.split(r'```(?:json)?', raw)[1].split("```")[0]
    
    try:
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
            
        data = json.loads(raw)
        
        # Apply Overrides
        if domain_override: data['domain'] = domain_override
        if category_override: data['category'] = category_override
        
        # Defaults
        if not data.get('domain'): data['domain'] = "Clan"
        if not data.get('category'): data['category'] = "Admin"
        
        data['source_raw'] = message
        data['created_at'] = datetime.now().isoformat()
            
        return data
    except Exception as e:
        return {
            "domain": domain_override or "Clan",
            "category": category_override or "Admin",
            "intent": "capture",
            "title": "Parse Error",
            "summary": "AI output was not valid JSON.",
            "source_raw": message,
            "created_at": datetime.now().isoformat(),
            "_reasoning": f"Failed to parse JSON: {str(e)}",
            "_raw": raw
        }

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain Sorter')
    parser.add_argument('message', nargs='?')
    parser.add_argument('--context', help='Context for classification')
    parser.add_argument('--stdin', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()

    if args.test:
        print(json.dumps(classify("#Cash BTC to the moon", "Trading charts research..."), indent=2))
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
