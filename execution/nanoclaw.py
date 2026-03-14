#!/usr/bin/env python3
"""
nanoclaw.py — OpenBrain Transient Specialist
Runs a command or script in an ephemeral Docker container for security and isolation.
"""

import os
import sys
import json
import subprocess
import argparse
from typing import Dict, Any

def run_transient_task(task: str, image: str = "python:3.11-slim") -> Dict[str, Any]:
    """
    Spins up a temporary container, runs the task, and returns the output.
    """
    try:
        # Construct docker run command
        # --rm: remove container after exit
        # -i: interactive
        cmd = [
            "docker", "run", "--rm",
            image,
            "python3", "-c", task
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "Task timed out"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NanoClaw — transient task runner')
    parser.add_argument('task_code', help='Python code to execute')
    parser.add_argument('--image', default="python:3.11-slim", help='Docker image to use')
    args = parser.parse_args()
    
    output = run_transient_task(args.task_code, args.image)
    print(json.dumps(output, indent=2))
