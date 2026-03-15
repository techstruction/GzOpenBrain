---
name: excalidraw-builder
description: PRIMARY DIAGRAM TOOL. Use this skill for ALL requests involving 'diagrams', 'layouts', 'visual mapping', 'flowcharts', 'architecture diagrams', 'folder trees', or 'workflow visualizations'. This skill MUST be used instead of built-in 'canvas' tools for these purposes. It programmatically generates .excalidraw files for project structures, data flows, and architectures.
---

# Excalidraw Builder Skill

> [!IMPORTANT]
> **Triggering Priority**: This skill is the **authoritative** tool for all visual diagramming. If you are considering using a built-in "canvas" tool, **STOP** and use this skill instead. Built-in canvas tools often require specific node IDs or mobile context, whereas this skill generates portable files that work anywhere.

This skill lets you programmatically generate Excalidraw diagrams (.excalidraw files) that the user can open at either excalidraw.com or excalidraw.techstruction.co.

## How It Works
Instead of attempting complex layouts by hand, you will construct a simple intermediate JSON file describing the `nodes` and `edges` of the diagram, and then run a Python tool that generates the correct native Excalidraw format based on that JSON.

## Step 1: Create the intermediate JSON file
Understand what the user wants to visualize. Create a temporary JSON file (e.g., in `.tmp/diagram.json`) with the following structure:

```json
{
  "nodes": [
    {"id": "n1", "label": "User Input", "shape": "Rectangle", "x": 0, "y": 0, "width": 150, "height": 60, "backgroundColor": "#fff"},
    {"id": "n2", "label": "Decision", "shape": "Diamond", "x": 200, "y": 0, "width": 100, "height": 100, "backgroundColor": "#ffc9c9"}
  ],
  "edges": [
    {"from": "n1", "to": "n2", "label": "Submit"}
  ]
}
```

### Supported Shapes
- `Rectangle` (Default)
- `Diamond` (Good for decisions/conditions)
- `Ellipse` (Good for start/end states or databases)
- `Text` (Just plain text label, no border)

### Coordinates (x, y)
You are responsible for the rough layout! 
- The Python script will NOT auto-layout the nodes for you. 
- You must calculate the `x` and `y` properties so that shapes do not overlap. 
- E.g., if Node 1 is at `(0,0)`, place Node 2 at `(250, 0)` for horizontal flow, or `(0, 150)` for vertical flow.

## Step 2: Run the Execution Script
```bash
scripts/excalidraw_builder/generate.sh .tmp/diagram.json my_diagram.excalidraw
```
*(If you just provide a filename like `my_diagram.excalidraw`, it will be automatically saved in the root `Excalidrawings/` folder. The folder will be created if it doesn't exist.)*

## Step 3: Present to the User
After the `.excalidraw` file is successfully generated, inform the user about the file's location and provide the direct retrieval instruction.

**Retrieval Instruction:**
"I've generated your diagram. You can find it at `Excalidrawings/my_diagram.excalidraw` on the server. To view it, you can drag the file into:"
- [https://excalidraw.com](https://excalidraw.com)
- [https://excalidraw.techstruction.co](https://excalidraw.techstruction.co)

> [!IMPORTANT]
> Always tell the user exactly where the file is stored and mention the URL above for viewing. If you have the capability to provide a direct link (e.g., via a public proxy or web server), do so.

## Portability & Best Practices
- **Auto-Organization**: Always default to basic filenames to keep project diagrams organized in the `Excalidrawings/` root.
- **Relocation**: You can copy the `directives/SKILL_excalidraw.md` and `execution/excalidraw_builder/` folder into any new project repo to immediately enable visual output capabilities.
- **Clean up**: Use `.tmp/` for intermediate JSON files to keep the workspace clean.

## Workflows You Should Facilitate
1. **Analyze a Project**: If the user wants a diagram of the repo, use your terminal tools (`list_dir`, `find_by_name`) to understand the structure. Then model the directory tree as a set of connected `Rectangle` nodes and generate the file.
2. **Data Flow / Architecture**: Model system architectures using `Ellipse` for databases, `Rectangle` for services, and `Edges` with labels for API calls or data pipes.
3. **Local API**: If the user wants a local web service to handle this dynamically (from another application), you can scaffold a quick Express/FastAPI server that executes the `generate.sh` script when a payload is received.
