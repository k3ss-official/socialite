# Socialite repository bloat audit

Assessed on 1 October 2026 against GitHub branch `feature/bible-workflow`, commit [`bf0d7f3`](https://github.com/k3ss-official/socialite/tree/bf0d7f3573a8a514d034db0c836bf7a773ba7b8d). Branch comparisons use the fetched remote history, including the previously shallow main history. This is a cleanup recommendation, not a record of deletions or merges performed.

The active Python application is reasonably small. The main bloat comes from a tracked older repository copy, repeated client outputs, near-duplicate documents, contradictory operating guidance and two unmerged experimental branches. The priority is to establish one current implementation and one clear set of instructions before the local handoff.

The user's requested deletion of old leads is present remotely: the last commit removed 15 lead files. ALO and Scran Away remain at the active top-level lead path. The audit inspected an isolated copy of that exact remote commit; it did not inspect the M4's uncommitted files, running processes or SQLite ledger.

## Measured inventory

These sizes are sums of tracked file contents, in decimal MB. They are not compressed clone sizes or the user's M4 disk usage.

| Area | Files | Bytes | Assessment |
|---|---:|---:|---|
| Entire active branch | 277 | 6,982,319 | Approximately 6.98 MB |
| `.claude/worktrees/sad-nash-d984f3/` | 133 | 3,375,857 | Old repository copy; 48.3% of the tracked bytes |
| Top-level `data/leads/scran-away-chorley/` | 62 | 3,146,290 | Old client artifacts; 45.1% of tracked bytes |
| Top-level `socialite/` | 18 | 88,728 | Small active application package |
| Top-level `dashboard/` | 12 | 52,188 | Active views, templates and styles |
| Top-level `docs/` | 14 | 146,913 | Some current documents, some duplicates and drafts |

Removing the nested repository copy and top-level Scran Away artifacts would remove 195 tracked files and 6,522,147 bytes: approximately **93.4% of current tracked content bytes**, before any replacement test fixtures. It would not erase those objects from Git history or automatically reduce existing clone sizes by that amount.

## Recommended bloat list

### 1 Remove the tracked Claude worktree copy

**Target:** `.claude/worktrees/sad-nash-d984f3/` in its entirety.

This is 133 tracked files, including an older application, schemas, templates, configuration, all 16 old lead records, generated Scran Away outputs and old handoff documents. Of the nested files, 92 are byte-identical to their top-level counterparts, 22 have different current counterparts, and 19 exist only in the nested copy after the recent lead cleanup. Those 19 comprise the 15 removed lead records and four old planning documents: `FINAL_HANDOFF.md`, `FIRST_3_CLIENTS.md`, `SPRINT_48H.md`, and `TODO.md`.

`git worktree list --porcelain` in this checkout reports only the root working tree. The nested material is tracked ordinary content here, not a registered working tree in this cloud checkout. The local agent should inspect the M4's worktree registration before removing a locally active checkout. Do not remove unrelated `.claude` preferences or useful agent configuration simply because the folder name contains Claude.

**Recommendation:** remove this specific copy from the current branch and ignore `.claude/worktrees/` so agent worktrees do not get committed again. The Git history already contains the old material. No replacement archive directory is needed.

**Why first:** even after removing old top-level leads, this copy still exposes those leads and obsolete instructions to recursive file searches and agent context ingestion. It also duplicates old provisioning scripts and tests.

### 2 Decouple tests from Scran Away and remove the remaining client artifacts

**Targets:** `tests/test_workflow.py:34` and `:35`, then `data/leads/scran-away-chorley/`.

The test setup reads Scran Away's real lead and Bible files directly. Every test therefore depends on the old client folder, including tests unrelated to that business.

**Verification:** on the exact remote snapshot, all 21 tests passed. In an isolated copy with just that client folder temporarily removed, all 21 errored with `FileNotFoundError` in setup. The folder was then restored in the isolated copy. The user's working data was untouched.

**Recommendation:** create small synthetic lead and original-format Bible fixtures under `tests/fixtures/`; update setup to read them; retain the useful behavior tests. Then remove all 62 top-level Scran Away artifacts. The existing synthetic `tests/fixtures/bible-v2.json` should remain.

Do not retain a client in the active pipeline merely to satisfy a test dependency. Do not resolve the failure by deleting the tests.

### 3 Remove repeated Scran Away prose reports

**Targets:**

- `clients/scran-away/bible-v2-scran-away-chorley.md`
- `notes/scran-away-bible-v2-2026-07-19.md`
- `notes/scran-away-manual-bible-2026-07-19.md`

The first two are exact byte-for-byte duplicates: 6,380 bytes each. The third is a superseded manual run. None is loaded by current runtime code. They are old client material rather than reusable source code or current ALO evidence.

**Recommendation:** remove all three from the current tree. Extract any still-useful general collection lesson into one corrected research note first. A root `clients/` folder containing only an old handwritten report does not need to survive as a competing client-data structure.

### 4 Collapse the two deep dive drafts into the current specification

**Targets:** `docs/DEEP-DIVE.md` and `docs/DEEP-DIVE-SPEC.md`.

These are approximately 98.3% similar by character sequence comparison. Their differences are explanatory annotations and references, not two independently necessary specifications.

Both describe paths such as `bibles/<lead-id>/` and `leads/{locale}/leads.json`, while current storage is under `data/leads/<id>/`. Both contain a prose JSON contract that differs from the implemented Bible v2 schema. They also describe a hard billing cap, a single no-revisit pass, older sales assumptions and a Scran Away/Pokhara validation plan.

**Recommendation:** preserve their useful research requirements in one current research specification, reconciled with the comprehensive handoff and `docs/BIBLE-V2.md`. Then remove both duplicated drafts. Keep a clear distinction between future research requirements and the implemented data contract. Do not discard unimplemented requirements merely because their present container is stale.

### 5 Delete the copied creative document and replace its obsolete operating assumptions

**Targets:** `docs/CREATIVE-DIRECTOR-SOUL copy.md` and `docs/CREATIVE-DIRECTOR-SOUL.md`.

The two are approximately 99.1% similar; the copy only changes the introductory description. Delete the `copy` document.

The remaining creative draft contains useful ideas: brand fidelity, craft, consistency, source and usage provenance, controlled variation and recording rejected directions. However, it presents mandatory gates tied to `BRAND.md`, `PROJECT.md`, `STYLE-LOCK.md` and `MEMORY.md`, none of which exists in the audited tree. It also references external system-agent conventions that are not implemented here.

**Recommendation:** reduce this to one clearly labelled creative design proposal aligned with the user's actual direction: client branding, a recognisable Socialite signature, tasteful work, and sensible use of Higgsfield credits. Describe required inputs and genuine authorisation boundaries in the current workflow. Do not let an old unimplemented draft create repeated approval requests or block already-authorised work.

### 6 Consolidate outdated setup and recovery guidance

**Targets:** `REBUILD.md`, setup sections in `FIELD_DEPLOYMENT_PLAYBOOK.md`, and repeated setup sections in `README.md`.

`REBUILD.md` advertises itself as a complete recovery authority, but its current-state marker is 19 July. It recommends Python 3.11+ and venv, describes the old reveal-already-live process, asserts a hard cost cap, mixes Scran Away commercial history with recovery instructions, and speaks about dedicated Hermes agents. The user now requires Conda `socialite`, Python 3.12, staff review and a local pilot; Hermes is explicitly an idea only.

`FIELD_DEPLOYMENT_PLAYBOOK.md` still links to deleted root documents `FIRST_3_CLIENTS.md` and `SPRINT_48H.md`. These are two confirmed broken Markdown links. It also says SQLite is only an index, although clients, services and jobs are now durable SQLite records. Following that description could produce an incomplete backup.

**Recommendation:** make `docs/WORKFLOW-QUICKSTART.md` the one setup and recovery authority. Keep README as a short project overview with links rather than repeated installation instructions. Extract any useful deployment-specific information into one corrected deployment guide and remove the old REBUILD document. Update code comments and CLI help that still prescribe `.venv` or overstate the billing cap.

Do not delete the working provisioning scripts simply to eliminate their stale documentation.

### 7 Replace contradictory research lessons with one dated source guide

**Targets:** `notes/LESSONS.md` and `notes/SCRAPING.md`.

Useful lessons are mixed with disproven rules. Examples include:

- A real website on an unrelated domain supposedly means a template/freebie. Current qualification deliberately accepts genuinely affiliated sites.
- A Socialite credit supposedly proves a prior pitch went cold. A credit cannot establish that business history.
- Facebook Group URLs supposedly being filtered out. The current discovery code accepts them, and ALO's known surface is a Group.
- Scrapling being the prescribed production library, even though it is absent from current dependencies and collection code.
- Socialite supposedly already running dedicated Hermes agents. It does not.
- Platform-access conclusions from one manual July experiment being written as general current facts.

**Recommendation:** merge the useful content into one source guide that states what is verified in current code, what was observed in an older experiment, what remains a candidate tool, and what has been superseded. Keep entity matching, non-deterministic search, access-failure recording, bounded retries and attribution discipline. Remove the wrong domain and prior-pitch heuristics.

### 8 Remove old demo activity from the repository seed

**Target:** tracked `data/events.jsonl`.

The audited file contains 82 historical events referencing the old prospects and a `test-sign-flow` lead. Removing lead files does not remove these event records. The current `/events` route still displays them, and reindexing replays them.

**Recommendation:** remove the old demo seed events from the committed tree. Keep real ALO and subsequent operational events as runtime records with appropriate backups. Inspect the actual M4 log before applying this recommendation there: it may contain new activity absent from GitHub.

The reindex command preserves clients, services and jobs intentionally. It is not a complete reset of a local database. This audit cannot establish whether the M4 has any old synthetic client agreements or jobs; the local agent should inspect that before calling the dashboard a clean start. Do not erase real pilot records to tidy a screen.

### 9 Retire the parallel legacy synthesis entry point after migrating its callers

**Targets:** `socialite/stages/bible.py`, `prompts/bible.md`, the `run` and `bible` CLI paths, and `run.sh`.

The staff worker synthesizes with `socialite/bible_v2.py` and `prompts/bible-v2.md`. The older CLI paths still generate the original Bible format and allow build/pitch without the new staff-review workflow. This creates two meanings of “run the Bible” and two prompting contracts to maintain.

**Recommendation:** make Bible v2 plus review the sole producer for new work. Provide deliberate CLI entry points to the same job/review flow, then retire the old producer and its wrapper if no required callers remain. Keep discovery, research and explicit build/pitch interfaces where useful.

**Dependency warning:** `schemas/bible.schema.json` is still validated by build/pitch, and `bible_v2.project()` currently translates approved v2 content into that format. `dashboard/templates/bible.html` handles old saved artifacts. Those are compatibility consumers, not automatically dead files. Remove them only after changing and verifying their consumers. The two Bible schemas and two viewer templates are not exact duplicates.

### 10 Separate reusable configuration from old market and sales assumptions

**Targets:** `config/locales/np-pokhara.yaml`, discovery sections in locale packs, and repeated commercial claims in old documents.

Multi-market configuration is useful. However, calling Pokhara “the MVP-proper market,” keeping UK discovery tied to Chorley hospitality, and treating old three-door prices as current agreed strategy confuses an ALO-led pilot.

**Recommendation:** keep the small locale mechanism. Remove obsolete market-priority language. Keep the Nepal pack only as an explicitly supported secondary/example locale, or remove it after verifying no intended caller uses it. Separate location/language/currency from sector discovery plans so soft-play and future categories are not forced into hospitality seeds. Treat the current ladder and price bands as configurable proposals unless the user confirms them as commercial policy.

This is scope clarification rather than a meaningful dependency-size saving.

## Branch consolidation

Four remote branches were present. The ahead/behind counts below are relative to remote `main` after fetching full history.

| Branch | Ahead | Behind | Recommendation |
|---|---:|---:|---|
| `main` | — | — | Make this the canonical maintained line after the reviewed pilot workflow and cleanup land |
| `feature/bible-workflow` | 4 | 0 | Current pilot work; complete cleanup and validation here, then merge the draft PR and retire the branch after handoff |
| `claude/cool-websites-gvlxlb` | 4 | 5 | Inspect selectively; do not merge its old client assets wholesale |
| `claude/repo-review-analysis-o4vka` | 1 | 13 | Extract useful resilience ideas; do not restore its old trial documents and outputs |

The creative branch's current tracked tree is 184,251,374 bytes, versus 6,982,319 bytes on the pilot branch. Five generated PNG originals alone total 172,699,586 bytes; an original MP4 adds 2,499,677 bytes. There are also delivered derivatives, fonts and a client-specific cinematic draft.

Potentially reusable code includes the cinema template, motion JavaScript and `tools/build_standalone.py`. They need assessment before reuse: the cinema template calculates ratings from selected review quotes, and the standalone utility has hard-coded Scran Away map copy and asset names plus a Pillow dependency. Extract design ideas or corrected reusable code; do not import old business claims into ALO.

The review branch adds pitch angles and CLI/collection resilience. Its missing-capture cache checks remain worth considering: the current collector checks context and age, but does not validate every cached capture exists before reuse. Its degraded-harvest fallback and CLI retry need deliberate freshness, cost and uncertainty handling rather than a blind merge.

Branches sharing history are normal; their existence is not itself proof of duplication. Both old experimental branches have unique work. Identify any retained code and asset-storage needs before deleting them. Deleting branches alone does not purge large media from Git history or guarantee a smaller existing clone. History rewriting is a separate migration and was neither requested nor performed.

## Keep these parts

- The active store, jobs, collector, validation, approval, builder, pitch generator and local dashboard.
- All seven Python requirements: imports confirm requests, BeautifulSoup, Jinja2, Flask, PyYAML, jsonschema and ddgs are used. There is no demonstrated removable package bloat here.
- `environment.yml` and `requirements.txt`: one specifies Conda/Python, the other application dependencies. They serve different purposes.
- Canonical JSON schemas and prompt files required by active callers.
- ALO's seed lead, dossier, sources and short owner intake. They are relevant pilot evidence and questions, not a completed production Bible.
- Synthetic test fixtures and useful regression coverage.
- Templates distinct from generated client sites. Dashboard views, printable reports, website templates and proposal templates have different consumers.
- Small provisioning scripts unless a reviewed replacement changes the deployment plan.
- The dated baseline gap analysis and its check evidence, labelled as historical. They explain previous faults, not necessarily the current implementation.
- The synthetic report-format PDF if it remains useful as a design example. It is not a source of client facts.

## Recommended execution order

1. Confirm the local agent is on the intended remote branch and inspect uncommitted M4 work.
2. Replace Scran Away test inputs with minimal synthetic fixtures and verify the behavior suite.
3. Delete the nested Claude repository copy, remaining Scran Away artifacts and repeated prose reports; add worktree/generated-output ignore rules appropriate to the chosen data layout.
4. Separate old demo activity from real pilot records; reindex the active lead/event files and verify the board, clients and activity views.
5. Consolidate research specifications, setup/recovery, creative proposals and collection notes. Update internal links and remove contradictory instructions.
6. Migrate new CLI work onto Bible v2 and review; retire legacy producers without breaking their shared consumers.
7. Review unique experimental branch changes, extract useful parts, validate, then consolidate onto main and close obsolete branches.

Completion means ALO is the sole intended pilot on a fresh checkout and the M4, tests no longer depend on old client folders, recursive agent searches do not discover a second old application, setup uses Conda/Python 3.12 consistently, the documented current workflow matches code, and current provider/tool/Hermes limitations are explicit. No archive hierarchy is proposed.

## Validation and limits

The audit used Git file inventories and object sizes, byte comparisons, near-duplicate document comparisons, source import/caller inspection, Markdown link checks, complete remote branch history, and two isolated test runs. All 21 tests passed on the audited remote snapshot; removal of the dependent client folder caused 21 setup errors. External research and model calls were mocked. Live provider synthesis, real deployment, browser control and the M4's local runtime data were not evaluated.

No application code, client records or branches were deleted or merged during this audit. The deliverable is this report. Source measurements and test logs were retained in the cloud scratch workspace for inspection; they are audit evidence, not extra production dependencies.
