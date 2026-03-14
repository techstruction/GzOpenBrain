#!/usr/bin/env python3
"""
write_to_affine.py — OpenBrain Filing Cabinet

Updates classified entries to the Affine database using GraphQL.
Since self-hosted Affine (v0.x) doesn't expose a simple document creation mutation,
this version files entries as Comments on Domain-specific documents.

Usage:
    python3 execution/write_to_affine.py '{"domain": "Capital", "title": "Btc", "summary": "buy", ...}'
"""

import os
import sys
import json
import argparse
import requests
from dotenv import load_dotenv

# ─── Load Environment ────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

API_URL      = os.getenv('AFFINE_API_URL', 'https://affine-macbridge.techstruction.co')
API_TOKEN    = os.getenv('AFFINE_API_TOKEN', '')
WORKSPACE_ID = os.getenv('AFFINE_WORKSPACE_ID', '')

def run_graphql(query, variables):
    """Executes a GraphQL mutation/query with the provided variables."""
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "X-Forwarded-Proto": "https"
    }
    payload = {
        "query": query,
        "variables": variables,
        "operationName": "CreateEntry"
    }
    try:
        response = requests.post(f"{API_URL}/graphql", json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"errors": [{"message": str(e)}]}

def save_to_affine(entry):
    """
    Fails over from Doc creation to Comment-based filing on Domain Pages.
    """
    if not API_TOKEN:
        return False, "AFFINE_API_TOKEN not set in .env"

    domain = entry.get('domain', 'Clan')
    title = entry.get('title', 'Untitled Entry')
    summary = entry.get('summary', '')
    category = entry.get('category', 'Inbox')
    tags = entry.get('tags', [])
    
    # Mapping domains to their respective Document IDs from .env
    domain_map = {
        "Capital": os.getenv('AFFINE_DOC_CAPITAL'),
        "Computers": os.getenv('AFFINE_DOC_COMPUTERS'),
        "Cars": os.getenv('AFFINE_DOC_CARS'),
        "Cannapy": os.getenv('AFFINE_DOC_CANNAPY'),
        "Clan": os.getenv('AFFINE_DOC_CLAN')
    }
    
    target_doc_id = domain_map.get(domain) or domain_map.get("Clan")
    
    if not target_doc_id:
        return False, f"Missing target Doc ID for domain: {domain}"

    # Format the entry content for the comment
    tag_str = f" #{' #'.join(tags)}" if tags else ""
    formatted_content = (
        f"📌 **{title}** ({category})\n"
        f"📝 {summary}\n"
        f"🔗 Source: {entry.get('source_raw', 'Unknown')}\n"
        f"⏱ {entry.get('created_at', 'Just now')}{tag_str}"
    )

    query = """
    mutation CreateEntry($input: CommentCreateInput!) {
      createComment(input: $input) {
        id
      }
    }
    """
    
    variables = {
        "input": {
            "workspaceId": WORKSPACE_ID,
            "docId": target_doc_id,
            "content": {"body": formatted_content}, # Affine 0.26+ expects JSONObject
            "docMode": "page",
            "docTitle": domain
        }
    }

    print(f"DEBUG: Filing to Domain: {domain} (Doc: {target_doc_id})")
    result = run_graphql(query, variables)
    
    if "errors" in result:
        err_msg = json.dumps(result['errors'])
        print(f"ERROR: GraphQL Failure: {err_msg}")
        return False, f"GraphQL Error: {err_msg}"
        
    comment_id = result.get("data", {}).get("createComment", {}).get("id")
    if comment_id:
        return True, f"Entry successfully filed as Comment {comment_id} in {domain}."
    
    return False, "Unknown error: No comment ID returned."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain Filing Cabinet — Store in Affine')
    parser.add_argument('entry', nargs='?', help='Classified JSON entry')
    parser.add_argument('--stdin', action='store_true', help='Read entry from stdin')
    args = parser.parse_args()

    try:
        if args.stdin:
            raw_input = sys.stdin.read().strip()
        elif args.entry:
            raw_input = args.entry
        else:
            # Test default
            raw_input = '{"domain": "Clan", "title": "System Test", "summary": "Pipeline re-verified."}'

        entry = json.loads(raw_input)
        success, message = save_to_affine(entry)
        
        print(json.dumps({
            "success": success,
            "message": message
        }, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)
