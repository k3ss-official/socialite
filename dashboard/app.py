"""Socialite internal dashboard — server-rendered Flask, no auth, internal only.

Run from repo root in the socialite Conda environment: python dashboard/app.py
"""
from __future__ import annotations

import json
import os
import re
import secrets
import sys
from pathlib import Path

# Bootstrap so `import socialite` works when run as dashboard/app.py from repo root.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import (Flask, abort, flash, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)

from socialite import bible_v2, jobs, store
from socialite.config import data_dir, ladder, settings

app = Flask(__name__)
app.secret_key = os.environ.get('SOCIALITE_SESSION_SECRET') or secrets.token_hex(32)
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Strict', MAX_CONTENT_LENGTH=1024*1024)


@app.before_request
def protect_forms():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    if request.method == 'POST' and not secrets.compare_digest(request.form.get('csrf_token', ''), session['csrf_token']):
        abort(400, description='This form expired. Reload the page and try again.')

LEAD_ID_RE = re.compile(r"^[a-z0-9-]+$")
PIPELINE = ["found", "bible", "built", "pitched", "signed", "live"]


# ---------- helpers ----------

def q(sql: str, params: tuple = ()) -> list:
    conn = store.db()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def lead_path(lead_id: str) -> Path:
    """Read-only artifact path for a lead. Never mkdirs, 404s bad ids."""
    if not LEAD_ID_RE.match(lead_id or ""):
        abort(404)
    return data_dir() / "leads" / lead_id


def load_lead(lead_id: str) -> dict | None:
    p = lead_path(lead_id) / "lead.json"
    if not p.exists():
        return None
    try:
        return store.load_json(p)
    except (ValueError, OSError):
        return None


def file_versions(parent: Path, suffix: str) -> list[int]:
    """Sorted versions for files named v<N><suffix> under parent."""
    if not parent.is_dir():
        return []
    out = []
    for p in parent.glob(f"v*{suffix}"):
        stem = p.name[1:len(p.name) - len(suffix)] if suffix else p.name[1:]
        if stem.isdigit():
            out.append(int(stem))
    return sorted(out)


def dir_versions(parent: Path) -> list[int]:
    if not parent.is_dir():
        return []
    return sorted(int(p.name[1:]) for p in parent.glob("v*")
                  if p.is_dir() and p.name[1:].isdigit())


def latest_pitch_json(lead_id: str) -> dict | None:
    pdir = lead_path(lead_id) / "pitch"
    vs = file_versions(pdir, ".json")
    if not vs:
        return None
    try:
        return store.load_json(pdir / f"v{vs[-1]}.json")
    except (ValueError, OSError):
        return None


@app.template_filter("money")
def money(v) -> str:
    try:
        return f"{float(v):,.2f}"
    except (TypeError, ValueError):
        return "0.00"


@app.template_filter("ts")
def short_ts(v) -> str:
    return (v or "").replace("T", " ").replace("+00:00", "")[:19]


@app.context_processor
def inject_globals():
    return {"PIPELINE": PIPELINE, "LEAD_STATUSES": store.LEAD_STATUSES,
            'csrf_token': session.get('csrf_token', '')}


# ---------- routes ----------

@app.get("/")
def board():
    rows = q("SELECT * FROM leads ORDER BY updated_at DESC")
    cols = {s: [] for s in PIPELINE}
    rejected = 0
    for r in rows:
        if r["status"] == "rejected":
            rejected += 1
        elif r["status"] in cols:
            cols[r["status"]].append({
                "id": r["id"], "name": r["name"], "locale_key": r["locale_key"],
                "score": None if json.loads(r['json'])['qualification'].get('score_status') == 'not_run' else r["score"],
                "spend": store.spend(r["id"]),
            })
    return render_template("board.html", cols=cols, rejected=rejected)


@app.get("/lead/<lead_id>")
def lead_detail(lead_id):
    lead = load_lead(lead_id)
    if lead is None:
        abort(404)
    base = lead_path(lead_id)
    spend = store.spend(lead_id)
    cap = float(settings()["cost_cap_usd_per_lead"])
    pct = (spend / cap * 100) if cap else 0.0

    cost_events = q("SELECT * FROM events WHERE lead_id=? AND cost_usd>0 "
                    "ORDER BY id DESC LIMIT 100", (lead_id,))
    recent_events = q("SELECT * FROM events WHERE lead_id=? "
                      "ORDER BY id DESC LIMIT 30", (lead_id,))

    # Sign form: ladder rungs + prefill from latest pitch JSON.
    sign = None
    if lead.get("status") == "pitched":
        pitch = latest_pitch_json(lead_id) or {}
        pitch_rungs = {r.get("key"): r for r in pitch.get("rungs", [])}
        rungs = []
        for key, rung in ladder()["rungs"].items():
            pr = pitch_rungs.get(key, {})
            rungs.append({
                "key": key, "name": rung["name"], "kind": rung.get("kind", ""),
                "monthly_low": pr.get("monthly_low", 0),
                "recommended": bool(pr.get("recommended")),
            })
        sign = {"rungs": rungs,
                "currency": pitch.get("currency",
                                      lead.get("locale", {}).get("currency", "GBP"))}

    return render_template(
        "lead.html", lead=lead, spend=spend, cap=cap, pct=pct,
        evidence=lead.get("qualification", {}).get("evidence", []),
        bible_versions=file_versions(base / "bible", ".json"),
        pitch_versions=file_versions(base / "pitch", ".html"),
        site_versions=dir_versions(base / "site"),
        cost_events=cost_events, recent_events=recent_events, sign=sign,
        jobs=jobs.for_lead(lead_id))


@app.post("/lead/<lead_id>/status")
def advance_status(lead_id):
    if load_lead(lead_id) is None:
        abort(404)
    status = request.form.get("status", "")
    if status in store.LEAD_STATUSES:
        store.set_status(lead_id, status)
    return redirect(url_for("lead_detail", lead_id=lead_id))


@app.post("/lead/<lead_id>/sign")
def sign(lead_id):
    lead = load_lead(lead_id)
    if lead is None:
        abort(404)
    rung_keys = [k for k in request.form.getlist("rungs") if k in ladder()["rungs"]]
    if rung_keys:
        values = {}
        for key in rung_keys:
            try:
                values[key] = float(request.form.get(f"value_{key}", 0) or 0)
            except ValueError:
                values[key] = 0.0
        currency = request.form.get("currency") or lead.get("locale", {}).get("currency", "GBP")
        try:
            store.sign_lead(lead_id, rung_keys, values, currency)
        except ValueError as exc:
            flash(str(exc))
    return redirect(url_for("lead_detail", lead_id=lead_id))


@app.get("/lead/<lead_id>/bible/<int:v>")
def bible_view(lead_id, v):
    path = lead_path(lead_id) / "bible" / f"v{v}.json"
    if not path.exists():
        abort(404)
    try:
        bible = store.load_json(path)
    except (ValueError, OSError):
        abort(404)
    palette = bible.get("palette", {}) or {}
    if bible.get('schema_version') == '2.0':
        bible_v2.validate(bible)
        review = bible_v2.load_review(lead_id, v)
        evidence = {e['id']: e for e in bible['evidence']}
        allowed = {c['id']: bible_v2.approvable(c, evidence) for c in bible['claims']}
        return render_template('bible_v2.html', lead_id=lead_id, v=v, bible=bible,
                               review=review, approvable=allowed)
    swatches = [(k, palette[k]) for k in
                ("primary", "secondary", "accent", "background", "text")
                if isinstance(palette.get(k), str)]
    photos = []
    for ph in bible.get("photos", []) or []:
        rel = (ph.get("path") or "").removeprefix("raw/").removeprefix("images/").lstrip("/")
        if rel:
            photos.append({**ph, "rel": rel})
    return render_template("bible.html", lead_id=lead_id, v=v, bible=bible,
                           swatches=swatches, photos=photos)


@app.post('/lead/<lead_id>/research')
def start_research(lead_id):
    if load_lead(lead_id) is None:
        abort(404)
    try:
        job = jobs.enqueue(lead_id, 'research', request.form.get('staff_name', ''),
                           force=request.form.get('force') == 'yes')
        flash(f"Research {job['status']}. The worker processes queued jobs.")
    except ValueError as exc:
        flash(str(exc))
    return redirect(url_for('lead_detail', lead_id=lead_id))


@app.get('/lead/<lead_id>/bible/<int:v>/report')
def bible_report(lead_id, v):
    path = lead_path(lead_id) / 'bible' / f'v{v}.json'
    lead = load_lead(lead_id)
    if lead is None or not path.exists():
        abort(404)
    bible = store.load_json(path)
    if bible.get('schema_version') != '2.0':
        abort(400, description='The report format uses Bible v2. Start research from the prospect page.')
    bible_v2.validate(bible)
    return render_template('bible_report.html', bible=bible, lead=lead,
                           review=bible_v2.load_review(lead_id, v), sections=bible_v2.SECTIONS)


@app.post('/lead/<lead_id>/bible/<int:v>/review')
def review_bible(lead_id, v):
    path = lead_path(lead_id) / 'bible' / f'v{v}.json'
    if not path.exists():
        abort(404)
    bible = store.load_json(path)
    if bible.get('schema_version') != '2.0':
        abort(400, description='Research this prospect again to create a Bible v2 review')
    decisions = {c['id']: request.form.get('claim_' + c['id'], 'hold') for c in bible['claims']}
    approved_assets = {}
    for asset in bible['assets']:
        key = asset['id']
        if request.form.get('asset_' + key) == 'yes':
            approved_assets[key] = {'rights': request.form.get('rights_' + key, ''),
                                    'note': request.form.get('note_' + key, ''),
                                    'use': request.form.get('use_' + key, '')}
    try:
        bible_v2.save_review(bible, decisions, approved_assets, request.form.get('reviewer', ''),
                            request.form.get('note', ''), int(request.form.get('revision', '0')))
        flash('Review saved. Only approved source-backed page fields enter the preview.')
    except ValueError as exc:
        flash(str(exc))
    return redirect(url_for('bible_view', lead_id=lead_id, v=v))


@app.post('/lead/<lead_id>/bible/<int:v>/preview')
def start_preview(lead_id, v):
    if load_lead(lead_id) is None:
        abort(404)
    try:
        if not (lead_path(lead_id) / 'bible' / f'v{v}.json').is_file():
            abort(404)
        job = jobs.enqueue(lead_id, 'preview', request.form.get('staff_name', ''), bible_version=v)
        flash(f"Preview {job['status']}.")
    except ValueError as exc:
        flash(str(exc))
    return redirect(url_for('lead_detail', lead_id=lead_id))


@app.get('/lead/<lead_id>/bible/<int:v>/evidence/<evidence_id>')
def evidence_view(lead_id, v, evidence_id):
    path = lead_path(lead_id) / 'bible' / f'v{v}.json'
    if not path.exists():
        abort(404)
    bible = store.load_json(path)
    entry = next((e for e in bible.get('evidence', []) if e['id'] == evidence_id), None)
    if entry is None:
        abort(404)
    content = entry['excerpt']
    if entry['capture_file']:
        raw = lead_path(lead_id) / 'raw'
        capture = (raw / entry['capture_file']).resolve()
        if not capture.is_relative_to(raw.resolve()):
            abort(404)
        if capture.is_file():
            content = capture.read_text()
    return render_template('evidence.html', entry=entry, content=content, lead_id=lead_id, v=v)


@app.get('/job/<job_id>')
def job_status(job_id):
    job = jobs.get(job_id)
    if job is None:
        abort(404)
    return jsonify(job)


@app.post('/job/<job_id>/cancel')
def cancel_job(job_id):
    job = jobs.get(job_id)
    if job is None:
        abort(404)
    jobs.cancel(job_id)
    flash('Cancellation requested. A running job finishes its current operation first.')
    return redirect(url_for('lead_detail', lead_id=job['lead_id']))


@app.errorhandler(400)
def bad_request(e):
    return render_template('error.html', code=400, message=e.description), 400


@app.get("/lead/<lead_id>/raw/images/<path:p>")
def raw_image(lead_id, p):
    d = lead_path(lead_id) / "raw" / "images"
    if not d.is_dir():
        abort(404)
    return send_from_directory(d, p)


@app.get("/lead/<lead_id>/pitch/<int:v>")
def pitch_view(lead_id, v):
    d = lead_path(lead_id) / "pitch"
    if not (d / f"v{v}.html").exists():
        abort(404)
    return send_from_directory(d, f"v{v}.html")


@app.get("/preview/<lead_id>/<int:v>/", defaults={"p": "index.html"})
@app.get("/preview/<lead_id>/<int:v>/<path:p>")
def preview(lead_id, v, p):
    d = lead_path(lead_id) / "site" / f"v{v}"
    if not d.is_dir():
        abort(404)
    if (d / p).is_dir():
        p = f"{p.rstrip('/')}/index.html"
    return send_from_directory(d, p)


@app.get("/clients")
def clients():
    rollup = store.mrr_rollup()
    rows = q("SELECT c.id, c.lead_id, c.signed_at, COALESCE(l.name, c.lead_id) AS name "
             "FROM clients c LEFT JOIN leads l ON l.id = c.lead_id "
             "ORDER BY c.signed_at DESC")
    client_list = []
    for c in rows:
        services = q("SELECT * FROM services WHERE client_id=? ORDER BY id", (c["id"],))
        totals: dict[str, float] = {}
        for s in services:
            if s["status"] == "active":
                cur = s["currency"] or "?"
                totals[cur] = totals.get(cur, 0.0) + float(s["monthly_value"] or 0)
        client_list.append({"id": c["id"], "lead_id": c["lead_id"], "name": c["name"],
                            "signed_at": c["signed_at"], "services": services,
                            "totals": totals})
    return render_template("clients.html", rollup=rollup, clients=client_list)


@app.get("/events")
def events():
    rows = q("SELECT * FROM events ORDER BY id DESC LIMIT 200")
    return render_template("events.html", events=rows)


# ---------- error pages ----------

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", code=404,
                           message="Nothing here. The artifact or lead doesn't exist yet."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", code=500,
                           message="Something broke server-side. Check the terminal."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(settings()["dashboard_port"]), debug=False)
