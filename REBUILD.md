# REBUILD.md — Socialite Replication & Disaster-Recovery Playbook
> **Purpose:** patent-style enablement. Anyone — or any capable agent — holding this repo and this document can rebuild the entire Socialite system from bare metal and operate it. If everything falls over, feed this file to a frontier coding agent (Claude Code or equivalent) at the repo root and instruct: *"Rebuild and verify this system per REBUILD.md."*
> Owner: Tony Whelan (k3ss) · Created 2026-07-19 · Keep current or it's worthless.

---

## 0. WHAT THIS SYSTEM IS

Socialite finds small hospitality businesses with no website, researches them into an evidence-backed "bible," auto-builds them a branded landing page, reveals it to them already-live, and converts them onto recurring managed services. Five pipeline stages — FIND → BIBLE → BUILD → PROVISION → UPSELL — implemented in this repo, driven by `run.sh`, monitored via the dashboard, every action logged to `events.jsonl`.

**Commercial model (the three-door close):** the free landing page is the hook, built before first contact. Door 1: managed service, monthly residual (the target outcome; ladder in `config/ladder.yaml`). Door 2: licence the code, £1,000/yr, frozen-as-delivered (no updates — deliberate upgrade pressure back toward managed). Door 3: buy outright, £5,000. A "no" costs only minutes of agent time and the build feeds the template library.

**Target demographic:** technophobe operators with active Facebook but no website — "just make it work" buyers who pay for headaches to disappear. All pitches are framed as headaches removed, never features sold.

---

## 1. SYSTEM INVENTORY (what must exist for the business to exist)

| Asset | Location | Recovery source |
|---|---|---|
| Canonical repo | `/Volumes/deep-1t/Users/k3ss/k3ss-official/socialite` | github.com/k3ss-official/socialite (main) |
| GitHub remote | github.com/k3ss-official/socialite | local clone; GDrive mirrors |
| Domains + DNS | Cloudflare (free plan): socialite.design targets, dogonapc.com (staging), scranaway.cafe (client #1), demo wildcard | Cloudflare account; registrar |
| Client sites | VPS (provision/ scripts define it) + Cloudflare | rebuildable from repo templates + bibles |
| Historic archives | `/Volumes/hotblack-2tb/Archive/project-curation/2026-05-18/socialite-cluster/` + `projects/_SUPERSEDED-socialite-20260719/` | read-only; safe to lose |
| GDrive mirrors | cheeky-scouser acct: socialite-design folder | secondary backup only |
| Session artefacts | `docs/` + `notes/` in repo | in repo — that's the point |

**Credentials needed to operate** (never stored in repo; held in 1Password): GitHub, Cloudflare (API token: DNS edit), VPS root SSH, Anthropic API / Claude subscription, payments provider (GoCardless account exists; re-evaluate at restart), domain registrar, Higgsfield account (asset layer), client mailbox provider.

---

## 2. COLD REBUILD — ORDER OF OPERATIONS

1. **Machine:** any macOS/Linux box. Install: git, Python 3.11+, `claude` CLI (authenticated), 1Password CLI.
2. **Clone:** `git clone https://github.com/k3ss-official/socialite && cd socialite`. If GitHub is gone, restore from local clone or GDrive mirror, then re-create the remote.
3. **Environment:** `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`.
4. **Config:** review `config/settings.yaml` (hard cost cap per lead — currently $2 — model names, locale) and `config/ladder.yaml` (the offer — keep aligned with §0's three-door model).
5. **Golden path:** `./run.sh --city chorley` (or current invocation per README). Expect: leads found → pick Scran Away → bible generated → site built → pitch generated. Scran Away is the permanent golden-path fixture; its known-good outputs are in `notes/` and git history.
6. **Verify (all must pass):** lead JSON validates against `schemas/`; bible validates + passes quality gate (every upsell finding evidenced); built site renders locally; `events.jsonl` receiving events; total spend ≤ cap; dashboard loads.
7. **Provision:** follow `FIELD_DEPLOYMENT_PLAYBOOK.md` verbatim — VPS, DNS, SSL, mailbox. VPS/DNS/money steps are **manual by design**; do not automate approvals away.
8. **Research layer upgrades** (§4) and **asset layer** (§5) as needed — the core pipeline runs without them.

A competent agent given steps 1–6 should reach a verified golden path in under an hour.

---

## 3. GOVERNANCE (non-negotiable, survives any rebuild)

- **Evidence-first:** no claim about a business without a receipt (URL + timestamp, screenshots in production). No fabrication ever — an invented review quote creates the DMCC liability we sell protection against. Empty field beats invented field.
- **Privacy line:** research the business, never the owner as a private individual.
- **Cost caps are law:** per-lead cap in settings; agent stops at cap, marks partial, moves on.
- **Anti-loop:** same failure twice = dead source/direction for the run; bisect the cause, never re-roll the symptom.
- **Approval gates:** anything that spends real money, touches DNS/VPS, contacts a client, or publishes — human approves. An unguarded `claude -p` once wrote a rogue bible mid-run (see git history, June 11); tool lockdown exists for a reason.
- **Compliance is product:** allergen page, DMCC-safe reviews, NAP consistency ship with every client. See `docs/DEEP-DIVE-SPEC.md` §D5.

---

## 4. RESEARCH LAYER DOCTRINE

Authoritative field notes: `notes/SCRAPING.md` (including 2026-07-19 addendum). Summary: Google Places + FSA + search snippets carry a quality-gated bible **without** walled socials — socials are enrichment, not dependency. Scrapling is driven **as a library** in pipeline code (page_action consent-decline once, persist cookies); its MCP wrapper is recon-only. Stealthy browser fetches run **serial**. Planned components: self-hosted Open Notebook (lfnovo/open-notebook) as the RESEARCH→BIBLE synthesis engine (replaces any NotebookLM/Google dependency — client research data stays on our metal); `last30days` skill as the **managed-loop heartbeat** — the monthly "what was said about you and your competitors" report that justifies the residual and feeds competitor-watch rungs.

---

## 5. ASSET LAYER (visuals)

Governed by `docs/CREATIVE-DIRECTOR-SOUL.md`: a Creative Director agent drives Higgsfield via MCP under a taste rubric, four approval gates, credit-budget-as-law, and style-lock consistency. Per-client context files (BRAND / PROJECT / STYLE-LOCK / MEMORY) are generated from the bible. First production use case: replacing stock imagery with on-brand generated assets matched to the client's real photography (Scran Away catering section is the standing example).

---

## 6. AGENT ROSTER (dedicated — built on the Hermes agent framework)

Socialite runs its **own** agents, documented here, per Hermes conventions (SOUL.md / AGENTS.md / USER.md / MEMORY.md each). House/system agents (Rae, Janet, Trillian, Slarty) are separate personal infrastructure and are **out of scope** — never conscript them.

| Agent | Role | Stages |
|---|---|---|
| Scout | prospecting + research collection | FIND, RESEARCH |
| Librarian | synthesis + bible authorship (Open Notebook) | BIBLE |
| Builder | site generation from bible + templates | BUILD |
| CD | asset direction per CREATIVE-DIRECTOR-SOUL | BUILD assets, campaigns |
| Steward | managed-service loop, last30days reports, review responses | post-sale |
| Sentinel | QA gates, schema validation, events.jsonl watch, cap enforcement | all |

Roster is design-intent as of 2026-07-19; write each agent's governance files before first autonomous run. Until then, a single Claude Code session at repo root performs all roles under human gates — which is also the minimum-viable recovery mode.

---

## 7. RECOVERY MATRIX

| Lost | Action |
|---|---|
| The Mac | Any machine + §2. Nothing business-critical lives only on local disk. |
| GitHub | Re-push from local clone (or GDrive mirror). Re-point remotes. |
| VPS | Re-provision per FIELD_DEPLOYMENT_PLAYBOOK; client sites rebuild from repo + bibles. |
| Cloudflare account | Registrar → new DNS host; re-create zones; certs reissue. Client domains are the crown jewels — keep registrar access airtight. |
| Everything digital | GDrive mirror or hotblack archive → §2 from step 2. |
| The founder's context | This file + repo docs + git history ARE the context. That's why this document exists. |

---

## 8. CURRENT STATE MARKER (update on every material change)

**As of 2026-07-19 (evening):** MVP pipeline implemented and golden-pathed (June 11). Pre-pivot field docs removed at `6a5bc19` — recoverable from history; superseded by the three-door model, **door 1 monthly pricing TBD**. Client #1 (Scran Away, Chorley): site staged (dogonapc.com), client domain live as coming-soon (scranaway.cafe, ours, 3.76k uniques pre-launch), bible v2 current in notes/ (fresh system dry run — see delta section for why reruns beat cached data), reveal meeting not yet held. Scrapling installed + field-tested (consent-wall + concurrency lessons in notes/SCRAPING.md); Open Notebook and last30days not yet integrated; CD/Higgsfield harness spec'd, connector being wired; dedicated agent roster spec'd (§6), not yet built. First market after Chorley proof: Pokhara, Nepal.
