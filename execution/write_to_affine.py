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
import time
import random
import string
from dotenv import load_dotenv

# ─── Load Environment ────────────────────────────────────────────────────────
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'), override=True)

API_URL      = os.getenv('AFFINE_API_URL', 'http://affine_server:3010')
API_TOKEN    = os.getenv('AFFINE_API_TOKEN', '')
WORKSPACE_ID = os.getenv('AFFINE_WORKSPACE_ID', '')

# Domain Doc IDs
DOC_IDS = {
    "Capital":   os.getenv("AFFINE_DOC_CAPITAL"),
    "Computers": os.getenv("AFFINE_DOC_COMPUTERS"),
    "Cars":      os.getenv("AFFINE_DOC_CARS"),
    "Cannapy":   os.getenv("AFFINE_DOC_CANNAPY"),
    "Clan":      os.getenv("AFFINE_DOC_CLAN")
}


def gen_id(length=10):
    """Generates a random Alphanumeric ID for BlockSuite blocks."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_snapshot(content):
    """Generates a BlockSuite snapshot for the provided content string."""
    page_id = gen_id()
    note_id = gen_id()
    para_id = gen_id()
    
    return {
        'type': 'page',
        'meta': {
            'id': page_id,
            'title': '',
            'createDate': int(time.time() * 1000),
            'tags': []
        },
        'blocks': {
            'type': 'block',
            'id': page_id,
            'flavour': 'affine:page',
            'version': 2,
            'props': {'title': {':internal:text$': True, 'delta': []}},
            'children': [{
                'type': 'block',
                'id': note_id,
                'flavour': 'affine:note',
                'version': 1,
                'props': {
                    'xywh': '[0,0,800,92]',
                    'background': {'dark': '#252525', 'light': '#ffffff'},
                    'index': 'a0',
                    'displayMode': 'both'
                },
                'children': [{
                    'type': 'block',
                    'id': para_id,
                    'flavour': 'affine:paragraph',
                    'version': 1,
                    'props': {
                        'type': 'text',
                        'text': {
                            ':internal:text$': True,
                            'delta': [{'insert': content}]
                        }
                    },
                    'children': []
                }]
            }]
        }
    }

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
        return False, "AFFINE_API_TOKEN not set"

    domain = entry.get('domain', 'Clan')
    target_doc_id = DOC_IDS.get(domain)

    if not target_doc_id:
        return False, f"No Document ID found for domain: {domain}"

    # Format the content as a readable string
    tag_str = f"\nTags: {', '.join(entry.get('tags', []))}" if entry.get('tags') else ""
    formatted_content = (
        f"### {entry.get('title', 'Untitled Entry')}\n"
        f"**Category:** {entry.get('category', 'Inbox Log')}\n\n"
        f"{entry.get('summary', 'No summary provided.')}\n\n"
        f"---\n"
        f"*Source:* {entry.get('source_raw', 'Manual entry')}\n"
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
            "content": {"body": formatted_content},
            "docMode": "page",
            "docTitle": domain
        }
    }

    # Debug to stderr
    print(f"DEBUG: Filing to Domain: {domain} (Doc: {target_doc_id})", file=sys.stderr)
    result = run_graphql(query, variables)
    
    if "errors" in result:
        err_msg = json.dumps(result['errors'])
        print(f"ERROR: GraphQL Failure: {err_msg}", file=sys.stderr)
        return False, f"GraphQL Error: {err_msg}"
        
    comment_id = result.get("data", {}).get("createComment", {}).get("id")
    if comment_id:
        return True, f"Entry successfully filed as Comment {comment_id} in {domain}."
    
    return False, "Unknown error: No comment ID returned."

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='OpenBrain Filing Cabinet')
    parser.add_argument('entry', nargs='?')
    parser.add_argument('--stdin', action='store_true')
    args = parser.parse_args()

    try:
        raw_input = sys.stdin.read().strip() if args.stdin else args.entry
        if not raw_input:
            raw_input = '{"domain": "Clan", "title": "System Test", "summary": "Re-verified."}'

        entry = json.loads(raw_input)
        success, message = save_to_affine(entry)
        
        # Only JSON to stdout
        print(json.dumps({"success": success, "message": message}, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
