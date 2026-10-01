# Local handover after repository cleanup

The user approved the full bloat-audit cleanup on 1 October 2026 and paused the M4
agent while it was carried out. The delivered canonical branch is **main**. Read
README, the research specification, source guide and Bible contract before continuing.
Do not restore old client folders, copied agent worktrees or the retired legacy producer.

## Update the M4

Repository: `/Volumes/deep-1t/Users/k3ss/k3ss-official/socialite`.
Environment: Conda `socialite`, Python 3.12. Dashboard port: 5057.

1. Stop the dashboard and worker with Ctrl-C in their respective terminals.
2. Inspect `git status --short`. Preserve any uncommitted ALO lead changes and actual
   pilot activity before switching. Do not overwrite new local evidence with the seed.
3. Fetch the remote, switch to main and fast-forward. The old research/creative branches
   have been consolidated or retired; do not merge their old snapshots back into main.

```sh
cd /Volumes/deep-1t/Users/k3ss/k3ss-official/socialite
conda activate socialite
git fetch origin --prune
git switch main
git pull --ff-only
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
bash provision/test_mock.sh
```

If local changes prevent switching, save them selectively and reapply ALO's changes
afterwards. An agent should reconcile the actual diff, not blindly stash/pop deleted
demo artifacts or overwrite a modified event log.

## Remove old local runtime records

The user's existing full external repository backup is reported to be under
`/Volumes/hotblack-2tb/backups`. The cloud could not inspect that volume. A separate
verified Git bundle, working-tree snapshot and SQLite backup were taken in the cloud
at `/workspace/backups/socialite-pre-cleanup-20261001` before editing.

The following one-time migration adds its own timestamped backup in the requested
M4 backup location before removing demo data:

```sh
python tools/focus_pilot.py --keep alo-soft-play-hire-lancashire \
  --backup-dir /Volumes/hotblack-2tb/backups
python -m socialite.cli status
```

It preserves ALO's folder, evidence, Bibles, reviews, spend, agreements and jobs. It
removes other lead folders, their client/service/job rows and non-ALO demo events, then
rebuilds the indexes. It refuses to run while the CLI worker holds its lock. Keep the
dashboard stopped too. This is actual deletion, not an archive feature.

The backup contains `data.tar.gz`, a consistent `ledger.sqlite` and a manifest. Restore
the data tree and that database together if needed. If copying a modified old event log
back into the repo to retain ALO activity, do so before this migration so its filtering
keeps the real ALO entries. Reindex alone does not remove old client agreements or jobs.

## Restart and continue the pilot

```sh
python dashboard/app.py
```

In the other terminal:

```sh
conda activate socialite
claude --version
python -m socialite.cli worker
```

The board should contain ALO only and show **Not assessed**, not a misleading zero
performance rating. Check the client and activity views after migration as well.

The next task is ALO's first real collection and synthesis run, followed by staff review.
The cloud does not have Claude CLI installed and cannot verify the M4 login. The owner
has agreed to the pilot, but no publication, outreach, domain purchase or generated
creative spend was performed during cleanup. Existing user authorisation persists;
do not restart an unnecessary permission loop.

## Remaining product work

- Ingest supplied screenshots and owner answers as first-class evidence. The starter
  dossier is not automatically a verified production Bible.
- Verify the supplied Group's current access and identity; Group does not mean private.
- Complete missing packages/prices, coverage, equipment and applicable trust information
  through a concise owner intake. Do not infer Chorley, credentials or charity affiliation.
- Expand source planning and choose tools/connectors based on actual local access.
- Benchmark three providers, still TBD; Gemini Pro/Flowith credits do not prove API access.
- Develop the Socialite design signature after the pipeline works. Higgsfield generation
  credits have not been spent here. Hermes remains deferred.

## Delivered validation

The [cleanup verification record](audit/2026-10-01/cleanup-verification.json) describes
checks and limitations. Automated tests use synthetic fixtures and mocked external
services. They exercise the real review-to-render/proposal path and the local migration,
not a live provider or a real VPS. Browser checks in the cloud inspect a local test
server, not the user's M4 browser.
