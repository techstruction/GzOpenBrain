# 🏗️ Multi-Agent Workflow Cheat Sheet

## Phase 1: Building a New System

To trigger the **Project Architect**, just use natural language in the chat:

- *"Start a new project"*
- *"Architect a [domain] swarm"*
- *"Build me a specialized team for [objective]"*

## Phase 2: Running a Project

Once a project is scaffolded, change your directory to the project folder and run:

- `@ORCHESTRATOR.md instantiate`
- Or: `@AGENTS.md instantiate`

## Phase 3: The 3-Layer Logic

1. **Directives** (`directives/`): The SOPs. If an agent is acting dumb, edit their .md file.
2. **Orchestration** (`ORCHESTRATOR.md`): The strategy. If the flow is wrong, edit this.
3. **Execution** (`execution/`): The scripts. If the data is wrong, fix the Python.

## Pro Tip: Self-Annealing

When a script breaks, tell the agent: *"Fix the script, test it, and update your directive."* This makes the system permanently stronger.

---

### File Reference

- **Global Skill Directory**: `/Users/tonyg/.gemini/antigravity/skills/project-architect-skill/`
- **Domain Mappings**: `references/domain_roster.md` (inside the skill folder)
- **Coordination Protocols**: `references/protocols.md` (inside the skill folder)
