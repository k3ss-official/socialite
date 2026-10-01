"""Durable local worker queue; stages remain callable by another future harness."""
from __future__ import annotations

import json
from uuid import uuid4

from . import bible_v2, store

ACTIVE = ('queued', 'running', 'cancel_requested')


class Cancelled(RuntimeError):
    pass


def db():
    conn = store.db()
    conn.executescript('''
      CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY, lead_id TEXT NOT NULL, kind TEXT NOT NULL,
        status TEXT NOT NULL, stage TEXT NOT NULL, requested_by TEXT NOT NULL,
        created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
        payload TEXT NOT NULL, result TEXT NOT NULL, error TEXT
      );
      CREATE UNIQUE INDEX IF NOT EXISTS one_active_job_per_lead ON jobs(lead_id)
        WHERE status IN ('queued','running','cancel_requested');
    ''')
    return conn


def decode(row) -> dict | None:
    if row is None:
        return None
    item = dict(row)
    item['payload'], item['result'] = json.loads(item['payload']), json.loads(item['result'])
    return item


def get(job_id: str) -> dict | None:
    with db() as conn:
        return decode(conn.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone())


def for_lead(lead_id: str) -> list[dict]:
    with db() as conn:
        return [decode(r) for r in conn.execute('SELECT * FROM jobs WHERE lead_id=? ORDER BY created_at DESC,rowid DESC LIMIT 20', (lead_id,))]


def enqueue(lead_id: str, kind: str, requested_by: str, **payload) -> dict:
    store.get_lead(lead_id)
    if kind not in ('research', 'preview') or not requested_by.strip():
        raise ValueError('Select a job type and enter a staff name')
    if kind == 'preview':
        version = int(payload['bible_version'])
        bible = store.load_json(store.lead_dir(lead_id) / 'bible' / f'v{version}.json')
        review = bible_v2.load_review(lead_id, version)
        bible_v2.project(bible, review)  # Fail immediately with actionable missing approvals.
        payload['review_revision'] = review['revision']
    with db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        active = conn.execute("SELECT * FROM jobs WHERE lead_id=? AND status IN ('queued','running','cancel_requested')", (lead_id,)).fetchone()
        if active:
            return decode(active)
        job_id, ts = uuid4().hex, store.now()
        conn.execute('INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                     (job_id, lead_id, kind, 'queued', 'queued', requested_by.strip(), ts, ts,
                      json.dumps(payload), '{}', None))
    store.log_event('jobs', 'queued', lead_id=lead_id, job_id=job_id, kind=kind, requested_by=requested_by.strip())
    return get(job_id)


def cancel(job_id: str) -> None:
    with db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        conn.execute("UPDATE jobs SET status=CASE WHEN status='queued' THEN 'cancelled' ELSE 'cancel_requested' END, updated_at=? WHERE id=? AND status IN ('queued','running')", (store.now(), job_id))


def update(job_id: str, **values) -> None:
    if not values.keys() <= {'status', 'stage', 'result', 'error'}:
        raise ValueError('Unknown job field')
    if 'result' in values:
        values['result'] = json.dumps(values['result'])
    values['updated_at'] = store.now()
    with db() as conn:
        conn.execute('UPDATE jobs SET ' + ','.join(f'{k}=?' for k in values) + ' WHERE id=?',
                     (*values.values(), job_id))


def recover_interrupted() -> int:
    """Run only with the exclusive worker lock, after the previous worker stopped."""
    with db() as conn:
        cur = conn.execute("UPDATE jobs SET status='failed',error='Worker stopped before completion; retry from the lead page',updated_at=? WHERE status IN ('running','cancel_requested')", (store.now(),))
        return cur.rowcount


def run_next() -> dict | None:
    from .stages import build, pitch, research
    with db() as conn:
        conn.execute('BEGIN IMMEDIATE')
        row = conn.execute("SELECT * FROM jobs WHERE status='queued' ORDER BY created_at,rowid LIMIT 1").fetchone()
        if row is None:
            return None
        job = decode(row)
        conn.execute("UPDATE jobs SET status='running',updated_at=? WHERE id=?", (store.now(), job['id']))
    job_id, lead_id = job['id'], job['lead_id']
    result = {}
    def check_cancel():
        if get(job_id)['status'] == 'cancel_requested':
            raise Cancelled('Cancelled after the current operation completed')
    try:
        check_cancel()
        if job['kind'] == 'research':
            update(job_id, stage='collecting')
            bundle = research.harvest(lead_id, force=bool(job['payload'].get('force')), check_cancel=check_cancel)
            result['source_count'] = len(bundle['fetched'])
            result['collection_failures'] = sum(f.get('outcome') != 'captured' for f in bundle['fetched'])
            update(job_id, result=result)
            check_cancel()
            update(job_id, stage='synthesizing')
            bible = bible_v2.generate(lead_id, bundle)
            result['bible_version'] = bible['version']
            check_cancel()
            update(job_id, status='review', stage='awaiting_review', result=result)
        else:
            version = int(job['payload']['bible_version'])
            if bible_v2.load_review(lead_id, version).get('revision') != job['payload']['review_revision']:
                raise ValueError('Review changed since this job was queued; queue a new preview')
            update(job_id, stage='building')
            manifest = build.build(lead_id, bible_version=version)
            result['site_version'] = manifest['site_version']
            check_cancel()
            update(job_id, stage='pitching', result=result)
            proposal = pitch.generate(lead_id, bible_version=version)
            result.update(bible_version=version, pitch_version=proposal['version'])
            check_cancel()
            update(job_id, status='succeeded', stage='complete', result=result)
    except Cancelled as exc:
        update(job_id, status='cancelled', error=str(exc), result=result)
    except (Exception, SystemExit) as exc:
        message = str(exc)[:500]
        update(job_id, status='failed', error=message, result=result)
        store.log_event('jobs', 'failed', 'error', lead_id, job_id=job_id, stage_name=get(job_id)['stage'], error=message)
    except KeyboardInterrupt:
        update(job_id, status='failed', error='Worker interrupted; retry from the lead page', result=result)
        raise
    return get(job_id)
