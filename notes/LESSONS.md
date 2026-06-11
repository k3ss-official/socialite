# Lessons

One topic per entry, one-line summary each. Update in place; delete what turns out wrong.

- **Verify candidate websites by content, not URL** — a page must mention the business name (all tokens for short names) before any verdict counts; everything else is a directory or coincidence.
- **"Real site on unrelated domain" = template** — tech-averse owners with a genuine web investment have their name in the domain; their content on a borrowed/odd domain is a freebie deployment (Scran Away's dogonapc.com case).
- **Research starts from known URLs, not fresh search** — FIND already proved which URLs are theirs; harvest those first, search only fills gaps.
- **Nested `claude -p` needs env scrubbing** — inside a Claude Code session, ANTHROPIC_BASE_URL/auth vars leak into subprocesses and 401 the CLI; llm.py strips them.
- **Subagents share the account rate limit** — parallel agent fan-out dies instantly during a cooldown window; build inline when the limit is near.
