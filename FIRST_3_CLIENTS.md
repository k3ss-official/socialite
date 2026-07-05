# First 3 Clients

Objective: **3 signed Foundation clients in Chorley** (£49/mo each ≈ £147 MRR, ~£1,750/yr)
using the pipeline as proof-of-work. Everything below is derived from real pipeline output —
the candidates were qualified live by `find-locale` on 2026-07-05.

## Target profile

- Hospitality (pub / cafe / takeaway / restaurant) in one town — Chorley — so demos,
  walk-ins, and word-of-mouth compound.
- **Active Facebook page, no real website** (FIND verdict `none`, `dead`, or `template`;
  score ≥ 80). The page proves they care about being found; the missing site is the gap.
- Owner-operated. One decision-maker, one conversation.
- **Trading right now.** Bible `alerts` must be clean (Scran Away taught us: verify before
  you walk in).

## Live candidates (qualified 2026-07-05, all score 90, verdict `none`)

| Lead id | Business | Evidence |
|---|---|---|
| `the-woodsman-chorley` | The Woodsman (Leyland/Chorley) | FB page **with menu** + Instagram — most digitally active, best first target |
| `hinds-head-chorley` | Hinds Head, Charnock Richard | FB page, phone 01257 792430 recovered |
| `the-roebuck-chorley` | The Roebuck Inn, Whittle-le-Woods | FB page, address recovered |
| `the-talbot-chorley` | The Talbot, Chorley | FB presence weaker (video link only) — pitch last in the pool |

Wildcard option: **Janine's Scran Away relaunch** (see `scran-away-chorley` bible v4
alerts). Warm-ish, we already have full research, but the business doesn't exist yet —
treat as pipeline #4, not one of the first 3. Re-engagement alert applies: reference the
old pitch, don't walk in cold.

Refill the funnel any time (free): `.venv/bin/python -m socialite.cli find-locale --locale uk --limit 25`

## The offer

> "I build websites for [town] food businesses. I already built yours — it's live, look."
> *(hand them your phone showing `https://<id>.demo.k3ss.co.uk`)*
> "The site is free — it's yours as long as you're hosted with me. £49 a month covers
> hosting, SSL, a proper `you@yourpub.co.uk` email, and me personally updating your hours,
> menu, and photos whenever you message me. No contract tricks: 12 months, then rolling."

The gift structure is the ladder working as designed: the build costs us minutes; the
monthly is the product.

## Price ladder (UK locale pack — rep discretion inside bands)

| Rung | Band | First-3 anchor |
|---|---|---|
| Foundation (host+SSL+email+edits, free site) | £39–59 | **£49** |
| Social Launch (profiles rebuilt + 4 posts/mo) | £99–149 | £99 upsell after month 1 |
| Social Growth / Pro, Competitor Watch, Seasonal, Upscale | per `config/ladder.yaml` | don't lead with these |

Close Foundation only. Upsell rungs at the 30-day check-in with the first traffic numbers.
Discipline: **no discounting, ever** — the price is £49. If a close needs a release valve,
give the first month free instead: costs pennies, protects the MRR anchor.

## Outreach

Walk-in beats everything in a small town, 2–4pm lull. Sequence per candidate:

1. **Prep** (desk): run `./run.sh "<name>, Chorley, UK"`, clear the alerts, deploy demo to
   the wildcard subdomain, print the pitch sheet, load the demo on your phone.
2. **Walk in**, ask for the owner. If absent, get their name + when they're in; leave
   nothing (the demo is the hook — don't burn it on staff).
3. **Show, don't pitch**: phone in their hand within 30 seconds. The pitch sheet's gap
   lines (their reviews invisible, page quiet, no menu online) do the arguing.
4. **Close**: sign form is in the dashboard on your laptop; payment instruction on the
   spot (below). If "let me think": leave the pitch PDF, book a specific return day.

FB Messenger fallback (owner unreachable in person):

> Hi [name] — I'm local, I build websites for Chorley food businesses. I already made one
> for [business] so you can see it working, not a mockup: [demo link]. It's free with
> hosting at £49/mo — email/DM me or I'll pop in [day]. — Tony, Socialite Design

## Proof needed (in this order of power)

1. **Their own site, live, on your phone** — built from their real photos and reviews.
2. Pitch sheet with named local competitors who have what they lack.
3. Scran Away demo as portfolio ("I built this for another Chorley business").
4. After client #1: "The Woodsman is with me" — the only proof that matters by client #3.

## Getting paid — decided

- **Default: GoCardless direct debit** — mandate set up on the laptop at signing (~1% fee).
  First month collected day one.
- **Fallback only** (client is old-school or refuses GoCardless): bank standing-order
  mandate on the printed agreement. Carry a few blanks; don't offer it first.
- **Paper**: one-page agreement — parties, £/mo, 12-month initial term then rolling
  monthly, what Foundation includes (lift the bullet list from `config/ladder.yaml`),
  site remains ours if hosting stops, 30 days notice, GDPR one-liner. Two signatures,
  photo of it into the lead folder.

## Delivery checklist per signed client

- [ ] Dashboard sign form completed → `/clients` shows the MRR row.
- [ ] Verify with the owner in person: phone number, hours, menu items, postcode
      (the bible flags conflicts — resolve them from the owner's mouth, then
      `bible --force` + `build` if anything changed).
- [ ] Domain registered (`<business>.co.uk`), DNS A/MX/SPF set.
- [ ] `provision/provision_client.sh` run; all acceptance checks in
      [FIELD_DEPLOYMENT_PLAYBOOK.md](FIELD_DEPLOYMENT_PLAYBOOK.md) §3 pass.
- [ ] Mailbox credentials handed over; owner logged in while you watch.
- [ ] Facebook page: website field updated to the new domain (owner does it, you guide).
- [ ] First payment collected/mandate active.
- [ ] Status → **live**. Book the 30-day check-in (that's the Social Launch upsell slot).
