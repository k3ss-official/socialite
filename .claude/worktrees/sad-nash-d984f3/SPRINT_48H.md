# 48-Hour Revenue Sprint

Goal: **first real money — at least 1 signed Foundation client (£49/mo), target 3 pitches.**
Companion docs: [FIELD_DEPLOYMENT_PLAYBOOK.md](FIELD_DEPLOYMENT_PLAYBOOK.md) (mechanics),
[FIRST_3_CLIENTS.md](FIRST_3_CLIENTS.md) (targets, scripts, paper). All commands from repo root.

**Hard prerequisites (can't start without):** a confirmed VPS (host + deploy user — Tony's
call, not yet made), the `*.demo.k3ss.co.uk` wildcard A record created against it, a
GoCardless account (plus a few printed standing-order mandates as the old-school fallback),
and ~£30 for one client domain registration.

---

## Hour 0–2 — Infrastructure preflight (desk)

```sh
bash provision/test_mock.sh                                  # RESULT: 12 passed, 0 failed
ssh deploy@vps 'nginx -v && certbot --version && rsync --version | head -1 && docker ps --format "{{.Names}}" | grep mailserver'
# wildcard DNS must exist (⚠ MANUAL, exact record in playbook §0): *.demo.k3ss.co.uk → VPS IP
dig +short check.demo.k3ss.co.uk                             # VPS IP
claude --version                                             # logged in, plain terminal
```

**Gate:** every line passes. **Recovery:** missing VPS package → install it now; no
mailserver container → follow docker-mailserver quickstart (30 min) or descope mailboxes
to week 2 and sell Foundation without email day one (say "email lands this week").

## Hour 2–5 — Build all three prospects (desk, ~$3 LLM total)

```sh
./run.sh "The Woodsman, Chorley, UK"
./run.sh "Hinds Head, Charnock Richard, Chorley, UK"
./run.sh "The Roebuck Inn, Whittle-le-Woods, Chorley, UK"
.venv/bin/python dashboard/app.py    # review each: score, ALERTS, preview, pitch sheet
```

**Gate (per lead):** playbook §1 acceptance checks; **every bible alert resolved or the
lead swapped out** (bench: `the-talbot-chorley`, or refill via
`find-locale --locale uk --limit 25`). **Recovery:** claude 401 → plain terminal; cost cap
→ inspect spend, it's $2/lead for a reason; bad photos → prune `raw/images/`, `bible --force`.

## Hour 5–7 — Deploy demos + print collateral (desk)

```sh
for id in the-woodsman-chorley hinds-head-chorley the-roebuck-chorley; do
  v=$(ls -d data/leads/$id/site/v* | sed 's/.*v//' | sort -n | tail -1)
  provision/deploy_site.sh --site data/leads/$id/site/v$v \
    --domain $id.demo.k3ss.co.uk --vps deploy@vps --email scousercheeky@gmail.com
  curl -sI https://$id.demo.k3ss.co.uk | head -1     # HTTP/2 200 each
done
```

Print 3 pitch sheets (dashboard → pitch → print to PDF). Print 3 blank one-page
agreements. Load all three demo URLs on your phone; screenshot each as offline backup.

**Gate:** three 200s over mobile data, not wifi. **Recovery:** certbot/DNS → playbook §3
table; total blocker → demos run off the laptop via dashboard preview (weaker, still sells).

## Hour 7–10 — Field round 1 (Chorley, 1:30–4:30pm)

Walk-in order: **The Woodsman → Hinds Head → The Roebuck** (most digitally active first —
they convert fastest). Script and close per FIRST_3_CLIENTS.md.

Outcomes per visit: **signed** (sign form + payment mandate on the spot) / **return
booked** (specific day+time) / **owner absent** (name + when back) / **no** (ask "who else
round here needs this?" — referral, then next).

## Hour 10–14 — Same-day delivery for anyone signed

The wow is going live the day they signed. Playbook §3: register domain, DNS, wait for
propagation, `provision_client.sh`, full acceptance checks, credentials handed over,
status → **live**. If DNS is still propagating at midnight, finish at Hour 24 — tell the
owner "live tomorrow morning" and be right.

## Hour 24–30 — Day 2 morning: iterate (desk)

- Messenger follow-up (template in FIRST_3_CLIENTS.md) to every non-signed visit, demo
  link included.
- Rebuild anything the field contradicted (wrong hours/phone): fix inputs → `bible --force`
  → `build` → redeploy demo. Log the correction in `notes/LESSONS.md`.
- Funnel low? `find-locale --locale uk --limit 25`, qualify 2 more, run pipeline (~$2).

## Hour 30–36 — Field round 2

Booked returns first (they expect you — highest close rate), then owner-absent revisits,
then one new candidate. Same close, same paper.

## Hour 36–48 — Deliver, collect, close the loop

- Finish playbook §3 for every signed client; **no client left in `signed` limbo** — every
  acceptance check green or a named blocker with a date.
- Confirm first payments actually collected (GoCardless dashboard / bank).
- Dashboard `/clients`: MRR reflects reality. Statuses: pitched / signed / live all true.
- 15 minutes honest retro into `notes/LESSONS.md`: what line closed, what objection
  repeated, what broke. Book every 30-day check-in (the upsell slot) in the calendar.

---

## Sprint failure modes

| Risk | Counter |
|---|---|
| 0 signs after round 1 | Objections are data — usually price (offer month 1 free; never discount the £49) or trust (lead with Scran Away portfolio + "no payment until it's live on your domain"). Round 2 with the adjusted line. |
| Owner wants "to think" forever | Two touches max (visit + follow-up), then bench and replace from the funnel. The pipeline makes prospects cheap — desperation is the only expensive thing. |
| VPS/mail blocker mid-sprint | Site can go live without the mailbox (nginx+certbot only, `deploy_site.sh` directly). Email "this week". Never delay a signed client's site for mail. |
| A demo is wrong in front of the owner | "Spotted something to fix — that's exactly the service" — correct from their mouth, redeploy tonight. The bible alerts exist to make this rare. |
| Anthropic/claude outage | Bibles for all 3 targets are pre-built by Hour 5; selling and provisioning never depend on the LLM. |
