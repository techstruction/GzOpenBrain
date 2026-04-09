---
name: github-scan
description: Search GitHub for repos, fetch trending pages, and read READMEs. Uses GitHub public API (no key) and Jina Reader. ZoClaw only — Rigs (COMPUTERS domain). Store discoveries to openbrain.db via openbrain-interact.
---

# Skill: github-scan

**Level:** Domain
**Agent:** ZoClaw (Rigs — COMPUTERS)
**Purpose:** Research trending repos, search GitHub by topic, and fetch READMEs. File discoveries to openbrain.db.

> **Deployment note:** Deploy to `/root/.openclaw/skills/github-scan/` (top-level, not `domain/github-scan/`).

---

## Use Mode A — Trending repos (Jina Reader)

```bash
# All languages
curl -s "https://r.jina.ai/https://github.com/trending"

# Filter by language
curl -s "https://r.jina.ai/https://github.com/trending/python"
```

Returns markdown. Parse for repo names, descriptions, and star counts from the page text.

---

## Use Mode B — Search repos (GitHub API, no auth)

```bash
curl -s "https://api.github.com/search/repositories?q=<query>&sort=stars&order=desc&per_page=5" \
  -H "Accept: application/vnd.github+json"
```

Extract from JSON response:
- `.items[].full_name` — owner/repo
- `.items[].description` — one-line description
- `.items[].stargazers_count` — star count
- `.items[].html_url` — repo URL

**Rate limit:** 60 req/hr unauthenticated. If `GITHUB_TOKEN` is in `/root/.zo_secrets`, add:
`-H "Authorization: Bearer $GITHUB_TOKEN"` for 5,000 req/hr.

---

## Use Mode C — Fetch README (Jina Reader)

```bash
curl -s "https://r.jina.ai/https://github.com/<owner>/<repo>"
```

Returns clean markdown of the repo's README. Use for deeper tool evaluation.

---

## Filing discoveries to openbrain.db

After a scan, file notable tools using the `openbrain-interact` skill:
- domain: `COMPUTERS`
- type: `tool-discovery`
- content: JSON with `repo`, `description`, `stars`, `url`, `summary`

---

## When to use

- Weekly trending repo scan for Rigs
- Specific technology research triggered by user message
- Evaluating a specific repo before recommending to the team

---

## Error handling

If GitHub API returns 403 (rate limit), wait and retry once. If Jina returns empty, skip that URL.
