#!/usr/bin/env python3
import json
import subprocess
import os
import sys

OPENCLAW_CONFIG = "/Users/tonyg/Documents/GzOpenBrain/open-claw/openclaw.json"
CONTAINER_NAME = "openbrain_openclaw"

def get_current_version():
    try:
        with open(OPENCLAW_CONFIG, 'r') as f:
            data = json.load(f)
            return data.get("meta", {}).get("lastTouchedVersion", "unknown")
    except Exception as e:
        return f"Error reading config: {e}"

def get_latest_version():
    try:
        result = subprocess.run(["npm", "show", "openclaw", "version"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except Exception:
        return "unknown"

def get_container_status():
    try:
        result = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}}", CONTAINER_NAME], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return "missing"
    except Exception:
        return "error"

def main():
    current = get_current_version()
    latest = get_latest_version()
    status = get_container_status()
    
    update_available = current != latest and latest != "unknown"
    
    report = {
        "current_version": current,
        "latest_version": latest,
        "update_available": update_available,
        "container_status": status,
        "healthy": status == "running"
    }
    
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
