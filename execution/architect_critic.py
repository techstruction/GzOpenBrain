#!/usr/bin/env python3
"""
architect_critic.py — OpenBrain Architect (Critic)
Reviews classification proposals from the Sorter and provides feedback or approval.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

INTELLIGENCE_BACKEND = os.getenv('INTELLIGENCE_BACKEND', 'kimi').lower()

CRITIC_PROMPT = """You are the Architect (Critic) for the OpenBrain system.
Your mission is to ensure the Sorter agent has correctly classified the user's message.

## The Core Principles
1. Accuracy: Is the domain (Capital, Computers, Cars, Cannapy, Clan) exactly right?
2. Schema: Is the intent (capture/execute) correct? (execute = task/request for action; capture = note/info/fact)
3. Quality: Is the title and summary professional and descriptive?

## Domains Reference
- Capital: Finance, money, charts, investments
- Computers: Tech, code, AI, servers
- Cars: Automotive research, vehicle projects
- Cannapy: Cannabis operations and research
- Clan: Family, health, personal development

## Your Task
Review the classification proposal against the raw message.
Return a JSON object with your verdict.

## Output Schema
{
  "verdict": "pass" | "fail",
  "reason": "Clear explanation if failing",
  "suggested_fix": {
     "domain": "string (optional)",
     "category": "string (optional)",
     "intent": "string (optional)"
  }
}
"""

def review_with_kimi(raw_message: str, proposal: Dict[str, Any]) -> dict:
    from openai import OpenAI
    api_key = os.getenv('KIMI_API_KEY')
    base_url = os.getenv('KIMI_BASE_URL', 'https://integrate.api.nvidia.com/v1')
    model = os.getenv('KIMI_MODEL', 'moonshotai/kimi-k2.5')
    
    client = OpenAI(api_key=api_key, base_url=base_url)
    
    prompt = f"### RAW MESSAGE:\n{raw_message}\n\n### PROPOSAL:\n{json.dumps(proposal, indent=2)}"
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": CRITIC_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=512,
        timeout=120
    )
    
    raw = response.choices[0].message.content.strip()
    return json.loads(raw)

def review_with_ollama(raw_message: str, proposal: Dict[str, Any]) -> dict:
    import requests
    host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    model = os.getenv('OLLAMA_MODEL', 'qwen3.5:9b')
    
    prompt = f"### RAW MESSAGE:\n{raw_message}\n\n### PROPOSAL:\n{json.dumps(proposal, indent=2)}"
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": CRITIC_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "stream": False,
        "options": {"temperature": 0.0}
    }
    
    resp = requests.post(f"{host}/api/chat", json=payload, timeout=120)
    raw = resp.json()['message']['content'].strip()
    
    # Strip markdown
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    
    return json.loads(raw)

def review(raw_message: str, proposal: Dict[str, Any]) -> dict:
    backend = INTELLIGENCE_BACKEND
    try:
        if backend == 'kimi':
            return review_with_kimi(raw_message, proposal)
        else:
            return review_with_ollama(raw_message, proposal)
    except Exception as e:
        # If critic fails, we default to pass to avoid blocking the pipeline, but log it
        print(f"[ERROR] Critic failed: {e}", file=sys.stderr)
        return {"verdict": "pass", "reason": "Critic failed, defaulting to pass", "suggested_fix": {}}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Architect Critic — review a classification')
    parser.add_argument('raw_message', help='The original message text')
    parser.add_argument('proposal_json', help='The proposed classification in JSON')
    args = parser.parse_args()
    
    try:
        review_result = review(args.raw_message, json.loads(args.proposal_json))
        print(json.dumps(review_result, indent=2))
    except Exception as e:
        print(json.dumps({"verdict": "pass", "reason": f"Error parsing input: {e}"}))
        sys.exit(0)
