# Socialite Design

A local staff workflow for **select prospect → research → evidence-backed Bible →
review → client-branded preview and proposal**. The Bible is the maintained source of
truth for the landing page and future services.

**ALO Soft Play Hire Lancashire is the sole seeded pilot.** Its owner has agreed to
participate; its starter dossier is not a completed or publication-approved Bible.

## Start here

Use the existing Conda environment named `socialite` with Python 3.12.
Follow [setup, commands and recovery](docs/WORKFLOW-QUICKSTART.md). Run the local
dashboard and worker in separate terminals. Synthesis requires an installed,
authenticated Claude CLI.

## Current scope

- Bounded search/web collection with source receipts, access outcomes and valid fresh caches.
- Bible v2 claims, uncertainty, coverage, comparisons and now/next/later roadmap.
- Staff approval of supported public facts and image permissions.
- Static preview/proposal generation and a printable report.
- Durable local jobs and client/service ledgers; file-backed lead/event indexes.
- Local-only dashboard with CSRF protection; staff names are self-reported.

Expanded browser/API collectors, screenshot/owner-answer ingestion, the three-provider
benchmark, recurring service automation and the signature design system remain future
work. Hermes remains an idea, not an implemented harness. Configured service terms and
price bands are proposals. The spend setting is an estimated preflight gate, not a
guaranteed provider billing ceiling.

## Project references

- [Research requirements](docs/RESEARCH-SPEC.md)
- [Sources, limitations and candidate tools](docs/RESEARCH-SOURCES.md)
- [Bible contract and approval](docs/BIBLE-V2.md)
- [Design direction](docs/DESIGN.md)
- [ALO dossier and owner intake](docs/pilots/alo-soft-play-hire-lancashire/README.md)
- [Deployment](provision/README.md)
- [Local handover](docs/LOCAL-HANDOVER.md)
- [Historical gap and bloat audits](docs/audit/README.md)

## Repository layout

```text
socialite/       CLI, collectors, Bible, review, jobs, storage and rendering
dashboard/       Flask staff UI and printable report
schemas/         validation contracts
prompts/         current Bible synthesis prompt
config/          settings, proposed service ladder, locales and sector discovery profiles
templates/       supported website and proposal templates
tests/fixtures/  small synthetic inputs independent of client data
data/            ALO seed plus ignored, backed-up operational artifacts
provision/       explicit deploy/mail scripts and isolated mock checks
tools/           one-time local pilot-data migration
```

New research is queued through the dashboard or CLI and stops for review. The previous
unreviewed one-command pipeline and its separate synthesis prompt have been removed.
Original-format content remains supported as the renderer's projection contract and
for reading historical files; it is not a second producer for new research.
