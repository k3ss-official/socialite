# Scraping Quirks (per platform)

Field notes on what each platform allows anonymously. Keep current — this file is gold.

## Facebook
- Page URLs return HTTP 200 anonymously but serve a JS shell / login wall — zero extractable text via plain requests. Don't mistake 200 for content; check text length.
- Page *existence* and page-root URL are reliably discoverable via DDG search results (titles include the page name).
- Group posts mentioning a business surface well in search snippets — useful evidence, never use as the business's own social URL (`/groups/` is filtered out in find.py).
- Upgrade path if we need post content: scrapling (pip, self-hosted stealth browser) — not worth it for MVP.

## Instagram
- Same as Facebook: 200 + JS shell, no anonymous text. Profile URL discovery via search works.
- Search sometimes returns post URLs (`/p/<shortcode>`) which are SHORTER than profile URLs — never pick socials by URL length alone (find.py ranks profile-roots first).

## DuckDuckGo (ddgs lib)
- Free, keyless, works. Result variance between identical runs is real — same query returns different orderings/sets minutes apart. Pipelines must not assume determinism here.
- Occasional transient failures; one retry with backoff is enough.

## Directory-scraper sites (findglocal, mapquest, cylex, theukhighstreet, wanderboat.ai, ...)
- Endless supply of these; blocklists always lose. Structural rules win:
  - their own site has the business name in the domain, or
  - content on an unrelated domain + deep path = somebody's listing page.
- They ARE useful as research sources: findglocal/cylex carry address, hours, phone scraped from FB before the login walls went up.

## Generic search-term hazard
- Business names made of common words ("Scran Away" — 'scran' = northern slang for food) poison unquoted queries. Always quote the exact name, and verify every fetched page actually mentions the business before harvesting text or images from it.

## ratings.food.gov.uk (UK FSA)
- Searchable, anonymous, reliable. Confirms a food business exists, gives address + hygiene rating. Snippets can leak the council's email — never treat a gov.uk address as business contact.

---

# Addendum 2026-07-19 — Scrapling field test (Scran Away golden path, manual re-run)

## Facebook, corrected diagnosis
- Scrapling stealthy fetch DOES beat Meta's bot detection: real 200, real page pipeline, no login redirect — the "upgrade path" note above is confirmed viable.
- The actual blocker in UK/EU is the **GDPR consent interstitial**, not bot detection and not (for pages) the login wall. A fetcher cannot consent; no amount of stealth fixes a legal gate.
- **Production fix:** drive Scrapling as a *library* in research.py — one page_action click on "Decline optional cookies" (decline is also the privacy-correct default), persist the consent cookies, pass them via `cookies` on every subsequent fetch for that locale. One consent, whole run sails.

## MCP vs library doctrine
- The Scrapling MCP tools (fetch/stealthy_fetch/bulk_*) are for **ad-hoc recon only** — they fetch, they don't interact.
- The **pipeline always drives the library directly** (page_action, cookie persistence, retry policy under our control). Never build a stage on the MCP wrapper.

## Concurrency limits (hard lesson)
- bulk_stealthy_fetch with 3 parallel stealth browsers **hung the MCP server** — 4-minute timeout, server dead, restart required.
- Rule: **stealthy fetches run serial** (concurrency 1) on the Mini until proven otherwise. Plain-requests fetches can parallelise; browsers cannot, cheaply.
- Supervise the Scrapling MCP under launchd with auto-restart, same as the gateway.
- Anti-loop: a hung server is a dead source for the run — log it, move on, never retry into it.

## Google Places is the richest anonymous seam
- Today's manual bible got the entire competitor gap matrix — review counts, averages, pull-quotes, hours, phone, price level — from Places + FSA + search snippets alone, zero walled-social access needed.
- Implication: walled socials are *enrichment*, not a dependency. A bible can hit quality gate without them; don't burn time/risk on Meta when Places already carries the pitch.

## Failure log (this run)
- FB stealthy single fetch → 200, content = consent interstitial only. (Fix above.)
- bulk_stealthy_fetch ×3 → MCP server hang, 4-min timeout, no retry attempted.

## Agent scoping note
- Socialite runs on its **own dedicated Hermes-framework agents**, documented in this repo. House/system agents (Rae, Janet, etc.) are separate infrastructure and out of scope for Socialite pipeline work.
