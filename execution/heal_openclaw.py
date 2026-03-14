#!/usr/bin/env python3
import subprocess
import json
import os
import sys

CONTAINER_NAME = "openbrain_openclaw"
DOCKER_COMPOSE_FILE = "/Users/tonyg/Documents/GzOpenBrain/docker-compose.yml"

def get_logs(limit=50):
    res = subprocess.run(["docker", "logs", "--tail", str(limit), CONTAINER_NAME], capture_output=True, text=True)
    return res.stdout + res.stderr

def check_container_exists():
    res = subprocess.run(["docker", "ps", "-a", "--filter", f"name={CONTAINER_NAME}", "--format", "{{.Names}}"], capture_output=True, text=True)
    return CONTAINER_NAME in res.stdout

def attempt_restart():
    print("Attempting to restart container...")
    res = subprocess.run(["docker-compose", "restart", "open-claw"], capture_output=True, text=True)
    return res.returncode == 0

def diagnose():
    """
    Troubleshooting Methodology:
    1. Check if container exists.
    2. Check container status (running/paused/exited).
    3. Check logs for fatal errors (port conflicts, missing files, config errors).
    4. Check for port binding issues.
    """
    print("Starting Deep Troubleshooting Methodology...")
    
    exists = check_container_exists()
    if not exists:
        return {"issue": "Container does not exist", "recommendation": "Run apply_openclaw_update.py to rebuild."}

    # Get status and health
    res = subprocess.run(["docker", "inspect", CONTAINER_NAME], capture_output=True, text=True)
    inspect_data = json.loads(res.stdout)[0]
    status = inspect_data.get("State", {}).get("Status")
    exit_code = inspect_data.get("State", {}).get("ExitCode")
    
    logs = get_logs()
    
    diag_report = {
        "status": status,
        "exit_code": exit_code,
        "recent_logs": logs[-1000:], # Last 1000 chars
        "port_bindings": inspect_data.get("HostConfig", {}).get("PortBindings")
    }

    if status == "running":
        return {"issue": "Service reports running but may be unresponsive", "data": diag_report}
    
    if "address already in use" in logs.lower():
        return {"issue": "Port conflict detected", "recommendation": "Check for other processes on port 18789", "data": diag_report}
    
    if "no such file or directory" in logs.lower():
        return {"issue": "Missing file in volume mount", "recommendation": "Verify open-claw/ directory contents", "data": diag_report}

    return {"issue": "Unknown failure", "data": diag_report}

def main():
    print("Initiating OpenClaw Self-Heal Protocol...")
    
    # Tier 1: Basic Restart
    if attempt_restart():
        # Check if it stayed up
        import time
        time.sleep(2)
        res = subprocess.run(["docker", "inspect", "-f", "{{.State.Status}}", CONTAINER_NAME], capture_output=True, text=True)
        if res.stdout.strip() == "running":
            print("Successfully healed via restart.")
            sys.exit(0)
    
    # Tier 2: Deep Diagnosis
    report = diagnose()
    print("\nTroubleshooting Report:")
    print(json.dumps(report, indent=2))
    
    print("\nACTION REQUIRED: Basic healing failed. Use the report above to perform agentic reasoning fix.")
    sys.exit(1)

if __name__ == "__main__":
    main()
