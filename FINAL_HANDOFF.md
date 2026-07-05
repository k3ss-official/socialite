# Final Handoff — field-deployment readiness (branch `claude/sad-nash-d984f3`)

Session date: 2026-07-05. Goal was: make Socialite ready for the first real-money field
deployment without rewriting anything. Done; two live-blocking bugs found and fixed.

## What changed

**Code / config (minimal, no new frameworks, architecture untouched):**

| File | Change | Why |
|---|---|---|
| `socialite/web/overpass.py` | Descriptive User-Agent on Overpass requests | overpass-api.de now 406s generic UAs — `find-locale` (the whole prospecting funnel) was dead on first real use |
| `config/locales/np-pokhara.yaml` | `area_name: "Pokhara, Nepal"` | OSM has no "Pokhara Lakeside" area → silent 0 results |
| `schemas/lead.schema.json`, `socialite/store.py`, `dashboard/app.py`, `dashboard/static/style.css` | New `live` status after `signed` | `signed` = money agreed, `live` = go-live checks passed; the pipeline previously couldn't tell them apart |
| `run.sh` | Fail loud with setup hint when `.venv` missing | Cryptic exec error otherwise |

**Docs (the deliverables):**

- `FIELD_DEPLOYMENT_PLAYBOOK.md` — lead name → live domain + mailbox, exact commands,
  acceptance checks, failure-recovery tables. All VPS/DNS/domain/mailbox/money actions
  marked ⚠ MANUAL.
- `FIRST_3_CLIENTS.md` — targets, offer, scripts, payment, delivery checklist
  (Tony's 2026-07-05 decisions baked in).
- `SPRINT_48H.md` — hour-by-hour first-revenue schedule with gates and failure modes.
- `README.md` — links the above; documents the new status flow.
- `TODO.md` — decisions recorded, blockers updated. `notes/LESSONS.md` — Overpass/OSM lesson.

**Data:** 15 real Chorley leads qualified live by the fixed sweep (free, no LLM), committed
under `data/leads/` — including the four score-90 first-3 candidates.

## Verification run (all on this branch, 2026-07-05)

```sh
bash provision/test_mock.sh                    # → RESULT: 12 passed, 0 failed
.venv/bin/python -m socialite.cli find-locale --locale uk --limit 15
                                               # → 15 leads scored; 4× score 90 website=none
.venv/bin/python -c "import json,jsonschema; s=json.load(open('schemas/lead.schema.json'));
jsonschema.Draft202012Validator.check_schema(s);
jsonschema.validate(json.load(open('data/leads/scran-away-chorley/lead.json')), s)"
                                               # → schema valid, existing artifacts still validate
.venv/bin/python dashboard/app.py &            # then:
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5057/                 # 200
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5057/lead/scran-away-chorley  # 200
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:5057/clients          # 200 (board shows the new live column)
sh -n run.sh && bash -n provision/*.sh         # → syntax ok
```

Pokhara Overpass path verified directly: `find_businesses("Pokhara, Nepal", ...)` → 1,739
businesses (per-business qualification at scale still on TODO, not sprint-blocking).

Not verified (impossible without real infra, by design): live VPS deploy, certbot against
a real domain, real mailbox creation. These are exactly the ⚠ MANUAL steps in the playbook,
and the mock harness covers their logic 12/12.

## How to start the 48h sprint

1. Clear the two human blockers below (VPS + DNS record). Open GoCardless account.
2. `open SPRINT_48H.md` and execute top to bottom — Hour 0–2 preflight gates on the infra,
   Hour 2–5 builds the three prospects (`./run.sh "The Woodsman, Chorley, UK"` etc.,
   ~$3 LLM total), Hour 5–7 deploys demos to `*.demo.k3ss.co.uk`, afternoon is walk-ins.
   Every block has its gate and recovery table; the playbook is the reference behind it.

## Tony must decide / do manually

1. **VPS host + deploy user** — the only true blocker. Nothing provisions live until this
   exists. Prereqs list: playbook §0 (nginx, certbot, rsync, docker-mailserver, ssh key).
2. **Create the DNS record** (after 1): `A` record, host `*.demo`, domain `k3ss.co.uk`,
   value `<VPS-IP>`. Documented in playbook §0; used by sprint hours 0–2/5–7 and the offer script.
3. **GoCardless account** — decided as default rail; needs the account opened before the
   first walk-in. Print 2–3 standing-order mandates as the fallback.
4. Standing decisions already recorded (TODO.md): Woodsman first; Hinds Head/Roebuck/Talbot
   pool; Janine = #4; £49 Foundation, no discounting (month-one-free is the only lever).

## Merge / push recommendation

**Merge to `main` and push: yes, now.** The branch is doc-heavy, code changes are small
and verified, nothing touches live infrastructure, and the lead artifacts are real pipeline
output consistent with how Scran Away is already stored. No migrations, no schema breaks
(existing artifacts validate against the extended enum). Suggested flow:

```sh
git checkout main && git merge claude/sad-nash-d984f3 && git push origin main
```

One judgement call to be aware of before pushing to a public remote: `data/leads/` now
contains scraped qualification evidence for 15 named local businesses and the docs contain
the sales playbook and pricing. If the GitHub repo is (or becomes) public, that's your
competitive playbook in the open — keep the repo private.
