---
name: research-topic
description: Research a topic by fetching 1-5 seed URLs via Jina Reader, summarizing via Rate Queue LLM, and filing the result to openbrain.db. Takes topic, urls, and domain as inputs.
---

# Skill: research-topic

**Level:** Workflow
**Agent:** Any OpenClaw instance (ZoClaw, NemoClaw)
**Purpose:** Fetch, summarize, and file. Composes web-fetch + llm-complete + db-write.

## Step 1 - Fetch (web-fetch)

Fetch each seed URL using Jina Reader. Max 5 URLs per call. Sleep 1s between requests.

```bash
curl -s "https://r.jina.ai/<url>"
sleep 1
```

Collect the returned markdown. Skip empty or error responses.

## Step 2 - Summarize (llm-complete via Rate Queue)

Rate Queue URL by claw:
- ZoClaw: http://127.0.0.1:18792/v1
- NemoClaw: http://100.106.189.97:18792/v1

Send fetched content to the chat completions endpoint.
Model: nvidia/meta/llama-3.1-8b-instruct
System: "You are a research assistant. Summarize the provided content concisely and extract key facts relevant to the topic."
User: "Topic: <topic>\n\nContent:\n<fetched_content>"
Max tokens: 500

Parse result from: .choices[0].message.content

Concatenate content from all URLs into one request -- one LLM call per research task.

## Step 3 - File to DB (openbrain-interact)

Use the openbrain-interact Python script to create an item:

```bash
source ~/.zo_secrets  # ZoClaw only -- sets DIRECTUS_URL and DIRECTUS_API_TOKEN

python3 /home/workspace/Skills/openbrain-interact/openbrain_interact.py item-create \
  <domain> "research-topic" "<topic>" \
  "<summary from Step 2>" \
  --type research --source research-topic
```

NemoClaw path: /sandbox/.openclaw/skills/openbrain-interact/openbrain_interact.py
NemoClaw secrets: source /sandbox/.nemoclaw-secrets

## Inputs

- topic -- what is being researched (e.g., "AI agent frameworks 2026")
- urls -- 1-5 seed URLs to fetch
- domain -- OPENBRAIN domain (COMPUTERS, CAPITAL, CARS, CANNAPY, CLAN)

## Output

Summary returned to calling agent. Item written to openbrain.db with item_type=research, source=research-topic.

## Constraints

- Max 5 URLs. Never call NVIDIA directly -- always use Rate Queue.
- NemoClaw Rate Queue: http://100.106.189.97:18792/v1
- Colons in description field break SKILL.md parsing -- avoid "Key: value" patterns in frontmatter description.
