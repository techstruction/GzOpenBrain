# Self-Healing Protocol & Troubleshooting Ledger

This document serves as the high-fidelity memory of the OpenBrain project. It captures architectural failures, "ghost-in-the-machine" bugs, and the surgical fixes required to resolve them. **Read this before attempting to modify the Affine pipeline or the Classification engine.**

---

## ⚡️ Key Case Studies

### 1. The Affine Filing Visibility Crisis (March 2026)
**Symptom:** The `write_to_affine.py` script returns a 200 OK and a valid Comment ID, but the note is completely invisible in the Affine UI sidebar.

**The "War Room" Discovery:**
- **Initial Assumption:** Just sending text in the `content` field would work. **Result:** Failure.
- **Trial 2 (The Map):** Sending a "Flat Map" of Block IDs. **Result:** Failure (API accepts it, UI ignores it).
- **The Breakthrough:** Using browser-captured network requests, we discovered that Affine's frontend requires a **Nested Tree** snapshot structure. Even a single missing property (like `flavour` or `index`) renders the entire comment invisible.

**The Fix:**
- Implemented `generate_gold_standard_snapshot()` in `write_to_affine.py`. This function clones the exact, bit-for-bit JSON structure captured from a manual browser interaction.
- **Key Lesson:** In Affine/BlockSuite, **Structure is Visibility**. If the JSON schema isn't 100% compliant with the frontend's expectation, the data is "orphaned" in the database.

---

### 2. The "Poisoned Sidebar" (Frontend Corruption)
**Symptom:** Even after fixing the snapshot format, the Comments panel remained empty ("No comments yet") and the browser console reported:
`TypeError: Cannot read properties of undefined (reading 'type') at DocCommentStore.listComments`

**Root Cause:**
- One or more malformed comments (from earlier troubleshooting steps) contained data that the Affine frontend didn't know how to map.
- Because Affine fetches *all* comments for the sidebar, **a single malformed entry crashes the entire rendering loop.** This makes even perfectly formatted new comments invisible.

**The Fix:**
- Created a surgical cleanup script (`cleanup.py`) to delete the specific malformed IDs via GraphQL mutation (`deleteComment`).
- **Healing Rule:** If the UI crashes, assume data corruption in the document history. Purge the "poisoned" entries to restore the render loop.

---

### 3. Classification Accuracy & Domain Drift
**Symptom:** Technical messages mentioning "Affine", "OneBrain", or "Agentic System" were defaulting to the **Clan** domain instead of **Computers**.

**Root Cause:**
- The `CLASSIFICATION_PROMPT` had loosely defined boundaries.
- **Clan** was acting as a "catch-all" when the model was uncertain.
- Lack of specific "Anchors" for the project's own terminology.

**The Fix:**
- **Deep Definitions:** Explicitly anchored "Affine", "OpenClaw", and "Coding" to **Computers**.
- **Negative Constraints:** Explicitly told the model that **Clan** is strictly for *personal* life and MUST NOT contain work/tech.
- **Internal Reasoning:** Added a `_reasoning` field to the classification output. This allows the bot to explain its logic to the logs, making it easier to audit "why" a mis-classification happened.

---

### 4. Background: Nvidia API 404 Errors
**Symptom:** Internal classification failed with a 404 "Function Not Found" after a server-side script update.

**Root Cause:**
- Certain models (like `nemotron-70b`) may be deprecated or restricted for specific API keys in certain regions/accounts, even if they appear in standard lists.

**The Fix:**
- Verified model availability via direct `curl` from the server.
- Switched to `meta/llama-3.1-70b-instruct`, which proved most stable for the `macbridge` environment.

---

## 🛠 Self-Healing Checklist (The "Golden Rules")

1. **Verify the Target Doc ID:** Always check `.env` against the live browser URL. A doc ID mismatch is the #1 cause of "missing" data.
2. **Standardize Newlines:** BlockSuite's delta format hates literal `\\n` chars. Always use standard Python `\n` in JSON payloads.
3. **Internal URLs First:** When running inside Docker, use `http://affine_server:3010` instead of the public URL to avoid NAT/Proxy latency and timeouts.
4. **The STDIN Protocol:** When passing complex JSON records to scripts, use `sys.stdin.read()` + the `--stdin` flag. Shell passing of large JSON strings often breaks due to escaping/quote nesting.

---
*Capture every failure. Update the ledger. The system grows through scar tissue.*
