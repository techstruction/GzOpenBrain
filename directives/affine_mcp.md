# Directive: Affine MCP Server

## Goal
Provide a Model Context Protocol (MCP) server that allows AI agents to interact with the Affine database (affine-macbridge). This enables seamless storage, retrieval, and organization of documents within the OpenBrain ecosystem.

## Scope
The MCP server should expose tools for:
- Listing workspaces
- Listing documents in a workspace
- Creating new documents
- Appending content to documents
- Reading document content
- Searching for documents

## Architecture (3-Layer)
- **Directive**: This file.
- **Orchestration**: Antigravity (the agent) routes user requests to the MCP tools.
- **Execution**: `execution/mcp/affine_mcp.py` (The Python FastMCP server).

## Tool Definitions

### `affine_list_workspaces`
- **Description**: Lists all available workspaces in the Affine instance.
- **Inputs**: None.
- **Output**: JSON list of workspaces (id, name, etc.).

### `affine_list_docs`
- **Description**: Lists documents within a specific workspace.
- **Inputs**:
    - `workspace_id`: The UUID of the workspace.
- **Output**: JSON list of documents (id, title, updated_at).

### `affine_create_doc`
- **Description**: Creates a new document in a workspace.
- **Inputs**:
    - `workspace_id`: The UUID of the workspace.
    - `title`: The title of the document.
    - `content`: Initial content (Markdown).
- **Output**: JSON object with the new document's ID.

### `affine_read_doc`
- **Description**: Reads the content of a specific document.
- **Inputs**:
    - `doc_id`: The UUID of the document.
- **Output**: The document content as Markdown or JSON structure.

### `affine_append_content`
- **Description**: Appends Markdown content to an existing document.
- **Inputs**:
    - `doc_id`: The UUID of the document.
    - `content`: The Markdown content to append.
- **Output**: Success/Failure status.

## Environment Variables
The server reads from the system env or `.env` file:
- `AFFINE_API_URL`: Base URL of the Affine instance (e.g., `https://affine-macbridge.techstruction.co`).
- `AFFINE_API_TOKEN`: Bearer token for authentication.
- `AFFINE_WORKSPACE_ID`: Default workspace ID (optional).

## Self-Annealing
- If an API call fails due to authentication, log the error and suggest checking the token.
- If the endpoint changes, update the internal tool mapping and this directive.
- Log all interactions for auditability.
