#!/usr/bin/env python3
import subprocess
import json
import os
import datetime

OPENCLAW_DIR = "/Users/tonyg/Documents/GzOpenBrain/open-claw"
OPENCLAW_CONFIG = f"{OPENCLAW_DIR}/openclaw.json"
DOCKER_COMPOSE_FILE = "/Users/tonyg/Documents/GzOpenBrain/docker-compose.yml"

def run_command(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return True

def update_config_metadata(new_version):
    try:
        with open(OPENCLAW_CONFIG, 'r') as f:
            data = json.load(f)
        
        data["meta"]["lastTouchedVersion"] = new_version
        data["meta"]["lastTouchedAt"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        with open(OPENCLAW_CONFIG, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to update config: {e}")
        return False

def main():
    # 1. Get latest version to update config later
    print("Fetching latest version...")
    res = subprocess.run(["npm", "show", "openclaw", "version"], capture_output=True, text=True)
    latest_version = res.stdout.strip() if res.returncode == 0 else "unknown"

    # 2. Rebuild container
    print("Rebuilding OpenClaw container...")
    if not run_command(["docker-compose", "build", "--no-cache", "open-claw"]):
        print("Build failed.")
        return

    # 3. Restart service
    print("Restarting OpenClaw service...")
    if not run_command(["docker-compose", "up", "-d", "open-claw"]):
        print("Restart failed.")
        return

    # 4. Update metadata
    if latest_version != "unknown":
        print(f"Updating configuration metadata to {latest_version}...")
        update_config_metadata(latest_version)

    print("Update complete.")

if __name__ == "__main__":
    main()
