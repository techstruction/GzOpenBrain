import os
import time
import base64
import subprocess
import json

# Configuration
WORKSPACE_ID = "00925943-6237-425b-b3a2-5641b75f568f"
USER_ID = "443b1fcb-a362-47e5-b546-82b7e9b9d40c"
PAGE_ID = "db_test_page_" + str(int(time.time()))

def run_psql(cmd):
    full_cmd = f"docker exec affine_postgres psql -U affine -d affine -c \"{cmd}\""
    result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
    return result

def test_db_filing():
    print(f"Starting DB filing POC for PAGE_ID: {PAGE_ID}")
    
    # 1. Insert Metadata into workspace_pages
    # We need to satisfy the schema (id is page_id, workspace_id, public, etc)
    # Based on our \d workspace_pages check earlier: 
    # id (character varying), workspace_id (character varying), public (boolean), defaultRole (smallint)
    # The table actually has 'page_id' and 'workspace_id' as PK? Wait.
    # Let's check columns again just to be 100% sure on names.
    # From previous \d: workspace_id, page_id (Indexes: workspace_pages_pkey PRIMARY KEY, btree (workspace_id, page_id))
    # Columns listed were: workspace_id, page_id, public, defaultRole, summary, title, blocked, published_at.
    
    title = "DB DIRECT FILING TEST"
    # use double quotes and escape them for the shell
    insert_page = f"INSERT INTO workspace_pages (workspace_id, page_id, public, \\\"defaultRole\\\", title) VALUES ('{WORKSPACE_ID}', '{PAGE_ID}', false, 30, '{title}');"
    
    # Minimal Yjs doc state hex (correct prefix for v1 update)
    # Binary: [0, 0] is AgHGpPqDBQA= in some encodings, but let's use a real one.
    blob_hex = "000101" # Very minimal Yjs update (empty state)
    
    insert_update = f"INSERT INTO updates (guid, workspace_id, blob, created_at, created_by) VALUES ('{PAGE_ID}', '{WORKSPACE_ID}', decode('{blob_hex}', 'hex'), now(), '{USER_ID}');"
    
    print("Inserting metadata...")
    res1 = run_psql(insert_page)
    if res1.returncode != 0:
        print(f"Metadata fail: {res1.stderr}")
        return

    print("Inserting update...")
    res2 = run_psql(insert_update)
    if res2.returncode != 0:
        print(f"Update fail: {res2.stderr}")
        return

    print("Successfully filed via DB! Check Affine UI for 'DB DIRECT FILING TEST'.")

if __name__ == "__main__":
    test_db_filing()
