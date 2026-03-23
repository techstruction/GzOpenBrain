import os
import subprocess
import time
import sys

def run_ssh(cmd):
    full_cmd = f"ssh macbridge \"/home/tonyg/.local/bin/openshell doctor exec -- kubectl exec -n openshell nemoclaw -- /bin/bash -c \\\"{cmd}\\\"\""
    print(f"Executing: {cmd}")
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result

def main():
    # 1. Update Node.js to 22
    print("Step 1: Upgrading to Node.js 22...")
    run_ssh("curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && apt-get install -y nodejs")
    
    # 2. Install Net-tools and Socat
    print("Step 2: Installing networking tools...")
    run_ssh("apt-get update && apt-get install -y net-tools socat")
    
    # 3. Fix Binary Links
    print("Step 3: Fixing binary paths...")
    run_ssh("rm -f /usr/bin/openclaw /bin/openclaw && ln -s /opt/NemoClaw/node_modules/.bin/openclaw /bin/openclaw")
    
    # 4. Clean up stale processes
    print("Step 4: Purging old processes...")
    run_ssh("pkill -9 -f openclaw || true; pkill -9 -f socat || true")
    
    # 5. Launch Gateway (Internal 18788)
    print("Step 5: Launching Gateway on 18788...")
    env_vars = (
        "export NVIDIA_API_KEY='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' && "
        "export CHAT_UI_URL='https://nemoclaw-macbridge.techstruction.co' && "
        "export PUBLIC_PORT=18788"
    )
    # We use a trick to keep the background processes alive
    run_ssh(f"{env_vars} && cd /opt/NemoClaw && (nohup openclaw gateway run --port 18788 > /tmp/gateway_final.log 2>&1 &)")
    
    time.sleep(5)
    
    # 6. Launch Bridge (0.0.0.0:18789)
    print("Step 6: Launching Network Bridge on 18789...")
    run_ssh("(nohup socat TCP-LISTEN:18789,fork,reuseaddr TCP:127.0.0.1:18788 > /tmp/socat_final.log 2>&1 &)")
    
    print("Step 7: Verifying listeners...")
    res = run_ssh("netstat -tunlp | grep -E '18788|18789'")
    print(res.stdout)
    
    print("\n--- RESTORATION COMPLETE ---")
    print("Use URL: https://nemoclaw-macbridge.techstruction.co/#token=10eb44562cd34bfa2a1dd9e1d1d3de133f17cce64c8768ee")

if __name__ == "__main__":
    main()
