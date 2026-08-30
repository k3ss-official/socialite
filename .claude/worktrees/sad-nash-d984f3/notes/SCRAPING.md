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
