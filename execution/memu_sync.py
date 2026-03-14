#!/usr/bin/env python3
"""
memu_sync.py — OpenBrain Memory Synchronizer
Syncs classified entries and knowledge from OpenBrain to specialist agents.
"""

import os
import sys
import json
import subprocess
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

def sync_to_openclaw(entry_json: str):
    """
    Appends the classified entry to OpenClaw's internal MEMORY.md for context.
    """
    try:
        entry = json.loads(entry_json)
        memory_line = f"\n### [{entry.get('domain')}] {entry.get('title')}\n{entry.get('summary')}\nTags: {', '.join(entry.get('tags', []))}\n"
        
        # We use docker exec to append to a file inside the container
        # Note: In production, we'd use a shared volume or a Proper API.
        cmd = [
            "docker", "exec", "openbrain_openclaw",
            "sh", "-c", f"echo {json.dumps(memory_line)} >> /root/.openclaw/MEMORY.md"
        ]
        
        subprocess.run(cmd, check=True)
        return True, "Synced to OpenClaw memory"
    except Exception as e:
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        success, msg = sync_to_openclaw(sys.argv[1])
        print(json.dumps({"success": success, "message": msg}))
    else:
        print(json.dumps({"success": False, "message": "No entry provided"}))
