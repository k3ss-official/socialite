# Lessons

One topic per entry, one-line summary each. Update in place; delete what turns out wrong.

- **Verify candidate websites by content, not URL** — a page must mention the business name (all tokens for short names) before any verdict counts; everything else is a directory or coincidence.
- **"Real site on unrelated domain" = template** — tech-averse owners with a genuine web investment have their name in the domain; their content on a borrowed/odd domain is a freebie deployment (Scran Away's dogonapc.com case).
- **FIND will hit our own cold-pitch demos** — every prospect we've pitched has one of our sites in their search results; sitecheck detects the Socialite.Design credit and flags the lead as re-engagement (confirmed pattern: dogonapc.com was Tony's demo, deal went cold).
- **Research starts from known URLs, not fresh search** — FIND already proved which URLs are theirs; harvest those first, search only fills gaps.
- **Nested `claude -p` needs env scrubbing** — inside a Claude Code session, ANTHROPIC_BASE_URL/auth vars leak into subprocesses and 401 the CLI; llm.py strips them.
- **Subagents share the account rate limit** — parallel agent fan-out dies instantly during a cooldown window; build inline when the limit is near.
- **`claude -p` is an agent, not a text API** — left unguarded it wrote a bible file straight into the repo mid-call with invented metadata; llm.py now disallows mutating tools and runs it from /tmp. Treat every nested-agent call as having hands unless you tie them.
- **Free APIs gate on User-Agent, and OSM area names must exist verbatim** — overpass-api.de 406s generic client UAs (send a descriptive tool UA), and `area["name"=...]` returns silent zero for names OSM doesn't have ("Pokhara Lakeside" → nothing, "Pokhara" → 1.7k businesses); a 0-result sweep means check the area name before blaming the query.
- **Sales-rep alerts must be part of the bible contract** — closures, ownership changes, phone/postcode conflicts, and prior-pitch detection only get surfaced if the schema requires an `alerts` field and the prompt feeds FIND's evidence in; prompt v2 caught a postcode error in our own demo site.
