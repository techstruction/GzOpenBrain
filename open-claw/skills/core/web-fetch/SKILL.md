---
name: web-fetch
description: Fetch a single URL and return clean markdown using Jina Reader (https://r.jina.ai). Free, no API key. Use for articles, README files, docs, news pages. NOT for full-site crawls, JS-heavy SPAs, paywalled content, or internal/LAN URLs.
---

# Skill: web-fetch

**Level:** Core
**Agent:** Any OpenClaw instance (ZoClaw, NemoClaw)
**Purpose:** Fetch a URL and return clean markdown. No API key, no cost.

> **Deployment note:** OpenClaw scans top-level skill directories only.
> Deploy to `~/.openclaw/skills/web-fetch/` (not `core/web-fetch/`).

---

## How to invoke

Prepend `https://r.jina.ai/` to the full target URL and curl it:

```bash
curl -s "https://r.jina.ai/https://example.com/some-page"
```

No headers, no auth, no encoding required for standard URLs.

**In batch scenarios** (multiple fetches in a loop): add `sleep 1` between calls to respect Jina's soft rate limit.

---

## Output

Clean markdown of the page content. Jina strips nav, ads, and boilerplate.
Very long pages are truncated — acceptable for single-page reads.

---

## Error handling

If the response is empty or contains a Jina error message, log it and return an empty string. Do not retry more than once.

---

## When NOT to use

- Full-site crawls → use `web-crawl`
- JS-heavy SPAs that require JavaScript rendering
- Paywalled or login-gated content
- Internal/LAN URLs (Jina is an external service)

---

## Example

```bash
# Fetch GitHub trending page
curl -s "https://r.jina.ai/https://github.com/trending"
```
