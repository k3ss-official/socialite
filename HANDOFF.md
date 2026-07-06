# HANDOFF — Socialite

For the next agent. Read this, then `TODO.md` and `notes/LESSONS.md`.

## 1. What is Socialite

Internal sales/build pipeline for **Socialite Design**. It finds small hospitality businesses that live on a Facebook page with no real website, researches them, auto-builds a hand-crafted static landing page, and produces a rep-facing pitch sheet mapped to a "residual ladder" of recurring services. Deployment targets our own VPS; the dashboard tracks leads through to signed clients and MRR.

## 2. Tech stack

- **Python 3.12**, plain venv. Deps: `requests`, `beautifulsoup4`, `jinja2`, `flask`, `pyyaml`, `jsonschema`, `ddgs` ([requirements.txt](requirements.txt))
- **Flask + SQLite** for the internal dashboard (SQLite is just an index; JSON artifacts on disk are the source of truth)
- **Jinja2** static site templates (no frontend framework — output is a zero-runtime static bundle)
- **`claude -p` CLI** as the LLM synthesis engine (BIBLE stage); DuckDuckGo (`ddgs`) + OSM Overpass for free, keyless discovery
- **Bash** provisioning scripts (nginx vhost + SSL + mailbox) with a mock test harness

## 3. Repo structure

- [run.sh](run.sh) — one-command full pipeline
- `socialite/` — the package: [cli.py](socialite/cli.py), [store.py](socialite/store.py) (SQLite + artifacts), [llm.py](socialite/llm.py) (claude -p wrapper + cost cap), [contracts.py](socialite/contracts.py) (schema validation), `stages/` (find, research, bible, build, pitch), `web/` (search, sitecheck, overpass helpers)
- `schemas/` — JSON Schema contracts; every artifact validated on write
- `config/` — [settings.yaml](config/settings.yaml) (incl. `cost_cap_usd_per_lead`, $2), [ladder.yaml](config/ladder.yaml) (residual ladder + sell lines), `locales/` (uk.yaml, np-pokhara.yaml — new market = new YAML)
- `templates/site/classic/` — landing-page theme; `templates/pitch/` — pitch sheet
- `dashboard/` — Flask app ([app.py](dashboard/app.py))
- `provision/` — VPS deploy/mailbox scripts + `test_mock.sh`
- `prompts/` — versioned LLM prompts (feed `inputs_hash`)
- `data/` — leads, artifacts, `events.jsonl`, `db.sqlite` (partly gitignored)
- `notes/` — LESSONS.md, SCRAPING.md field notes

## 4. What's been built (all working, verified)

- Full pipeline FIND → RESEARCH → BIBLE → BUILD → PITCH, per-stage CLI and programmatic
- Proven live end-to-end on one real lead: **Scran Away, Chorley UK** (`data/leads/scran-away-chorley`)
- BIBLE via `claude -p` proven (v4, $0.90, ~5min) with rep alerts (caught a closure announcement, hours conflicts, competitor gaps)
- Dashboard: lead board, lead detail, bible/pitch viewers, site preview, sign flow, client ledger, MRR + attrition projection — all routes curl-verified
- Provisioning: mock harness 12/12 passing, dry-run side-effect-free (never run against a real VPS)
- Idempotent re-runs: `inputs_hash`-based reuse, forward-only statuses, cost cap kill switch, event log (`data/events.jsonl`)
- Nested-agent guard: `claude -p` runs from /tmp with mutating tools disabled (it once wrote a rogue file into the repo)

## 5. Current status

- Branch: `main`, clean, in sync with `origin/main` (HEAD `66620d1`)
- **Worktree `.claude/worktrees/sad-nash-d984f3` is on branch `claude/sad-nash-d984f3`, 3 commits ahead of main, NOT merged.** It contains field-deployment work: `FINAL_HANDOFF.md`, `FIELD_DEPLOYMENT_PLAYBOOK.md`, `FIRST_3_CLIENTS.md`, `SPRINT_48H.md`, an Overpass 406 fix + Pokhara area fix, a `live` lead status, and Tony's baked-in decisions (demo domain `*.demo.k3ss.co.uk`, GoCardless default, no-discount rule). **Review/merge this branch first — it supersedes parts of main's docs.**
- No open PRs known. No test suite beyond `provision/test_mock.sh`; acceptance test is `./run.sh "Scran Away, Chorley, UK"`
- Runnable right now: `.venv` exists, data for one lead present

## 6. Broken / incomplete

- BIBLE stage requires a logged-in local `claude` CLI; nested `claude -p` from an agent session 401s (see memory/LESSONS)
- `find-locale` Overpass sweep implemented but never run at scale (Pokhara field test pending; 406 fix lives on the worktree branch)
- Provisioning never executed against a real VPS — only mock/dry-run
- Only one site theme (`classic`); same-template smell risk with multiple clients in one town
- Test lead complication: Scran Away announced closure 27 May 2026 (relaunch planned) — pitch target decision pending

## 7. What's next (from TODO.md)

- **Blocked on Tony:** real VPS host/deploy-user for first live provisioning; decide Scran Away relaunch pitch vs. new UK test client
- Merge/reconcile the `claude/sad-nash-d984f3` worktree branch into main
- Field-test `find-locale --locale np-pokhara` at scale
- Per-locale palette/typography hints in locale packs
- WhatsApp CTA end-to-end test with an NP number
- Second site theme once 3+ clients live
- Phase 2 (recurring delivery orchestrator) is designed-for, not built — stage interfaces, versioned artifacts, and ledger schedule/state columns already support it

## 8. How to run

```sh
# setup (once)
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
claude --version   # bible stage shells out to local claude CLI, must be logged in

# full pipeline on one business
./run.sh "Scran Away, Chorley, UK"           # uk locale default
./run.sh "Moondance Cafe, Pokhara" np-pokhara

# individual stages / discovery / status
.venv/bin/python -m socialite.cli find|research|bible|build|pitch <args>
.venv/bin/python -m socialite.cli find-locale --locale np-pokhara --limit 25
.venv/bin/python -m socialite.cli status

# dashboard → http://127.0.0.1:5057
.venv/bin/python dashboard/app.py

# provisioning mock tests
provision/test_mock.sh
```

There is no separate frontend build — the dashboard serves everything; built sites are static bundles under `data/leads/<id>/site/v<N>/`.

## 9. Key files

- Entry points: [run.sh](run.sh), [socialite/cli.py](socialite/cli.py) (`cmd_run` at line 25), [dashboard/app.py](dashboard/app.py) (routes: `/`, `/lead/<id>`, bible/pitch viewers, `/preview/<lead_id>/<v>/`, `/clients`, `/events`; port from `settings.yaml` → 5057)
- Config: [config/settings.yaml](config/settings.yaml), [config/ladder.yaml](config/ladder.yaml), `config/locales/*.yaml`
- LLM boundary: [socialite/llm.py](socialite/llm.py) + `prompts/` (prompt text is versioned and hashed into artifacts)
- Data contracts: `schemas/*.schema.json`, enforced in [socialite/contracts.py](socialite/contracts.py)
- Field knowledge: `notes/LESSONS.md`, `notes/SCRAPING.md`, and the worktree's `FINAL_HANDOFF.md` / `FIELD_DEPLOYMENT_PLAYBOOK.md`
