"""CLI — every stage is also callable programmatically (Phase 2 orchestrator entry points):
find.find_single / research.harvest / bible.generate / build.build / pitch.generate."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

from . import store
from .config import ROOT, settings
from .stages import bible, build, find, pitch, research


def _provision_dry_run(lead_id: str) -> str:
    script = ROOT / "provision" / "provision_client.sh"
    if not script.exists():
        return "(provision scripts not present)"
    proc = subprocess.run(["bash", str(script), "--lead-id", lead_id, "--dry-run"],
                          capture_output=True, text=True, cwd=ROOT)
    store.log_event("provision", "dry_run", "ok" if proc.returncode == 0 else "error", lead_id)
    return proc.stdout + proc.stderr


def cmd_run(args) -> None:
    lead = find.find_single(args.query, args.locale)
    lid = lead["id"]
    print(f"[find]   {lid}  score={lead['qualification']['score']}  "
          f"website={lead['website']['verdict']}  socials={[s['platform'] for s in lead['socials']]}")
    research.harvest(lid)
    print("[research] raw bundle harvested")
    b = bible.generate(lid)
    print(f"[bible]  v{b['version']}  ({len(b['reviews'])} reviews, "
          f"{len(b['competitors'])} competitors, {len([g for g in b['gap_matrix'] if not g['prospect_has']])} open gaps)")
    m = build.build(lid)
    print(f"[build]  {m['output_dir']}")
    p = pitch.generate(lid)
    rec = next(t for t in p["tiers"] if t.get("recommended"))
    print(f"[pitch]  v{p['bible_version']}  recommended tier: {rec['name']} "
          f"({p['currency']} {rec['monthly_low']}-{rec['monthly_high']}/mo)")
    print("\n[provision --dry-run]")
    print(_provision_dry_run(lid))
    site = ROOT / m["output_dir"] / "index.html"
    print(f"""
DONE — {lead['name']}
  preview:   open {site}
  bible:     data/leads/{lid}/bible/v{m['bible_version']}.json
  pitch:     data/leads/{lid}/pitch/  (json + html)
  spend:     ${store.spend(lid):.2f} of ${settings()['cost_cap_usd_per_lead']:.2f} cap
  dashboard: .venv/bin/python dashboard/app.py  ->  http://127.0.0.1:{settings()['dashboard_port']}/lead/{lid}
""")


def main() -> None:
    ap = argparse.ArgumentParser(prog="socialite")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="full pipeline: find -> bible -> build -> pitch -> provision dry-run")
    p.add_argument("query", help='"Business Name, Town[, Country]"')
    p.add_argument("--locale", default="uk")

    p = sub.add_parser("find", help="qualify one business")
    p.add_argument("query")
    p.add_argument("--locale", default="uk")

    p = sub.add_parser("find-locale", help="sweep a locale for qualified leads")
    p.add_argument("--locale", required=True)
    p.add_argument("--limit", type=int, default=25)

    for name in ("research", "bible", "build", "pitch"):
        p = sub.add_parser(name)
        p.add_argument("lead_id")
        if name == "bible":
            p.add_argument("--force", action="store_true")
        if name == "build":
            p.add_argument("--bible-version", type=int, default=None)
            p.add_argument("--theme", default=None)

    sub.add_parser("dashboard", help="start the team dashboard")
    p = sub.add_parser("status", help="lead pipeline at a glance")

    args = ap.parse_args()
    if args.cmd == "run":
        cmd_run(args)
    elif args.cmd == "find":
        print(json.dumps(find.find_single(args.query, args.locale), indent=2))
    elif args.cmd == "find-locale":
        leads = find.find_locale(args.locale, args.limit)
        for l in leads:
            print(f"{l['qualification']['score']:>3}  {l['id']:<40} website={l['website']['verdict']}")
    elif args.cmd == "research":
        research.harvest(args.lead_id)
    elif args.cmd == "bible":
        print(json.dumps(bible.generate(args.lead_id, force=args.force), indent=2)[:2000])
    elif args.cmd == "build":
        print(json.dumps(build.build(args.lead_id, args.bible_version, args.theme), indent=2))
    elif args.cmd == "pitch":
        pitch.generate(args.lead_id)
    elif args.cmd == "dashboard":
        subprocess.run([sys.executable, str(ROOT / "dashboard" / "app.py")])
    elif args.cmd == "status":
        with store.db() as conn:
            for r in conn.execute("SELECT id, name, status, score FROM leads ORDER BY updated_at DESC"):
                print(f"{r['status']:>8}  {r['score']:>3}  {r['id']:<40} {r['name']}")


if __name__ == "__main__":
    main()
