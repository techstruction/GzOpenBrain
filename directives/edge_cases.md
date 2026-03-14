# Directive: Known Edge Cases & Disambiguation

> **Last updated:** 2026-03-12
> **Context:** Lessons learned during Stage 7 testing of the OpenBrain pipeline.

---

## 1. Intent Ambiguity (Capture vs. Execute)

**Scenario**: User says "Find a new car project."
- **Issue**: Should the system just save this note (`capture`) or summon the Scribe/OpenClaw to actually perform a search (`execute`)?
- **Policy**: Default to `capture` unless the user uses an action verb ("Write", "Search", "Fix", "Code", "Research") or the `/ask` command. The Architect Critic is trained to look for these action verbs.

## 2. Cross-Domain Conflict

**Scenario**: "Pay the mechanic for the server repair."
- **Issue**: This involves `Capital` (paying), `Cars` (mechanic), and `Computers` (server).
- **Policy**: Prioritize the **Asset** over the **Action**. If it's about a server, it goes to `Computers`. If it's about a car, it goes to `Cars`. Finance (`Capital`) is only for pure investment/cash management entries.

## 3. High-Latency "Thinking" Models

**Scenario**: Kimi k2.5 or local Qwen 3.5 takes >60s to "think".
- **Issue**: Webhook timeouts (Flask/Ngrok).
- **Policy**: Use the `timeout=120` in scripts. If requested via Telegram, send a "⚡️ Processing..." message immediately to prevent the user from thinking the system is dead.

## 4. Bouncer Over-Zealotry

**Scenario**: User sends a shorthand note "m3 parts list".
- **Issue**: Bouncer might flag it as "Too short/low quality".
- **Policy**: Short notes are acceptable if they contain high-value keywords (e.g., specific models like "M3" or "BTC"). The Bouncer should "Pass" if a Domain-specific keyword is detected, even if the sentence structure is poor.

---

## Related Files
- `directives/sorter.md`
- `directives/bouncer.md`
- `directives/architect.md`
