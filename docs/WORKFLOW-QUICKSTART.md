# Run the staff research workflow on the M4

Run these commands inside your existing Socialite repository. The working branch is
`feature/bible-workflow`. Preserve any local edits before switching branches.

```sh
git fetch origin
git switch feature/bible-workflow
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python dashboard/app.py
```

Open **http://127.0.0.1:5057**. Saved lead files are indexed automatically on first startup.
The dashboard remains a local prototype; staff names are recorded rather than authenticated.
Form submissions have CSRF protection. Do not expose this server publicly.

In a second terminal, from the same repository:

```sh
claude --version
.venv/bin/python -m socialite.cli worker
```

Live synthesis requires the existing Claude CLI installation and a working login. If
`claude --version` fails, install it using Anthropic's current official instructions.
If a synthesis call reports an authentication error, resolve the CLI login and retry
the research job. This branch has no OpenAI, Gemini or Flowith runtime adapter yet.

## Walk through one prospect

1. Select a lead on the board. Enter your name and choose **Start research**. A repeat
   click returns the active job rather than creating another one.
2. Watch collecting → synthesizing → awaiting review. Failed jobs retain their error
   and collection counts. To retry, start research again. **Refresh sources** bypasses
   the 24-hour cache; unchanged business context can reuse fresh captures.
3. Open the new Bible. Read the summary, coverage, claims and receipts. Unknown,
   conflicted, inferred or snippet-only claims cannot be approved for public copy.
4. Approve the supported page fields. Record a permission basis and note for any image
   you select. Save the review. This creates an immutable revision as well as the latest
   review record; an outdated form cannot overwrite a newer review silently.
5. Choose **Generate preview and proposal**. Missing required approvals are reported
   immediately. The worker builds the real static page and deterministic service proposal.
   It does not deploy, purchase a domain or send anything to the prospect.
6. Use **Open printable report → Print / save as PDF** for the report layout inspired
   by the supplied example. The JSON Bible remains the structured source of truth.

The first test case should be Vestry after a fresh collection. To create its lead if it
is not on the board, use `.venv/bin/python -m socialite.cli find "Vestry, Chorley" --locale uk`.
Review its category and affiliated website rather than assuming it has no web presence.
Existing legacy leads derive locality from their IDs if no explicit locality was stored.

The collector is currently bounded requests/BeautifulSoup plus search. It keeps metadata,
captures and access failures, and stops further requests to a host after HTTP 403/429.
It does not bypass logins or access challenges. Broader source planning, browser/API
adapters, domain-wide throttling and richer official-source research remain next steps.
The synthesis prompt reports those coverage limitations instead of claiming a complete audit.

## Recovery and backups

If lead/event indexes need reconciling:

```sh
.venv/bin/python -m socialite.cli reindex
```

This rebuilds file-backed leads and spend/events without clearing clients, services or jobs.
Malformed input files cause a visible failure rather than being silently skipped.

Back up the durable SQLite ledger with the supported command:

```sh
.venv/bin/python -m socialite.cli backup ../socialite-backups/ledger.sqlite
```

Also back up the entire `data/` artifact tree, including raw captures/images and reviews.
Git alone is not a backup: SQLite, captures and staff reviews are intentionally ignored.
Restore the artifact tree and database together. Do not delete an existing ledger to
recover a board index. Historical duplicate agreements need deliberate reconciliation;
this change prevents new duplicate signup rows and does not silently remove old ones.

If a worker crashed while a job was running, stop the old worker first, then run:

```sh
.venv/bin/python -m socialite.cli worker --recover
```

An exclusive worker lock prevents two CLI workers running together. Interrupted jobs are
marked failed for a deliberate retry. Cancellation finishes an in-flight operation before
stopping; it cannot undo an already billed request or an artifact already written.
Avoid running the legacy CLI pipeline concurrently against a prospect with an active job.

## Current validation and boundaries

Regression tests cover recovery/spend, signup idempotency, image routes/cache, optional
template fields, research geography/category, contact/site matching, uncertainty, evidence
references, review conflicts, CSRF, queue deduplication, failure/retry/recovery and the full
review-to-build/pitch path. External collection/model calls are mocked; live provider
synthesis has not been tested in this cloud workspace because Claude CLI is unavailable.

The USD 2 setting is an estimated preflight spend gate, not a guaranteed provider billing
ceiling. The three-AI benchmark is still pending. No Higgsfield generation credits were
used. Hermes is an idea under discussion; no harness integration has been implemented.
