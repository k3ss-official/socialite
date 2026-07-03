# Trial Day — Scran Away relaunch pitch

One page. Everything runs off your laptop; no network needed in the meeting.

## Before you leave (5 min)

```sh
cd ~/k3ss-official/Socialite && git pull
.venv/bin/python dashboard/app.py     # → http://127.0.0.1:5057
```

Open these two tabs and leave them up:

- **Demo site** — http://127.0.0.1:5057/preview/scran-away-chorley/4/
- **Pitch sheet (relaunch angle)** — http://127.0.0.1:5057/lead/scran-away-chorley/pitch/5

Optional refresh with live data (network needed, ~$1, only if you want the very
latest): `./run.sh "Scran Away, Chorley, UK"` then regenerate the pitch:
`.venv/bin/python -m socialite.cli pitch scran-away-chorley --angle relaunch`

## In the meeting

1. **Open with the relaunch angle** — the blue block at the top of the pitch sheet.
   Three lines, say them as written. This is Janine reopening, not a cold pitch.
2. **Read the rep briefing first** (amber blocks) — before you quote anything:
   - Confirm new trading name, location, reopening date (site carries all three).
   - Phone number is unconfirmed (two candidates on the sheet) — ask, don't guess.
   - Our old demo (dogonapc.com) has a postcode error — own it, say the rebuild fixes it.
3. **Show the site on their phone** — same URL works on your laptop's hotspot, or
   just hand the laptop over. Mobile layout is verified.
4. **Walk the gaps** ("What they're losing right now") — each has a say-it-out-loud
   line and the rung that fixes it.
5. **Offer the tiers** — Growth (£257–367/mo) is the recommended tier on the sheet.
   Every line item stands alone; one cancellation never takes the account.

## If they say yes

Lead page → http://127.0.0.1:5057/lead/scran-away-chorley → **Sign** section:
tick the rungs they took, enter the agreed monthly per rung, submit. That writes
the client ledger and MRR picks it up on /clients.

Going live on the VPS is one command once we have host details (see
`provision/README` / TODO board — still blocked on server credentials).

## If something breaks

- Dashboard won't start → `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
- Pitch/bible viewers 404 → check `data/leads/scran-away-chorley/` exists (it's in git).
- Never re-run `find`/`research` on hotel wifi mid-meeting — artifacts are already
  built; the pipeline never clobbers good research with a failed harvest anyway (guarded).

## What changed for this trial (July 2026)

- Pitch **angles**: vetted opening framings in `config/ladder.yaml` → `angles:`.
  `--angle relaunch` used for this pitch; `default` behaves exactly as before.
- Research cache self-heals on fresh clones (manifest referenced gitignored files)
  and never overwrites a good bundle with an empty harvest.
- `claude -p` calls retry once on transient CLI failures.
