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

## Blocked on Tony
- [ ] `claude /login` on this machine — then `python -m socialite.cli bible scran-away-chorley --force` to regenerate the bible through the CLI path (current v1 was synthesized in-session, same contract)
- [ ] Real VPS details (host, deploy user) for first live provisioning run
- [ ] Decision: Scran Away closed 27 May 2026, relaunch planned — pitch the relaunch or pick a second UK test client?

## Next
- [ ] Field-test `find-locale --locale np-pokhara` (Overpass sweep is implemented, not yet run at scale)
- [ ] Per-locale palette/typography hints in locale packs (Pokhara aesthetic ≠ Lancashire)
- [ ] Second site theme once 3+ clients are live (avoid same-template smell in one town)
- [ ] WhatsApp CTA end-to-end test with a NP number

## Phase 2 (designed-for, NOT built)
- Autonomous recurring delivery per rung (campaigns, monitoring, refreshes) driven by an external orchestrator through the existing stage interfaces
- Human-in-the-loop approval gates, standards/drift monitoring
- Service ledger `schedule`/`state` columns are reserved and already populated minimally
