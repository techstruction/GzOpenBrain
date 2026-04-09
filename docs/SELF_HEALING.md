# Self-Healing Ledger

This document tracks technical issues, configuration errors, and their resolutions within the Open-Claw system. Use this as a reference when encountering similar errors.

## 1. Skill Recognition Issues
- **Issue**: Newly created skills are not recognized as available tools.
- **Cause**: OpenClaw looks for skills in its configured root. If skills are added via a workspace, they may be ignored if they resolve outside the root or if the bot expects a specific subdirectory (e.g., `workspace/skills`).
- **Solution**: 
    1. Ensure skill directories contain a valid `SKILL.md`.
    2. Place copies (avoid symlinks to bypass "outside root" security warnings) in the expected path (e.g., `/root/.openclaw/workspace/skills/`).
    3. Run `openclaw skills list` to verify discovery.

## 2. Permission Denied for Elevated Tools
- **Issue**: Using the `exec` tool or running system scripts results in "elevated is not available" or permission errors.
- **Cause**: The `tools.elevated` section in `openclaw.json` is disabled or missing for the channel.
- **Solution**: 
    - Enable `elevated` tools in `openclaw.json`:
      ```json
      "tools": {
        "elevated": {
          "enabled": true,
          "allowFrom": { "telegram": ["*"] }
        }
      }
      ```

## 3. Missing Python Dependencies
- **Issue**: Skill scripts fail with `ModuleNotFoundError` (e.g., `No module named "requests"`).
- **Cause**: The bot container lacks common Python libraries.
- **Solution**: 
    - Install missing packages inside the container: `apt-get update && apt-get install -y python3-requests`.
    - Update `skill-creator` to check for dependencies during deployment.

## 4. Brave Search API Key Not Found
- **Issue**: Bot reports "Brave Search API key is not configured" even when present in the environment.
- **Cause**: OpenClaw expects the key in `tools.web.search.apiKey` and requires the provider to be explicitly set.
- **Solution**: 
    1. Set the provider: `openclaw config set tools.web.search.provider brave`.
    2. Ensure the key is in `openclaw.json` under `tools.web.search.apiKey`.
    3. Create a redundant `/root/.openclaw/.env` file in the state directory.

## 5. Tool Prioritization Failures
- **Issue**: Bot uses general web search for tasks that have dedicated skills.
- **Cause**: Default LLM behavior prefers familiar tools like `web_search`.
- **Solution**: 
    - Use "pushy" descriptions in `SKILL.md` (e.g., "ALWAYS use this for X").
    - Mandate tool priority in `AGENTS.md` under a "Tool Prioritization" section.

---
