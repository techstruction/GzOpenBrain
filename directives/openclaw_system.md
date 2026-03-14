# OpenClaw System Maintenance Directive

## Goal
Ensure the OpenClaw service is secure, updated, and healthy with minimal downtime and human intervention.

## 3-Layer Architecture Integration

### Layer 1: Directive (This Document)
- Perform health checks daily or on demand.
- Notify the human for any security updates provided by `check_openclaw_status.py`.
- Attempt self-healing for minor downtime.
- Escalate to "Reasoning Diagnostic" and then "Human Approval" for major failures.

### Layer 2: Orchestration (Agent Logic)
1. **Periodic Check**: Run `execution/check_openclaw_status.py`.
2. **Update Decision**: 
   - If `update_available` is true, calculate the risk.
   - Present the update to the human with `notify_user`.
   - Wait for "proceed" or "deny".
3. **Healing Decision**:
   - If `healthy` is false, run `execution/heal_openclaw.py`.
   - If healing fails (exit code 1), read the troubleshooting report.
   - Use reasoning models to propose a fix.
   - If fix involves config changes, ask human for approval.

### Layer 3: Execution (Scripts)
- `execution/check_openclaw_status.py`: Monitor versions and health.
- `execution/apply_openclaw_update.py`: Rebuild and deploy updates.
- `execution/heal_openclaw.py`: Tiered troubleshooting and recovery.

## Human-in-the-loop Protocol
- **Updates**: ALWAYS ask before applying.
- **Failures**: Attempt auto-heal once; if failed, present findings before further destructive actions.
