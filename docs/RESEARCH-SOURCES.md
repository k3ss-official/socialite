# Research sources and collection limits

The current collector uses ddgs search, requests and BeautifulSoup. It attempts known
business URLs before matched search results and a category/locality competitor query.
It is not OpenAI Deep Research, a browser scraper or a complete social audit.

## Implemented behavior

- At most 14 page attempts, 3 competitor page attempts, 8 saved images and 16 image attempts.
- Record search outcomes, HTTP status, metadata, source IDs, capture times and saved text hashes.
- Keep useful Open Graph descriptions without equating a JavaScript shell with full content access.
- Stop further requests to a host after HTTP 403 or 429 within the run; do not bypass challenges.
- Fetch prospect images only from matching pages; keep original URL and unresolved reuse rights.
- Reuse matching captures for 24 hours only if their files and hashes are intact.
- Keep independent collection manifests under `raw/history/`; a failed refresh does not erase old receipts or pass them off as current research.
- Support cancellation between operations. Global scheduling/throttling and richer source plans remain future work.

Search results vary. One bounded retry handles search transport failures; empty results
and inaccessible pages remain explicit coverage limitations. Discovery domain shapes
help prioritise candidates, but an affiliated website can legitimately live on another
domain. A Socialite footer credit does not prove a failed prior sales approach.

Facebook Page, Group and account types are distinct. A Group is not automatically
private or invisible to search. Resolve exact URLs and current access; do not infer
absence from one search query or automatically filter Group URLs out. Instagram and
Facebook may return metadata, consent pages, login screens or JavaScript shells;
record what was actually accessible rather than generalising an old experiment.

Directories can supply leads for identity/contact verification, but distinguish them
from a business's own site. Do not copy an authority's email into a business contact.
Use official guidance and registers where applicable, such as Google eligibility,
HSE equipment guidance and food hygiene information for food businesses. No Google
Places, regulatory or review API adapter is integrated yet.

## Capabilities to evaluate

| Candidate | Evaluation purpose | Current status |
|---|---|---|
| OpenAI Deep Research | Broad sourced research and report synthesis | No runtime adapter or benchmark |
| Gemini | Independent research/synthesis comparison | User has Pro; API access and integration unverified |
| Flowith Neo | Research automation and possible vendor-built components | User reports about 100,000 gift credits; no integration |
| Scrapling | Browser-based collection where permitted and useful | Historical experiment only; not installed by requirements or integrated |
| Chrome DevTools, browser use, computer use | Inspect rendered pages and bounded interactive workflows | Evaluate actual local tools and permissions; no automatic browser control |
| last30days | Recent reputation/trend monitoring where appropriate | Not integrated |
| Higgsfield | Creative assets after research and design briefs | User reports about 6,000 credits; no pipeline generation adapter |

Subscriptions, credits and an installed app do not establish API entitlement or callable
capabilities in every session. Assess source coverage, evidence export, cost, stability,
integration effort and reproducibility before choosing. Do not install everything by
default or build a dependency on a source the business cannot make accessible.

Earlier July field tests are recoverable in Git history. They inform experiments, not
current platform guarantees or instructions to use stealth/bypass blocked sources.
