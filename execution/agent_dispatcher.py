#!/usr/bin/env python3
"""
agent_dispatcher.py — OpenBrain Agent Dispatcher

Routes incoming tasks to the appropriate specialist agent (OpenClaw, NanoClaw, memU).
"""

import os
import json
import logging
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger('dispatcher')

# Specialist Agent Endpoints
OPENCLAW_URL = os.getenv('OPENCLAW_URL', 'http://open-claw:18789')
NANOCLAW_URL = os.getenv('NANOCLAW_URL', 'http://localhost:18790') # Planned

import subprocess

def dispatch(task_description: str, metadata: dict = None) -> dict:
    """Determine the best agent and route the task."""
    log.info(f"Dispatching task: {task_description[:50]}...")
    
    # Logic for routing: default to OpenClaw for now
    try:
        # Construct the docker exec command
        cmd = [
            "docker", "exec", "openbrain_openclaw",
            "openclaw", "agent",
            "--session-id", "system-dispatch",
            "--message", task_description,
            "--json"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        # Parse the JSON response from OpenClaw
        # Look for the last line or the whole thing if it's clean JSON
        output = result.stdout.strip()
        # Find the start of JSON (OpenClaw might print other things)
        start_idx = output.find('{')
        if start_idx != -1:
            clean_json = output[start_idx:]
            response_data = json.loads(clean_json)
            
            # Extract the actual text response
            # Based on the structure observed earlier
            # response_data['agent']['response']['text'] or similar
            # For now, return the whole thing
            return {
                "status": "success",
                "agent": "OpenClaw",
                "data": response_data
            }
        else:
            return {"status": "error", "message": f"Invalid JSON output: {output}"}
            
    except subprocess.CalledProcessError as e:
        log.error(f"Dispatch failed (CLI error): {e.stderr}")
        return {"status": "error", "message": f"CLI error: {e.stderr}"}
    except Exception as e:
        log.error(f"Dispatch failed: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(json.dumps(dispatch(query)))
