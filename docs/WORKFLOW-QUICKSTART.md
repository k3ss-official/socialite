# Local setup and recovery

Use Python **3.12** in the Conda environment **socialite**. This is the setup authority;
README links here rather than repeating installation instructions.

## Start the application

From the repository root:

```sh
conda env create -f environment.yml
conda activate socialite
python --version
python -m unittest discover -s tests -v
python dashboard/app.py
```

If the environment already exists, activate it and run
`python -m pip install -r requirements.txt` instead of recreating it.
Open http://127.0.0.1:5057. In a second terminal, in the same repository:

```sh
conda activate socialite
claude --version
python -m socialite.cli worker
```

Live synthesis needs a working Claude CLI login, not just a version response. Resolve
authentication using Anthropic's current CLI instructions when needed. OpenAI, Gemini
and Flowith adapters are not integrated. The dashboard binds to loopback, has CSRF
protection and records self-reported staff names; it is not an authenticated public service.

## Research and review

1. Open ALO's record. Enter your name and choose **Start research**.
2. Watch collecting → synthesizing → awaiting review. Failures retain their error and
   collection counts. Retry deliberately; **Refresh sources** bypasses the valid cache.
3. Inspect coverage, claims and receipts. Unknown, inferred, conflicted and snippet-only
   claims cannot be approved as public facts.
4. Approve supported page fields and record permission basis, note and usage for images.
   Save the review. Missing or changed source/asset files block approval or preview.
5. Choose **Generate preview and proposal**. The worker renders from approved content.
   It does not deploy, register a domain or contact the owner.
6. Use **Open printable report → Print / save as PDF**. The JSON Bible remains the source
   of truth; the report requires no additional model call.

The [ALO starter dossier](pilots/alo-soft-play-hire-lancashire/README.md) contains
screenshots and research notes. It is not automatically ingested production evidence.
Current Group access and important owner-only facts remain unconfirmed.

## CLI equivalents

```sh
python -m socialite.cli research alo-soft-play-hire-lancashire --staff-name Tony
python -m socialite.cli jobs alo-soft-play-hire-lancashire
python -m socialite.cli preview alo-soft-play-hire-lancashire --staff-name Tony --bible-version 1
```

Preview requires a saved valid staff review. `collect` collects receipts only.
`build` and `pitch` render saved content directly and enforce the review gate for v2.
The old `run`, `bible` commands and `run.sh` wrapper are retired.

Targeted discovery requires an explicit locality:
`python -m socialite.cli find "Business Name, Town" --locale uk`.
Area discovery also needs an explicit sector:
`python -m socialite.cli find-locale --locale uk --area "Town, UK" --sector hospitality --limit 10`.
Hospitality is currently the only area-discovery profile; soft-play sources need a
different plan. A locale does not establish a business's town or category.

## Backups and recovery

```sh
python -m socialite.cli backup /path/outside/repo/ledger.sqlite
python -m socialite.cli reindex
```

Back up **both the full data directory and SQLite**. Captures, images, Bibles, reviews,
generated sites, proposals and events are runtime data ignored by Git. Clients, services
and jobs are durable SQLite records. Reindex only reconciles leads and events; it does
not erase financial or job history. Git alone is not an operational backup.

If a worker crashed, stop the old process, then start
`python -m socialite.cli worker --recover`. Interrupted jobs become failed for a
deliberate retry. An exclusive lock prevents two CLI workers. Cancellation finishes an
in-flight operation before stopping and cannot undo a billed call.

For migration from the old demo data, follow [LOCAL-HANDOVER.md](LOCAL-HANDOVER.md).
The focus tool takes its own backup and retains all ALO records while deleting other
lead folders, their agreements/jobs and old demo events. Stop both processes first.

## Validation boundaries

Regression tests use disposable data, synthetic fixtures and mocked external services.
The cloud cannot verify the M4's Claude login or control its browser. The first real
ALO research run and the three-provider benchmark are still pending. No Higgsfield
credits were spent; no Hermes harness has been built.
