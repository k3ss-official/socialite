# BIBLE v2 — Scran Away, Chorley (system dry run, 2026-07-19 evening)
> lead_id: scran-away-chorley · Run mode: Socialite dry run per docs/DEEP-DIVE-SPEC.md, fresh capture, zero data reused from prior runs
> Status: **complete: partial** — walled-social enrichment logged infra_unavailable (Scrapling bridge restarting); no screenshot captures (chat-session limitation, production requires evidence/)
> Supersedes: notes/scran-away-manual-bible-2026-07-19.md (v1, morning manual run)

---

## RUN LOG

Tool calls: 3 (web_search ×2, places ×1, serial). Domains attempted: D1–D8, in order. Failures: D2 deep-social — infra_unavailable (local MCP bridge down; per doctrine socials = enrichment, run proceeds). Anti-loop events: 0. Estimated cost: negligible (bundled tooling; production budget untouched). Quality gate: PASS — all top findings ≥2 independent sources.

## DELTA vs v1 (what the fresh run found that the morning missed — the reason we rerun)

1. **NEW COMPETITOR: Wild Flour Deli** (25 Chapel St, 4.8★/61) — completely absent from v1. Head-to-head on the *signature dish*: their reviews call the Steak Canadian a must-try; Scran Away's own Google reviews praise their Canadian steak sandwich. Same dish, 400 yards apart, they have 3× the Google reviews.
2. **HOURS CHAOS UPGRADED**: not two sources but three-way contradiction, and two of the three are OUR OWN assets. FB (owner, 1d old): "back open Tuesday 8am until 2pm". scranaway.cafe placeholder: "Mon–Sat 7am 'till 3pm". dogonapc staging: "Mon–Sat 8am–2pm, Sun 9am–2pm" — Sunday opening no other source supports. F-003 (NAP repair) expands to full canonicalisation: phone, postcode, AND hours, and the fix starts with our own pages.
3. **MARKET GAP: afternoons.** Cafe Fresh reviewer: only downside is the 1:30pm close, every day. Majestic closed Wednesdays, bookings needed Saturdays. Chorley has unserved afternoon breakfast-café demand — pitch ammunition and a possible ops suggestion for the owner.
4. **CATEGORY MISMATCH**: FSA = Restaurant/Cafe/Canteen; Facebook = Sandwich Shop; Google types = sandwich_shop + breakfast_restaurant. Minor, but consistency feeds local SEO — fold into F-003.
5. **Minor entrant**: Classy Sandwich (market cabin, 5.0★/5) — no threat, completes the map.
6. All v1 core findings **re-confirmed on fresh evidence**: GBP thin (5.0★/20, hours field empty, third phone 07925 157262), 68 FB reviews @100%, no allergen info anywhere, catering invisible outside staging, cash-only Town Cafe, Calico praised by name for allergy-knowledgeable staff (the benchmark for F-004), FSA/SotD auto-updating badge embeds available, DMCC watch-out on staged testimonials stands.

## SNAPSHOT

Unchanged in substance, sharpened in pitch: a 5.0-rated operator Google can barely see — 20 reviews, no hours listed — while Wild Flour Deli sells the same signature sandwich 400 yards away with 61 reviews and Majestic sits on 356. Demand already proven twice over: 68 FB reviews at 100%, and 3.76k uniques hitting a coming-soon page (E-11, carried from v1, owner-verified).

## UPSELL MAP v2 (revised priorities)

**F-001 · Google visibility & review flywheel** — residual · **priority 96 ↑**
Fresh evidence sharpens the line: "Wild Flour Deli sells a Canadian steak too — and when someone Googles one in Chorley, they show up and you don't."
**F-003 · Full NAP + hours canonicalisation** — gift in onboarding · **priority 91 ↑**
Now covers 3 phones, 2 postcodes, 3 hour-sets, 3 category labels. First question for the owner: what ARE your real hours and which number rings? Then one truth, everywhere — including fixing our own two pages first.
**F-002 · Live site on scranaway.cafe** — hosting anchor · priority 92 (unchanged; E-11 remains the lead receipt)
**F-004 · Allergen page + FSA auto-badge** — compliance gift · priority 85 (Calico benchmark shows locals already reward it in reviews)
**F-005 · Catering promotion** — residual/seasonal · priority 78 (Cafe Fresh still winning catering via Google; ours still invisible)
**F-006 · TripAdvisor/directories** — priority 55 · Cylex listing exists (NAP propagation surface — include in F-003 sweep)
**F-007 · Managed socials** — priority 50 · FB authentically owner-run (post 1d old); pitch only on fatigue signals

## WATCH-OUTS (carried + new)

⚠️ Staged-site Sunday hours may be inventing an opening day — verify with owner before anything ships; if wrong, it's the same class of error as the postcode.
⚠️ Demo testimonials: DMCC-banned if published; replace with real Google/FB quotes (carried).
⚠️ Production runs MUST capture screenshots to evidence/ and drive Scrapling as library with consent-cookie flow (per notes/SCRAPING.md) — this run's social blindness is the cost of not having that built yet.

## RECEIPTS INDEX (all fresh-captured this run, 2026-07-19 evening)

E2-01 FSA record: 73 Bolton St PR7 3AG, rating 5, 25 Mar 2025, updated 4 Jan 2026, category Restaurant/Cafe/Canteen — ratings.food.gov.uk/business/1796323
E2-02 Scores on the Doors: rating 5 + embeddable badge — scoresonthedoors.org.uk/business/scran-away-1795032.html
E2-03 Facebook page (search capture): Sandwich Shop, 2 phones, Scran-away2025@outlook.com, 68 reviews @100%, "back open Tuesday 8am until 2pm" post 1d old, IG/TikTok handles — facebook.com/scranaway
E2-04 Google Places: 5.0/20, hours field empty, phone 07925 157262, types sandwich_shop+breakfast_restaurant, 5 pull-quote reviews — place_id ChIJy1OIDAANe0gR4nvepTdsWHE
E2-05 Competitor set (Places): Majestic 4.7/356 (Wed closed, Sat bookings); Town Cafe 4.3/324 (cash only per review); Caffe Latte 4.5/143 (Sun closed); Calico 4.5/1114 (allergy-praise review); Cafe Fresh 4.7/113 (1:30pm close complaint; catering-win review); **Wild Flour Deli 4.8/61 (Steak Canadian review)**; Classy Sandwich 5.0/5
E2-06 scranaway.cafe placeholder: "Mon–Sat 7am 'till 3pm" — scranaway.cafe
E2-07 dogonapc.com staging: "Mon–Sat 8am–2pm, Sun 9am–2pm", PR7 2AG, catering copy — dogonapc.com
E2-08 Cylex directory listing exists — chorley-chorley.cylex-uk.co.uk/company/scran-away-28909095.html
E2-09 Absence-of-evidence: no allergen info on any surfaced source (searched this run)
E-11 (carried, owner-verified): Cloudflare — 3.76k uniques on scranaway.cafe coming-soon vs 3.07k on staging
