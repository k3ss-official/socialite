# Socialite — Sprint Board

Living board. Maintained by the build agent; humans welcome to edit.

## Done
- [x] Repo scaffold, venv, deps
- [x] Data contracts pinned (schemas/) + validation on every artifact write
- [x] Core pipeline: find → research → bible → build → pitch (CLI + programmatic)
- [x] FIND proven live on Scran Away (score 80–90, evidence-backed template verdict, FB/IG/phone/email recovered)
- [x] RESEARCH trust-ordered harvest proven live (own site + socials + directories, 8 real photos)
- [x] BIBLE v1 for Scran Away — session-fallback synthesis (claude CLI auth was down; see Blocked)
- [x] Site theme `classic` — built + screenshot-verified mobile & desktop
- [x] PITCH sheet w/ rep-briefing alerts (caught the May-2026 closure announcement)
- [x] Dashboard: board, lead detail, bible/pitch viewers, site preview, sign flow, client ledger, MRR + attrition projection — all routes curl-verified with real data
- [x] Provisioning: deploy + mailbox + orchestrator, mock harness 12/12 passing, dry-run proven side-effect-free
- [x] Idempotent re-runs: hash-based reuse, forward-only statuses, evidence merge across search variance
- [x] Acceptance test: `./run.sh "Scran Away, Chorley, UK"` end to end
- [x] Canonical LLM path proven: bible v4 via `claude -p` ($0.90, 5min) — alerts caught postcode error in our own demo, hours conflict, 4 real competitors
- [x] Nested-agent guard: `claude -p` runs with mutating tools disabled from /tmp (it wrote a rogue bible into the repo once — quarantined, logged)
- [x] `find-locale --locale uk` field-proven: Overpass 406 fixed (descriptive UA), live Chorley sweep returned 4 score-90 no-website leads
- [x] `live` status after `signed` (schema + store + dashboard) — go-live is now tracked, not implied
- [x] Field docs: FIELD_DEPLOYMENT_PLAYBOOK.md, FIRST_3_CLIENTS.md, SPRINT_48H.md

## Blocked on Tony
- [ ] Real VPS details (host, deploy user) — nothing live provisions until confirmed
- [ ] Create the demo wildcard DNS record once VPS is confirmed: `A *.demo k3ss.co.uk → <VPS-IP>` (exact record + usage documented in FIELD_DEPLOYMENT_PLAYBOOK.md §0)
- [ ] Open the GoCardless account (decided: default rail; paper standing-order mandate is the old-school fallback only)

## Decided (Tony, 2026-07-05)
- [x] Payment rail: GoCardless default, standing-order fallback
- [x] Demo domain: `*.demo.k3ss.co.uk` (record not yet created)
- [x] First-3 order: The Woodsman first; Hinds Head, Roebuck Inn, Talbot active pool
- [x] Janine/Scran Away relaunch = pipeline #4 unless manually overridden
- [x] Offer: £49/mo Foundation, no discounting — first month free is the only lever

## Next
- [ ] Run pipeline on the 3 Chorley candidates (The Woodsman, Hinds Head, The Roebuck) — SPRINT_48H.md hour 2–5
- [ ] Field-test `find-locale --locale np-pokhara` at scale (UK sweep proven; Pokhara Overpass area fixed — "Pokhara, Nepal" resolves 1.7k businesses incl. tourism tags — per-business qualification not yet run)
- [ ] Per-locale palette/typography hints in locale packs (Pokhara aesthetic ≠ Lancashire)
- [ ] Second site theme once 3+ clients are live (avoid same-template smell in one town)
- [ ] WhatsApp CTA end-to-end test with a NP number

## Phase 2 (designed-for, NOT built)
- Autonomous recurring delivery per rung (campaigns, monitoring, refreshes) driven by an external orchestrator through the existing stage interfaces
- Human-in-the-loop approval gates, standards/drift monitoring
- Service ledger `schedule`/`state` columns are reserved and already populated minimally
