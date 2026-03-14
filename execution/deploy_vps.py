#!/usr/bin/env python3
"""
deploy_vps.py — OpenBrain VPS Deployment Script

Automates the process of syncing the local codebase to the macbridge VPS
and restarting the Docker container.

Usage:
    python3 execution/deploy_vps.py
"""

import subprocess
import os
import sys

# Configuration
VPS_HOST = "macbridge"
REMOTE_DIR = "~/GzOpenBrain"
EXCLUDES = [
    ".git",
    "venv",
    "__pycache__",
    ".DS_Store",
    ".tmp",
    "*.pyc",
    "*.ipynb",
    ".gemini",
    "open-claw/logs",
    "open-claw/agents/*/logs",
    "open-claw/MEMORY.md",
    "open-claw/identity",
    "open-claw/devices",
    "open-claw/workspace",
    "open-claw/telegram",
    "open-claw/memory",
    "open-claw/cron",
    "open-claw/canvas",
    "open-claw/agents/*/agent",
    "open-claw/agents/*/sessions",
    "open-claw/agents/*/logs"
]

def run(cmd):
    """Run a local shell command."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True)
    if result.returncode != 0:
        print(f"Error: Command failed with return code {result.returncode}")
        sys.exit(1)

def deploy():
    # 1. Ensure remote directory exists
    print(f"--- Preparing remote directory on {VPS_HOST} ---")
    run(f"ssh {VPS_HOST} 'mkdir -p {REMOTE_DIR}'")

    # 2. Sync files using rsync
    print(f"--- Syncing files to {VPS_HOST} ---")
    exclude_args = " ".join([f"--exclude='{e}'" for e in EXCLUDES])
    # Use absolute path for local dir to be safe
    local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Note: trailing slash on local_dir ensures we sync contents into REMOTE_DIR
    run(f"rsync -avz --delete {exclude_args} {local_dir}/ {VPS_HOST}:{REMOTE_DIR}")

    # 3. Build and restart container
    print(f"--- Restarting Docker containers on {VPS_HOST} ---")
    run(f"ssh {VPS_HOST} 'cd {REMOTE_DIR} && docker compose up -d --build'")

    print("\n--- Deployment Complete! ---")
    print(f"Checking status on {VPS_HOST}...")
    run(f"ssh {VPS_HOST} 'cd {REMOTE_DIR} && docker compose ps'")

if __name__ == "__main__":
    deploy()
