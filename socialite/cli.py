"""Local CLI for discovery, Bible v2 research jobs and reviewed previews."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from . import jobs, store
from .config import ROOT, data_dir
from .stages import build, find, pitch, research


def main() -> None:
    ap = argparse.ArgumentParser(prog="socialite")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("find", help="qualify one named business and locality")
    p.add_argument("query", help='"Business Name, Town[, Country]"')
    p.add_argument("--locale", default="uk")
    p = sub.add_parser("find-locale", help="discover candidates using an explicit area and sector")
    p.add_argument("--locale", required=True)
    p.add_argument("--area", required=True)
    p.add_argument("--sector", required=True)
    p.add_argument("--limit", type=int, default=25)
    p = sub.add_parser("research", help="queue collection and Bible v2 synthesis for staff review")
    p.add_argument("lead_id")
    p.add_argument("--staff-name", required=True)
    p.add_argument("--force", action="store_true", help="refresh sources instead of using valid fresh captures")
    p = sub.add_parser("preview", help="queue a preview and proposal from approved Bible fields")
    p.add_argument("lead_id")
    p.add_argument("--staff-name", required=True)
    p.add_argument("--bible-version", required=True, type=int)
    p = sub.add_parser("collect", help="collect source receipts only; does not synthesize or build")
    p.add_argument("lead_id")
    p.add_argument("--force", action="store_true")
    for name in ("build", "pitch"):
        p = sub.add_parser(name, help="render saved approved content directly")
        p.add_argument("lead_id")
        p.add_argument("--bible-version", type=int)
        if name == "build":
            p.add_argument("--theme")
    p = sub.add_parser("jobs", help="show recent jobs for a prospect")
    p.add_argument("lead_id")
    sub.add_parser("dashboard", help="start the local staff dashboard")
    sub.add_parser("reindex", help="reconcile file-backed indexes; preserve durable ledgers")
    p = sub.add_parser("backup", help="back up SQLite client/service/job storage")
    p.add_argument("destination", type=Path)
    p = sub.add_parser("worker", help="process research and reviewed preview jobs")
    p.add_argument("--once", action="store_true")
    p.add_argument("--recover", action="store_true", help="mark interrupted jobs failed after the old worker stopped")
    sub.add_parser("status", help="show the active lead pipeline")

    args = ap.parse_args()
    try:
        if args.cmd == "find":
            print(json.dumps(find.find_single(args.query, args.locale), indent=2))
        elif args.cmd == "find-locale":
            for lead in find.find_locale(args.locale, args.limit, area=args.area, sector=args.sector):
                print(f"{lead['qualification']['score']:>3}  {lead['id']:<40} website={lead['website']['verdict']}")
        elif args.cmd == "research":
            print(json.dumps(jobs.enqueue(args.lead_id, "research", args.staff_name, force=args.force), indent=2))
        elif args.cmd == "preview":
            print(json.dumps(jobs.enqueue(args.lead_id, "preview", args.staff_name, bible_version=args.bible_version), indent=2))
        elif args.cmd == "collect":
            bundle = research.harvest(args.lead_id, force=args.force)
            print(json.dumps({'sources': len(bundle['fetched']), 'harvested_at': bundle['harvested_at']}))
        elif args.cmd == "build":
            print(json.dumps(build.build(args.lead_id, args.bible_version, args.theme), indent=2))
        elif args.cmd == "pitch":
            print(json.dumps(pitch.generate(args.lead_id, args.bible_version), indent=2))
        elif args.cmd == "jobs":
            print(json.dumps(jobs.for_lead(args.lead_id), indent=2))
        elif args.cmd == "dashboard":
            raise SystemExit(subprocess.call([sys.executable, str(ROOT / "dashboard" / "app.py")]))
        elif args.cmd == "reindex":
            print(json.dumps(store.rebuild_index()))
        elif args.cmd == "backup":
            print(store.backup_database(args.destination))
        elif args.cmd == "worker":
            import fcntl
            with open(data_dir() / ".worker.lock", "a") as lock:
                try:
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                except BlockingIOError:
                    raise SystemExit("A Socialite worker is already running")
                if args.recover:
                    print(f"Recovered {jobs.recover_interrupted()} interrupted jobs")
                print("Worker ready; Ctrl-C to stop", flush=True)
                try:
                    while True:
                        result = jobs.run_next()
                        if result:
                            print(json.dumps(result), flush=True)
                        if args.once:
                            break
                        if result is None:
                            time.sleep(2)
                except KeyboardInterrupt:
                    pass
        elif args.cmd == "status":
            with store.db() as conn:
                for row in conn.execute("SELECT json FROM leads ORDER BY updated_at DESC"):
                    lead = json.loads(row['json'])
                    score = '?' if lead['qualification'].get('score_status') == 'not_run' else str(lead['qualification']['score'])
                    print(f"{lead['status']:>8}  {score:>3}  {lead['id']:<40} {lead['name']}")
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc


if __name__ == "__main__":
    main()
