# DEEP-DIVE.md — BIBLE Stage Specification
> Socialite Design pipeline · Stage 2 of 5 (FIND → **BIBLE** → BUILD → PROVISION → UPSELL)
> Purpose: turn one qualified lead into a research bible that (a) fully fuels the BUILD stage and (b) contains a ranked, evidence-backed upsell map that the UPSELL stage extracts rather than generates.
> Version 0.1 · Owner: Tony Whelan (k3ss) · Status: DRAFT

---

## 1. CONTRACT

**Input:** one lead object from `leads/{locale}/leads.json` (FIND output). Minimum required fields: business name, locale, category, at least one social URL, qualification score, no-website evidence.

**Output:**
- `bibles/{lead-id}/bible.md` — human-readable, rep-facing
- `bibles/{lead-id}/bible.json` — machine-readable, pinned schema (§6), consumed by BUILD and UPSELL
- `bibles/{lead-id}/evidence/` — screenshots and captures, referenced by ID

**Budget:** hard cost cap per lead (inherit from PRD, currently $2). Track spend per API/scrape call. Cap hit → finalize with what exists, mark `"complete": false`, move on. Never overspend chasing completeness.

**Runtime cap:** one lead, one pass, no revisits. If a source is unreachable, log it and continue — anti-loop applies (§7).

---

## 2. RESEARCH DOMAINS (the deep dive checklist — all eight, every lead)

### D1 — Identity & contact verification
Confirm trading name, address, phone, email, opening hours across every public source. Flag inconsistencies (NAP mismatches are themselves an upsell finding). Food businesses: pull the FSA rating record (UK) or local equivalent.

### D2 — Social footprint
Every platform they're on: follower counts, posting cadence, last post date, engagement pattern, what content performs. Capture their best-performing photos (URLs + why they work) — these anchor the BUILD.

### D3 — Reviews
Google, Facebook, TripAdvisor as applicable. Volume, average, trajectory, response rate (owner replying or silence?), pull-quotes worth featuring, recurring complaints (a complaint theme = an operational insight = rapport ammunition for the rep).

### D4 — Competitor gap matrix
Top 3 local competitors in the same category. For each: website y/n, online booking/ordering y/n, Google profile claimed + review response y/n, active socials, anything they do online this lead doesn't. Matrix format — every "they have / you don't" cell is a candidate upsell finding.

### D5 — Compliance exposure
Google Business Profile claimed? Allergen information published anywhere (food businesses)? Any fake-review-shaped content on their pages (DMCC exposure)? Privacy basics if they have any web presence at all? Accessibility of existing assets? Each gap is a **premium rung** — liability removal sells hardest to this demographic.

### D6 — Brand voice extraction
From their own posts, replies, and signage photos: tone, vocabulary, local idiom, how they talk about themselves. Output a voice profile the BUILD stage uses verbatim. The site must sound like *them*, not like us.

### D7 — Services & prices
Menu/service list and prices where publicly visible. What they sell that isn't promoted anywhere (catering mentioned once in a FB comment = an unmarketed revenue line = an upsell finding).

### D8 — Visual asset inventory
What usable photography exists (their own posts, tagged photos with rights caution flagged) vs. what BUILD will need generated. Output feeds STYLE-LOCK for the Higgsfield pass. Never inventory third-party photos as usable without a rights note.

---

## 3. EVIDENCE RULES (non-negotiable)

Every claim in the bible carries a receipt: source URL, capture timestamp, and where visual, a screenshot saved to `evidence/` with an ID. The upsell map references evidence IDs, never prose assertions. If a rep says "your competitor outranks you," it must be screenshottable on the spot. No evidence → the finding does not enter the bible. We do not guess about someone's business.

---

## 4. BIBLE.md STRUCTURE (rep-facing, in this order)

1. **Snapshot** — who they are, one paragraph, plus the single strongest reason they'll say yes
2. **Voice profile** — how they talk; how the rep should talk
3. **What's working** — lead with their wins (reviews, best photos, loyal following); the pitch opens with respect, not deficiency
4. **Gap matrix** — the competitor table
5. **Upsell map** — ranked findings (§5)
6. **Watch-outs** — anything awkward: bad review themes, rights-uncertain photos, family disputes visible in comments, signs they've been burned by an agency before
7. **Receipts index** — evidence ID → source → timestamp

---

## 5. UPSELL MAP (the bible's payload)

Each finding is one entry, ranked by `priority`. Framing rule: **headache removed, never feature sold.** The rep reads the `pitch_line` aloud; it must survive being said to a caff owner mid-service.

Rung types (residual ladder alignment):
- `hosting` — rung one, the 12-month anchor, everything hangs off it
- `residual` — recurring managed service (reviews, socials, seasonal campaigns, competitor watch)
- `gift` — one-time build (booking form, menu page, allergen page) priced £0, folded into the residual tier above it — the "and we'll just sort that for you" move
- `compliance` — liability-removal rungs; pitch with calm, never fear ("there's a legal thing — it's handled")
- `upgrade` — scheduled annual refresh (site/social upscale)

Priority scoring (1–100): impact on their business (×4), pain visibility to the owner (×3), ease of delivery (×2), recurring revenue attach (×3). Multiplier 0.5–1.0 for evidence strength — thin evidence discounts priority, same signal-integrity logic as the Bullshit Radar.

---

## 6. BIBLE.JSON SCHEMA (pinned — breaking changes bump the version)

```json
{
  "schema_version": "1.0",
  "lead_id": "scran-away-chorley",
  "generated_at": "ISO-8601",
  "complete": true,
  "cost_spent_usd": 0.00,
  "identity": { "name": "", "address": "", "phone": "", "email": "", "hours": {}, "nap_consistent": true, "fsa": { "rating": 5, "url": "" } },
  "voice_profile": { "tone": "", "vocabulary": [], "idiom_notes": "", "sample_lines": [] },
  "socials": [ { "platform": "", "url": "", "followers": 0, "last_post": "", "cadence": "", "top_content": [] } ],
  "reviews": { "sources": [ { "platform": "", "count": 0, "avg": 0.0, "owner_responds": false, "pull_quotes": [ { "text": "", "evidence_id": "" } ], "complaint_themes": [] } ] },
  "competitors": [ { "name": "", "gaps_vs_lead": [ { "capability": "", "they_have": true, "lead_has": false, "evidence_id": "" } ] } ],
  "compliance": { "gbp_claimed": false, "allergen_info_published": false, "dmcc_risk_flags": [], "evidence_ids": [] },
  "services": [ { "item": "", "price": "", "promoted": false, "evidence_id": "" } ],
  "assets": { "usable": [ { "url": "", "rights": "own|tagged-caution", "why": "" } ], "generation_needed": [] },
  "upsell_map": [
    {
      "finding_id": "F-001",
      "finding": "Google Business Profile unclaimed",
      "evidence_ids": ["E-004"],
      "rung_type": "residual",
      "headache": "People can't find you or see your hours on Google, and you can't answer reviews",
      "pitch_line": "You'll never have to think about Google again — we claim it, fill it, and answer every review in your voice.",
      "priority": 92,
      "evidence_strength": 1.0,
      "delivery": "included-in-managed",
      "recurring": true
    }
  ],
  "watch_outs": [ { "note": "", "evidence_id": "" } ],
  "evidence_index": [ { "id": "E-001", "source_url": "", "captured_at": "", "screenshot": "evidence/E-001.png" } ]
}
```

---

## 7. AGENT RUN RULES

- **One pass, eight domains, in order.** D1 first because identity errors poison everything downstream.
- **Anti-loop:** a source failing twice is dead for this run. Log it in `watch_outs`, move on. Never retry-spiral on a scrape.
- **Stop conditions:** all domains attempted, OR cost cap hit, OR runtime cap hit. Whichever first. Partial bible with `"complete": false` beats no bible.
- **No fabrication, ever.** Empty field > invented field. An invented review quote or price destroys the trust the whole model runs on — and creates the exact DMCC exposure we're selling protection from.
- **Privacy line:** public business information only. No research on owners as private individuals, no personal socials, no directors' home details. We profile the business, not the person.
- **Quality gate before handoff:** bible.json validates against schema; every upsell_map entry has ≥1 evidence_id; top-3 findings have evidence_strength ≥ 0.8. Fail → flag for human review, don't pass garbage to BUILD.
- **Logging:** structured run log per lead (calls made, cost, failures) — Hermes/Phase-2 harness will need these for the self-learning loop later.

---

*v0.1 — validate against Scran Away as golden path, then tune priority weights after the first five real Pokhara bibles.*
