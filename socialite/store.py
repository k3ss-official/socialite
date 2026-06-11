"""Persistence: artifact tree on disk (source of truth), SQLite index (dashboard),
structured event log (data/events.jsonl), and the per-lead cost ledger with kill switch.

Layout per lead:
  data/leads/<id>/lead.json
  data/leads/<id>/raw/            research harvest (pages/, images/, search.json)
  data/leads/<id>/bible/v<N>.json
  data/leads/<id>/site/v<N>/      static bundle + build-manifest.json
  data/leads/<id>/pitch/v<N>.json + v<N>.html
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .config import data_dir, settings

LEAD_STATUSES = ["found", "bible", "built", "pitched", "signed", "rejected"]


class CostCapExceeded(RuntimeError):
    pass


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(data_dir() / "db.sqlite")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS leads (
      id TEXT PRIMARY KEY, name TEXT, locale_key TEXT, status TEXT,
      score INTEGER, created_at TEXT, updated_at TEXT, json TEXT
    );
    CREATE TABLE IF NOT EXISTS events (
      id INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT, lead_id TEXT, stage TEXT,
      action TEXT, status TEXT, cost_usd REAL DEFAULT 0, artifact TEXT,
      version INTEGER, details TEXT
    );
    CREATE TABLE IF NOT EXISTS clients (
      id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id TEXT UNIQUE, signed_at TEXT, notes TEXT
    );
    -- Service ledger: one row per rung a client is on. `schedule` and `state`
    -- are JSON blobs reserved for the Phase 2 service engine (cadence, next_run,
    -- per-rung delivery state) — populated minimally now, never repurposed.
    CREATE TABLE IF NOT EXISTS services (
      id INTEGER PRIMARY KEY AUTOINCREMENT, client_id INTEGER, rung_key TEXT,
      name TEXT, monthly_value REAL, currency TEXT, start_date TEXT,
      renewal_date TEXT, status TEXT DEFAULT 'active', schedule TEXT, state TEXT
    );
    """)
    return conn


# ---------- artifact paths ----------

def lead_dir(lead_id: str) -> Path:
    d = data_dir() / "leads" / lead_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def next_version(parent: Path, pattern: str = "v*") -> int:
    parent.mkdir(parents=True, exist_ok=True)
    versions = [int(p.name.lstrip("v").split(".")[0]) for p in parent.glob(pattern) if p.name.lstrip("v").split(".")[0].isdigit()]
    return max(versions, default=0) + 1


def latest_version(parent: Path) -> int | None:
    if not parent.exists():
        return None
    versions = [int(p.name.lstrip("v").split(".")[0]) for p in parent.glob("v*") if p.name.lstrip("v").split(".")[0].isdigit()]
    return max(versions, default=None)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def save_json(path: Path, obj: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False))
    return path


# ---------- events ----------

def log_event(stage: str, action: str, status: str = "ok", lead_id: str | None = None,
              cost_usd: float = 0.0, artifact: str | None = None,
              version: int | None = None, **details) -> None:
    event = {"ts": now(), "lead_id": lead_id, "stage": stage, "action": action,
             "status": status, "cost_usd": round(cost_usd, 6), "artifact": artifact,
             "version": version, "details": details}
    with open(data_dir() / "events.jsonl", "a") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")
    with db() as conn:
        conn.execute(
            "INSERT INTO events (ts, lead_id, stage, action, status, cost_usd, artifact, version, details) "
            "VALUES (?,?,?,?,?,?,?,?,?)",
            (event["ts"], lead_id, stage, action, status, event["cost_usd"], artifact, version,
             json.dumps(details, ensure_ascii=False)))


# ---------- cost ledger / kill switch ----------

def spend(lead_id: str) -> float:
    with db() as conn:
        row = conn.execute("SELECT COALESCE(SUM(cost_usd),0) s FROM events WHERE lead_id=?",
                           (lead_id,)).fetchone()
    return float(row["s"])


def ensure_budget(lead_id: str, estimated_next_usd: float = 0.25) -> None:
    """Kill switch: refuse the next billable action if it would blow the per-lead cap."""
    cap = float(settings()["cost_cap_usd_per_lead"])
    spent = spend(lead_id)
    if spent + estimated_next_usd > cap:
        log_event("find", "cost_cap_kill_switch", "capped", lead_id,
                  spent_usd=spent, cap_usd=cap, estimated_next_usd=estimated_next_usd)
        raise CostCapExceeded(
            f"Lead {lead_id}: spent ${spent:.2f}, next action ~${estimated_next_usd:.2f} "
            f"would exceed cap ${cap:.2f}. Raise cost_cap_usd_per_lead in config/settings.yaml to continue.")


# ---------- leads ----------

def upsert_lead(lead: dict) -> None:
    save_json(lead_dir(lead["id"]) / "lead.json", lead)
    with db() as conn:
        conn.execute(
            "INSERT INTO leads (id, name, locale_key, status, score, created_at, updated_at, json) "
            "VALUES (?,?,?,?,?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name, "
            "status=excluded.status, score=excluded.score, updated_at=excluded.updated_at, json=excluded.json",
            (lead["id"], lead["name"], lead["locale"]["key"], lead["status"],
             lead["qualification"]["score"], lead["created_at"], lead.get("updated_at", now()),
             json.dumps(lead, ensure_ascii=False)))


def get_lead(lead_id: str) -> dict:
    return load_json(lead_dir(lead_id) / "lead.json")


def set_status(lead_id: str, status: str) -> None:
    assert status in LEAD_STATUSES, status
    lead = get_lead(lead_id)
    lead["status"] = status
    lead["updated_at"] = now()
    upsert_lead(lead)
    log_event("ledger", f"status:{status}", "ok", lead_id)


def advance_status(lead_id: str, status: str) -> None:
    """Forward-only: a pipeline stage may pull a lead up to its stage, never push it
    back (a rebuild must not regress a pitched or signed lead). Manual moves in the
    dashboard use set_status and can go anywhere."""
    lead = get_lead(lead_id)
    order = LEAD_STATUSES.index
    if lead["status"] != "rejected" and order(status) > order(lead["status"]):
        set_status(lead_id, status)


# ---------- clients & service ledger ----------

def sign_lead(lead_id: str, rung_keys: list[str], monthly_values: dict[str, float],
              currency: str, start_date: str | None = None) -> int:
    """Convert a pitched lead into a client with one service row per rung."""
    from .config import ladder
    start = start_date or now()[:10]
    renewal = f"{int(start[:4]) + 1}{start[4:]}"
    with db() as conn:
        cur = conn.execute("INSERT OR IGNORE INTO clients (lead_id, signed_at) VALUES (?,?)",
                           (lead_id, now()))
        client_id = cur.lastrowid or conn.execute(
            "SELECT id FROM clients WHERE lead_id=?", (lead_id,)).fetchone()["id"]
        for key in rung_keys:
            rung = ladder()["rungs"][key]
            schedule = json.dumps({"cadence_per_year": rung.get("cadence_per_year")})
            conn.execute(
                "INSERT INTO services (client_id, rung_key, name, monthly_value, currency, "
                "start_date, renewal_date, schedule, state) VALUES (?,?,?,?,?,?,?,?,?)",
                (client_id, key, rung["name"], monthly_values.get(key, 0), currency,
                 start, renewal, schedule, json.dumps({})))
    set_status(lead_id, "signed")
    log_event("ledger", "signed", "ok", lead_id, rungs=rung_keys)
    return client_id


def mrr_rollup() -> dict:
    """MRR per currency across active services, plus a 3-year ~10%/yr attrition projection."""
    with db() as conn:
        rows = conn.execute(
            "SELECT currency, COALESCE(SUM(monthly_value),0) mrr, COUNT(*) n "
            "FROM services WHERE status='active' GROUP BY currency").fetchall()
    out = {}
    for r in rows:
        mrr = float(r["mrr"])
        out[r["currency"]] = {
            "mrr": mrr, "active_services": r["n"],
            "projection": [round(mrr * (0.9 ** y), 2) for y in range(4)],  # y0..y3 at 10%/yr attrition
        }
    return out
