"""One-time local migration: retain one pilot and remove old demo runtime data.

Stop the dashboard and worker first. A timestamped data backup and SQLite backup
are completed before records are removed. This is deletion, not an archive view.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import shutil
import sys
import tarfile
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from socialite import store


def focus(keep: str, backup_dir: Path) -> dict:
    data = store.data_dir()
    lead = store.get_lead(keep)
    if lead['id'] != keep:
        raise ValueError('The retained lead does not match its folder')
    if backup_dir.resolve().is_relative_to(data.resolve()):
        raise ValueError('Choose a backup location outside the data folder')
    with open(data / '.worker.lock', 'a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Stop the worker before focusing the pilot') from None
        path = data / 'events.jsonl'
        events = [json.loads(s) for s in path.read_text().splitlines() if s.strip()] if path.exists() else []
        kept_events = [event for event in events if event.get('lead_id') == keep]
        removed = [p for p in (data / 'leads').iterdir() if p.is_dir() and p.name != keep]
        backup = backup_dir / ('socialite-focus-' + store.now().replace(':', '').replace('+', '_') + '-' + uuid4().hex[:8])
        backup.mkdir(parents=True, exist_ok=False)
        store.backup_database(backup / 'ledger.sqlite')
        with tarfile.open(backup / 'data.tar.gz', 'w:gz') as archive:
            archive.add(data, arcname='data')
        store.save_json(backup / 'manifest.json', {'kept': keep, 'created_at': store.now(),
                                                  'removed_folders': [p.name for p in removed]})
        # The worker lock serializes this migration with the CLI worker; callers
        # must also stop the dashboard to prevent new staff submissions.
        with store.db() as conn:
            conn.execute('BEGIN IMMEDIATE')
            tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            conn.execute('DELETE FROM services WHERE NOT EXISTS (SELECT 1 FROM clients c WHERE c.id=services.client_id AND c.lead_id=?)', (keep,))
            conn.execute('DELETE FROM clients WHERE lead_id<>?', (keep,))
            if 'jobs' in tables:
                conn.execute('DELETE FROM jobs WHERE lead_id<>?', (keep,))
            for folder in removed:
                if folder.is_symlink():
                    folder.unlink()
                else:
                    shutil.rmtree(folder)
            temporary = data / '.focus-events.jsonl'
            temporary.write_text(''.join(json.dumps(event, ensure_ascii=False) + '\n' for event in kept_events))
            temporary.replace(path)
            store._rebuild_index(conn)
        result = {'kept': keep, 'removed_lead_folders': len(removed),
                  'removed_events': len(events) - len(kept_events), 'backup': str(backup)}
        store.log_event('maintenance', 'focus_pilot', lead_id=keep, **result)
        return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--keep', default='alo-soft-play-hire-lancashire')
    parser.add_argument('--backup-dir', required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(focus(args.keep, args.backup_dir), indent=2))
    except (ValueError, FileNotFoundError) as exc:
        raise SystemExit(str(exc)) from exc
