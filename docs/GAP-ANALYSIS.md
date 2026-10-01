# Socialite Design repository gap analysis

Assessed: 1 October 2026. Baseline: [`520758d`](https://github.com/k3ss-official/socialite/tree/520758d9efa27f72106b2b191ed29259f3bcc7b1).

Socialite has a useful CLI prototype: lead discovery, bounded page collection, Claude synthesis, versioned Bible artifacts, static website generation, deterministic pitches, and a local dashboard. It does **not yet implement the staff-selected, evidence-backed business deep dive described in the current brief**. The most valuable next milestone is one complete, reviewable journey from selecting a prospect to generating a preview from approved facts.

This report separates implemented behavior from design documents. Checks ran in an isolated repository copy, with external research and model calls mocked for targeted probes. No live deployment, outreach, paid generation, or provider benchmark was performed. Runtime code in the source checkout was not changed.

## The intended journey

1. Discover businesses with a Facebook presence and no adequate website. Keep the qualification evidence, including weak existing sites, rather than forcing every prospect into “no site.”
2. Staff select a prospect and launch a tracked research job.
3. Gather company identity, public professional owner/operator information, likely customers, social presence, missing foundations, suitable channels, comparable competitors, content, assets, and relevant credentials.
4. Produce a versioned Bible with claim-level evidence, explicit uncertainty, conflicts, collection coverage, and a high-level now / next / later roadmap.
5. Staff resolve or acknowledge uncertainties and approve the facts and assets usable in a landing page.
6. Generate a client-branded preview and a relevant service proposal from that approved material. Maintain the Bible as facts and services change.

The Bible must be useful to staff and machine-readable. A polished report alone does not meet the requirement if the website generator cannot safely consume it.

## What is implemented

| Capability | Assessment | Evidence |
| --- | --- | --- |
| Lead discovery | Partial. Search and OpenStreetMap discovery exist; activity, identity matching, and website qualification need improvement. | [find.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/stages/find.py), [sitecheck.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/web/sitecheck.py) |
| Staff dashboard | Working artifact viewer and status/client ledger UI; no research launch or job tracking. | [app.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/dashboard/app.py), [lead.html](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/dashboard/templates/lead.html) |
| Public-source collection | Working requests/BeautifulSoup collector with page/image limits; limited extraction and no browser fallback. | [research.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/stages/research.py) |
| Bible synthesis | Working schema-shaped output and version reuse; contract primarily serves copy and website production. | [bible.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/stages/bible.py), [prompt](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/prompts/bible.md), [schema](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/schemas/bible.schema.json) |
| Comprehensive business audit | Missing as an integrated workflow. Some intended domains are documented, but owner research, customer profiles, social scoring, credentials, and roadmap have no complete runtime contract. | [deep-dive draft](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/docs/DEEP-DIVE-SPEC.md) |
| Competitor comparison | Partial. Competitors and boolean gaps exist; collection is tied to a fixed category and locality. No consistent two-way, evidence-backed comparison. | [research.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/stages/research.py), [Bible schema](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/schemas/bible.schema.json) |
| Landing-page generation | Working static build and caching for existing artifacts; one classic theme, incomplete input contract and publication checks. | [build.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/stages/build.py), [classic template](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/templates/site/classic/index.html.j2) |
| Service proposal | Working deterministic ladder selection; not a contextual now / next / later roadmap. | [pitch.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/stages/pitch.py), [ladder](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/config/ladder.yaml) |
| Versioning and events | Working file artifacts and JSONL events; SQLite recovery and client ledger persistence are incomplete. | [store.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/store.py) |
| Cost control | Estimated pre-call checks and reported-cost logging exist; a hard actual-spend cap is not demonstrated. | [llm.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/llm.py), [store.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/store.py) |
| Research tools/providers | Runtime uses ddgs, requests/BeautifulSoup, Overpass, and the local Claude CLI. Scrapling, browser collection, last30days, Open Notebook, and a Higgsfield creative workflow are not integrated. | [requirements](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/requirements.txt), [rebuild document](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/REBUILD.md), [creative draft](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/docs/CREATIVE-DIRECTOR-SOUL.md) |
| Recurring service delivery | Pricing and service records exist; monitoring, scheduled content refresh, and fulfillment are not implemented end to end. | [ladder](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/config/ladder.yaml), [store.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/store.py) |

The existing [deep-dive specification](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/docs/DEEP-DIVE-SPEC.md) already anticipates several important improvements, especially evidence IDs and richer social/review research. It labels itself a draft and uses paths and fields that differ from the live implementation. Reconcile it with the new brief before treating it as an executable specification.

## Findings that affect the next build

### 1. The dashboard cannot initiate the desired workflow

The only mutating dashboard routes change status or sign a lead. Staff cannot select a lead and start research, see collection progress, review failures, retry a stage, or approve a Bible. The [CLI](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/cli.py) runs stages sequentially; changing a dashboard status does not execute them.

Add persisted research jobs and a worker before expanding automation. Keep job state separate from prospect lifecycle state. A failed collection should be visible as a partial job with useful results, not disappear into a generic “bible” status.

The dashboard intentionally binds locally and has no authentication. Add staff identity, authorization, and protected write actions when making it accessible to a team; its current local setup is not evidence of a publicly exposed service.

### 2. The Bible contract cannot represent the full brief or its uncertainty

The [schema](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/schemas/bible.schema.json) centers on brand voice, palette, photos, services, reviews, competitors, gap booleans, and site copy. It lacks a consistent contract for:

- Company identity and entity matching; trading company versus venue; public professional owner/operator evidence.
- Measured customer information versus demographic hypotheses and local population context.
- Platform surface type, profile completeness, freshness, content quality, comparable engagement measures, and a transparent rating rubric.
- Critical foundations versus contextually appropriate additional channels. Instagram or TikTok should not be automatically “necessary” for every business.
- Verified hygiene ratings, affiliations, badges, and required customer-facing information, including applicability and verification date.
- Claim-level evidence, collection failures, conflicts, reviewer decisions, asset rights, and now / next / later actions.

Gap fields currently force true/false values. “Not found,” “inaccessible,” and “confirmed absent” need different meanings. Public inspection usually cannot establish whether a Google Business Profile is claimed; that should remain unknown unless direct evidence supports it.

The [prompt](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/prompts/bible.md) tells the model to treat qualification evidence as established fact, even though some qualification is heuristic. It calls alerts required, but the schema does not. A schema-valid Bible with optional typography omitted also crashes the current template. Shape validation alone is therefore insufficient.

Introduce a versioned Bible v2, with a compatibility projection for the existing builder and pitch. Keep research assertions separate from approved public copy. Do not replace the contract with a longer prompt and assume consumers will understand the new fields.

### 3. Collection can research the wrong business context

The [research stage](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/stages/research.py) uses the locale pack's town rather than the prospect's actual locality, and queries competitors as “takeaway street food” regardless of business type. In a mocked probe, an “Audit Prospect, Preston” lead produced Chorley queries. A cocktail bar needs nightlife/private-hire competitors, not a takeaway default.

The [discovery stage](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/stages/find.py) extracts phone/email from all search results before confirming they belong to the entity. A synthetic unrelated listing supplied the prospect's phone in the probe. It also demoted a valid sister-company venue page to “template” because the domain did not match the venue name.

Store explicit prospect location/category and candidate entity matches. Accept contacts and sites only with adequate business/location linkage. Preserve an affiliated site as an existing site and assess its quality separately.

### 4. Unavailable sources can become misleading business findings

The collector's `_fetch` collapses failures into `None`, losing whether the response was 403, 429, timeout, or another problem. Website checking treats access errors as “dead.” Search exceptions become empty results. That can turn a collection limitation into an unsupported “no website” or “missing presence” claim.

Public social metadata is also discarded when body text is short: a mocked Facebook shell containing useful Open Graph description data produced no usable text. A page returning HTTP 200 is not necessarily a successful extraction.

Record request outcomes, useful metadata, extraction completeness, and a reason for every unavailable source. Use bounded retries and stop on access challenges. Browser tools should render permitted public content; they should not turn a source's refusal into a collection loop.

### 5. Evidence and image handling are too weak for a maintained source of truth

Raw pages carry URLs and the bundle has a harvest time, but the production Bible lacks consistent evidence IDs linked to each claim. Image records omit a robust rights/approval state and original-image provenance. The model receives image file paths, not the actual images, yet is asked to select visual direction.

Existing raw research is reused indefinitely unless forced. Bible caching depends on raw text/JSON and a manually maintained prompt version; prompt contents, schema, model/configuration, and relevant lead changes are not all fingerprinted. Build caching excludes raw image bytes and relevant lead/locale inputs. A photo-only change reused the same site version in the probe.

Use immutable evidence captures with source URL, timestamp, relevant excerpt or screenshot, content hash, and access outcome. Give claims explicit observed / inferred / unknown / conflicted states, and independent review/publication status. Define freshness by field: event dates and opening hours age differently from brand history. Fingerprint all material inputs.

### 6. A fresh checkout loses the dashboard index and cost history

The repository contains 16 lead files, but a new SQLite database displayed zero leads. Stored JSONL events contained USD 1.286694 of recorded spend, while the fresh SQLite spend query returned zero. [store.py](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/socialite/store.py) creates empty tables without replaying the file artifacts/events.

Clients and active services live in SQLite without equivalent recoverable file artifacts. Decide explicitly whether the ledger's durable source is a backed-up database or replayable events. The current blanket “files are the source of truth” description does not cover that ledger.

Provide an idempotent index rebuild and documented backup/recovery. Writes to files, events, and SQLite need a consistent reconciliation strategy. Add atomic file replacement and safe version allocation when jobs introduce concurrent writes.

### 7. Signing is not idempotent, and cost limits are estimates

Submitting the same £39 foundation signup twice created two active service rows and displayed £78 monthly revenue. Make signup transactional and idempotent, with an explicit rule for service changes. Contracted revenue should be distinguished from collected payments.

The cost check accepts an estimated USD 0.30 operation; a mocked reported USD 3.00 call was then recorded despite the USD 2.00 lead cap. This did not spend real money. A preflight estimate cannot retroactively prevent an overrun. Bound provider work, reserve budget, reconcile actual usage, and distinguish a soft estimate from a guarantee. Include collection/generation spend beyond the current LLM call when those tools are added.

### 8. The page generator can publish unsupported trust claims

The [classic template](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/templates/site/classic/index.html.j2) averages selected review quotes into a displayed star rating. Two selected five-star quotes produced “5.0 from real reviews”; that is not a verified platform aggregate. Anonymous quotes can also receive “Verified review” text without a verification field.

Only render a platform rating with sourced aggregate, count, and capture date. Quote attribution needs its own evidence. Require approval for factual copy, review usage, badges, and images before publication; staff previews should clearly carry unresolved review status outside client-facing copy.

The Bible viewer currently constructs duplicate `images/images` paths: all eight image URLs tested returned 404, while the correct raw-image URL returned 200. Fix this independently of the larger schema change.

### 9. Tool access, design intent, and commercial delivery are not integrated capabilities

An available connector in this assistant session is not automatically callable by the deployed Socialite worker. Likewise, a consumer AI subscription or gift-credit balance does not establish API access, automation rights, or billing coverage. Inspect each integration's actual callable interface and operating terms during the tool-selection step.

Higgsfield's creative-director draft is a useful starting point, but there is no implemented signature system, asset-generation adapter, or approved-brief-to-build workflow. The current website uses one classic layout. Recurring service descriptions and prices are offers, not evidence of fulfillment automation.

There are also duplicate design documents and 133 tracked `.claude` files, including worktree copies. Pick canonical documents and remove obsolete tracked copies in a separate cleanup. Dependency versions are unpinned; there is no Python regression suite or CI configuration. Preserve a reproducible baseline before changing contracts.

## Recommended implementation order

| Order | Work package | Completion evidence |
| --- | --- | --- |
| 1 | Stabilize the existing baseline: rebuildable index/cost history, idempotent signup, image routes, contract/template alignment, correct prospect locality/category, explicit unavailable states, and truthful review rendering. | Fresh checkout shows saved leads; repeated signup does not change MRR; images load; a valid contract renders; wrong-entity data is rejected; an inaccessible source does not become “absent.” |
| 2 | Define Bible v2, evidence/capture contracts, quality gates, and the builder/pitch projection. Reconcile the old spec with the current brief. | Examples cover observed, inferred, unknown, stale, and conflicted claims; approved copy is traceable; existing valid builds still work through an explicit adapter. |
| 3 | Add staff-triggered jobs and the research/review UI using the existing collectors first. | Select one prospect; launch once; see progress and partial failures; retry safely; inspect receipts; approve publication fields; create a versioned preview. |
| 4 | Research and select the minimum tool stack, then add collection adapters, budget controls, freshness, and entity matching. | Every chosen integration has verified access, cost, limits, a fallback, and an acceptance test on relevant sources. No unexplained dependency on a desktop session. |
| 5 | Build the comprehensive research prompt and run the three-AI benchmark. Providers remain to be chosen. | Same brief, output contract, budget, and scoring rubric; source checks and quality results saved, with latency/cost and limitations. |
| 6 | Develop Socialite's signature design grammar and a small set of client-specific studies; connect approved assets to the builder. | Different business brands look distinct while sharing recognisable craftsmanship; approved image provenance, mobile/accessibility checks, and bounded generation spend. |
| Later | Recurring monitoring, service fulfillment, billing/payment reconciliation, and broader discovery scaling. | A working service-delivery loop and refreshed Bible, rather than just a subscription row. |

The first three packages should form one small end-to-end delivery. Avoid postponing all staff workflow work until every research tool is installed.

## Bible v2: minimum content and rules

Use structured sections for identity/company/operators; audience and local context; channels and surface types; services/menus/prices/hours/contact; reviews; brand voice; assets; relevant credentials; competitor comparisons; findings; roadmap; and approved landing-page inputs.

Each factual assertion should point to evidence IDs. Each inference should explain its basis and confidence. Each conflict should preserve the competing claims and the resolution needed. Unknown fields should state whether they were searched, inaccessible, inapplicable, or not yet investigated. Public professional owner information belongs here; unrelated private-life material does not improve the commercial brief.

Social ratings should expose their components, observation window, and available data. Compare competitors on the same measurement basis; do not infer reach, revenue, conversion, or audience demographics from follower counts. Capture both what competitors offer and what the prospect does better.

Roadmap items need evidence, expected customer/business benefit, priority, effort, dependencies, and proposed service. “Critical” should have a specific justification for this business. Recommendations about regulatory requirements need an appropriate authoritative source; a missing public record is not proof of noncompliance.

Keep report presentation flexible until the Genspark example arrives. The evidence and output contracts can be designed now without waiting for that visual reference.

## Tool-selection brief for the next stage

These are roles and candidates to investigate, **not a completed tool selection**:

| Role | Candidates to assess | Decision rule |
| --- | --- | --- |
| Discovery and search | Current ddgs/Overpass; a supported search API or research-provider search tool. | Structured provenance, geographic precision, dependable access, and affordable limits. |
| Authoritative facts | Companies House, Food Standards Agency, official local sources, appropriately licensed place/profile data. | Use business-relevant official evidence where applicable. Record what a public endpoint actually establishes. |
| Public page extraction | Current requests/BeautifulSoup; Scrapling if it measurably improves extraction/maintenance. | Start with the least costly supported method; preserve metadata and failure reasons. |
| Dynamic pages and inspection | Playwright/browser-use; Chrome DevTools or computer use for investigation and permitted interactive capture. | Bounded rendering with auditable captures. A usable runtime path matters more than installing overlapping tools. |
| Recent social signals | Platform-authorized APIs where available; last30days after repository/coverage/terms verification. | Treat recent trends as context, not authority for business identity or complete history. |
| Research synthesis | OpenAI, Gemini, Flowith Neo, and existing Claude capability. | Verify interactive versus API/worker access and costs; choose three for the benchmark after the contract is fixed. |
| Storage and retrieval | Existing versioned artifacts and SQLite first; assess Open Notebook only if it solves a demonstrated retrieval need. | Every result retains its source; avoid creating another conflicting source of truth. |
| Creative production | Higgsfield connector and supported runtime interface. | Approve a concrete creative brief and bounded asset batch; measure quality and credit use. |

Skills should describe collection policy, entity matching, evidence validation, sector research, structured synthesis, staff review, and visual direction. MCPs/connectors should expose narrow, inspectable operations. Installing every available tool would add failure modes without guaranteeing better intelligence.

A useful brief for Flowith's team would be an evidence export interface: claim IDs, cited source captures, timestamps, collection failures, structured JSON output, bounded jobs, and cost/usage reporting. Confirm their existing capabilities before commissioning it.

## Three-AI evaluation design

Run two separate comparisons: synthesis using the same captured evidence pack, then end-to-end research using each provider's supported tools. The first isolates reasoning and contract compliance; the second measures collection coverage and operating cost. Do not compare them as if they were the same test.

Score factual correctness and citation support first, then coverage, entity matching, uncertainty/conflict handling, freshness, competitor relevance, roadmap usefulness, publication readiness, latency, and cost. Save model/provider versions, prompt, tool configuration, budget, evidence, and outputs. Check unsupported claims even when the prose looks impressive.

Use Vestry as a difficult integration case: it has an affiliated website page, social surfaces, possibly stale information, and unresolved facts. The earlier trial Bible is richer but does not validate against today's production schema; it is a design fixture, not a drop-in replacement. Refresh its claims before using them as benchmark truth. Add a group-only prospect and a prospect with conflicting hours/limited source access to exercise the other failure modes.

## Socialite's signature

Define signature through consistent quality: editorial hierarchy, typography, image direction, transitions, useful contact/booking interactions, and unusually clear mobile layouts. Client identity should determine the palette, voice, imagery, and content structure. The signature should survive different layouts rather than depend on one repeated template.

Start with three art-direction studies for contrasting businesses after the functional slice works. Document shared principles and client-specific choices; then encode reusable components and quality checks. Higgsfield can supply approved visuals or motion, but the site's character also depends on composition, content, performance, and accessibility. No generation credits were used for this audit.

## Verification and limits

Recorded results: [check-results.json](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/docs/audit/2026-10-01/check-results.json). Provisioning harness output: [provision-check.txt](https://github.com/k3ss-official/socialite/blob/520758d9efa27f72106b2b191ed29259f3bcc7b1/docs/audit/2026-10-01/provision-check.txt).

- All five schema definitions were valid; 16 shipped lead files, three Bible files, four pitch files, four build manifests, and 82 event records passed their current schemas.
- After indexing leads in the isolated copy, eight dashboard read routes returned HTTP 200. Local site and pitch generation succeeded and unchanged inputs reused their versions.
- Targeted probes reproduced the index/recovery gap, image 404s, signup duplication, optional-field rendering failure, selected-review rating problem, image cache omission, estimated-cost overrun, sister-site misclassification, unrelated contact extraction, wrong geography/category, and lost social metadata.
- External source/model probes used mocked responses. They demonstrate code paths, not current behavior of those external services. A fresh live deep dive and three-provider comparison remain outstanding.
- The provisioning mock harness stopped with exit 127 because `envsubst` is absent here. Document/install that dependency before rerunning; this result does not establish that VPS deployment is broken. The Claude CLI is also unavailable in this workspace, so live synthesis was not tested.

The next implementation milestone is complete when a staff member can select one prospect, launch a bounded job, review a sourced Bible with visible unknowns, and generate a working preview from approved facts without duplicate jobs, invented ratings, or lost cost history.
