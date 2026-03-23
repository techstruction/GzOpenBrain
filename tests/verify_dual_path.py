import os
import json
import subprocess
import time

def test_dual_path():
    print("--- Starting Dual-Path Storage Verification ---")
    
    test_entry = {
        "domain": "Computers",
        "category": "Ideas",
        "title": "MCP Integration Test",
        "summary": "This is a test entry to verify dual-path storage to Affine and memU.",
        "source_raw": "Self-test",
        "tags": ["test", "mcp", "dual_path"],
        "created_at": "2026-03-15T16:20:00Z"
    }
    
    entry_json = json.dumps(test_entry)
    
    # 1. Test Affine Path
    print("\n[Testing Path A: Affine]")
    try:
        cmd = ["python3", "execution/write_to_affine.py", entry_json]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Stdout: {res.stdout.strip()}")
        print(f"Stderr: {res.stderr.strip()}")
    except Exception as e:
        print(f"Error: {e}")

    # 2. Test memU Path
    print("\n[Testing Path B: memU]")
    try:
        cmd = ["python3", "execution/memu_sync.py", entry_json]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Stdout: {res.stdout.strip()}")
        print(f"Stderr: {res.stderr.strip()}")
    except Exception as e:
        print(f"Error: {e}")

    print("\n--- Verification Complete ---")

if __name__ == "__main__":
    test_dual_path()
