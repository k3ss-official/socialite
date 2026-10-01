# Socialite

Internal pipeline for **Socialite Design**: find small hospitality businesses living on a
Facebook page with no real website → research them deeply → build them a hand-crafted
landing page → arm a sales rep with a pitch sheet built on a residual ladder → deploy on
our own VPS and track the client's recurring services.

## Staff research workflow

Use the dashboard and local worker for **select prospect → collect → Bible v2 → staff
review → preview and proposal**. Expanded collectors, three-provider benchmarking and
the signature design system remain subsequent work.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python dashboard/app.py
```

Open http://127.0.0.1:5057, select a prospect and start research. In a second terminal:

```sh
claude --version
.venv/bin/python -m socialite.cli worker
```

Live synthesis needs a working, logged-in Claude CLI. Other providers are not integrated
yet. The dashboard is local only and records self-reported staff names; keep it on loopback.

Bible v2 exposes coverage, claim receipts, unknowns/conflicts, roadmap and image permission
review. **Open printable report** uses the supplied example's structure; **Print / save as
PDF** exports from your browser. Existing Bible v1 viewers and builds remain available.

See [M4 setup and recovery](docs/WORKFLOW-QUICKSTART.md),
[Bible v2 contract](docs/BIBLE-V2.md), and the [baseline gap analysis](docs/GAP-ANALYSIS.md).

## Legacy one-command run

```sh
./run.sh "Scran Away, Chorley, UK"          # uk locale (default)
./run.sh "Moondance Cafe, Pokhara" np-pokhara
```

That single command runs **FIND → RESEARCH → BIBLE → BUILD → PITCH** plus a **dry-run of
provisioning**, then prints the local preview path, artifact paths, per-lead spend, and the
dashboard URL. Research uses a freshness window. This legacy path creates the original
Bible format and does not provide the new staff review step. Use the dashboard for Bible v2.

First-time setup:

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
claude --version   # the bible stage shells out to the local claude CLI (must be logged in)
```

Dashboard (lead board, bible/pitch viewers, live site previews, client ledger + MRR):

```sh
.venv/bin/python dashboard/app.py    # → http://127.0.0.1:5057
```

## Field deployment

Going from a lead to a paying client with a live site is documented step by step in
**[FIELD_DEPLOYMENT_PLAYBOOK.md](FIELD_DEPLOYMENT_PLAYBOOK.md)** — lead name → live
domain + mailbox: exact commands, acceptance checks, failure recovery. VPS/DNS/money
steps are manual by design.

> 2026-07-19: pre-pivot field docs (FIRST_3_CLIENTS, SPRINT_48H, HANDOFF, FINAL_HANDOFF,
> TODO) removed — superseded by the three-door offer model and CD-harness asset layer
> (see docs/). Recoverable from git history if needed.

Lead statuses run `found → bible → built → pitched → signed → live` (plus `rejected`);
`signed` means money agreed, `live` means all go-live acceptance checks passed.

## Pipeline stages

| Stage | Module | Output (versioned, reproducible) |
|---|---|---|
| FIND | `socialite/stages/find.py` | `data/leads/<id>/lead.json` — score + evidence for "no real website" |
| RESEARCH | `socialite/stages/research.py` | `data/leads/<id>/raw/` — pages, images, search results (free, requests-only) |
| BIBLE | `socialite/stages/bible.py` | `data/leads/<id>/bible/v<N>.json` — brand voice, palette, reviews, competitor gap matrix |
| BUILD | `socialite/stages/build.py` | `data/leads/<id>/site/v<N>/` — static bundle + build manifest |
| PITCH | `socialite/stages/pitch.py` | `data/leads/<id>/pitch/v<N>.{json,html}` — gaps mapped to the residual ladder |
| PROVISION | `provision/*.sh` | nginx vhost + SSL + branded mailbox on the VPS (`--dry-run` / `--mock` tested) |

Each stage is callable individually (`python -m socialite.cli find|research|bible|build|pitch <args>`)
and programmatically — the Phase 2 orchestrator drives the same functions.

Locale-scale discovery: `python -m socialite.cli find-locale --locale np-pokhara --limit 25`
(OpenStreetMap/Overpass sweep for businesses without website tags, then per-business qualification).

## The contracts

`schemas/*.schema.json` pin the data shapes between stages — every artifact is validated on
write. `data/events.jsonl` logs every pipeline action (machine-readable, Phase 2 food).
Costs: reported LLM usage is logged per lead; a preflight gate refuses actions whose
estimated cost exceeds the remaining `cost_cap_usd_per_lead` ($2 default).
Actual provider billing can exceed an estimate; this is not a guaranteed hard billing cap.

## The business config

- `config/ladder.yaml` — the residual ladder: rungs (recurring services), zero-priced gift
  builds folded into rungs, named tiers a rep sells in one conversation, and the canonical
  gap keys with say-it-out-loud sell lines.
- `config/locales/*.yaml` — everything market-specific is data: language, currency, contact
  channel (WhatsApp vs phone vs forms), price bands per rung, discovery seeds. UK and
  Pokhara ship today; a new market is a new YAML file.

## Key choices (one line each)

- **Python + Flask + SQLite + JSON artifacts on disk** — lead/event indexes recover from files; clients, services and jobs are durable SQLite data and need database backups too.
- **Static site output** — zero runtime, deploys anywhere nginx points at a folder.
- **`claude -p` as synthesis engine** — needs local installation and login; access/billing depend on that account, and reported usage supports spend tracking.
- **ddgs (DuckDuckGo) + Overpass for discovery** — free, keyless, no quota accounts to babysit.
- **No LLM in the pitch stage** — sell lines are vetted config; reps get consistency and the cost is zero.

## Phase 2 (designed for, not built)

Recurring delivery (campaigns, competitor monitoring, seasonal pushes, annual refreshes)
will be driven by an external orchestrator. The MVP already provides: versioned artifacts
reproducible from `inputs_hash`, structured event logging, a service ledger with per-rung
`schedule`/`state` JSON columns reserved, and clean programmatic stage interfaces. Nothing
in Phase 2 requires a rewrite.

## Repo map

```
run.sh                  one-command pipeline
socialite/              python package (cli, stages/, web/, store, llm, contracts)
schemas/                pinned stage contracts (JSON Schema)
config/                 settings, residual ladder, locale packs
templates/site/classic/ the landing-page theme (Jinja2)
templates/pitch/        pitch-sheet template
dashboard/              Flask internal dashboard
provision/              VPS deploy scripts + mock test harness
prompts/                LLM prompt templates (versioned — they feed inputs_hash)
notes/                  LESSONS.md + SCRAPING.md field notes
data/                   leads, artifacts, events.jsonl, sqlite (partly gitignored)
```
