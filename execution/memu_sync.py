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
    Sends the classified entry to the memU MCP server for storage.
    """
    try:
        import requests
        entry = json.loads(entry_json)
        
        # Use the container name if running in docker, or localhost if testing
        host = os.getenv('MEMU_HOST', 'openbrain_memu')
        port = os.getenv('MEMU_PORT', '8001')
        url = f"http://{host}:{port}/store"
        
        response = requests.post(url, json=entry, timeout=10)
        response.raise_for_status()
        
        return True, "Synced to memU memory"
    except Exception as e:
        # Fallback to local file append if container is unreachable and we are NOT in docker
        if not os.getenv('DOCKER_CONTAINER'):
             try:
                memory_file = os.path.join(os.path.dirname(__file__), '..', 'open-claw', 'MEMORY.md')
                memory_line = f"\n### [{entry.get('domain')}] {entry.get('title')}\n{entry.get('summary')}\nTags: {', '.join(entry.get('tags', []))}\n"
                with open(memory_file, 'a') as f:
                    f.write(memory_line)
                return True, "Synced to local memory file (fallback)"
             except:
                pass
        return False, str(e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        success, msg = sync_to_openclaw(sys.argv[1])
        print(json.dumps({"success": success, "message": msg}))
    else:
        print(json.dumps({"success": False, "message": "No entry provided"}))
