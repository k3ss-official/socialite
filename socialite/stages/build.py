"""BUILD: render a static site bundle from a bible version. Static output because the
product is a landing page: zero runtime, deploys anywhere nginx can point at a folder."""
from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .. import contracts, store
from .. import bible_v2
from ..config import ROOT, locale as load_locale, settings
from .find import research_context


def build(lead_id: str, bible_version: int | None = None, theme: str | None = None) -> dict:
    lead = store.get_lead(lead_id)
    theme = theme or settings()["default_theme"]
    bdir = store.lead_dir(lead_id) / "bible"
    bible_version = bible_version or store.latest_version(bdir)
    if not bible_version:
        raise SystemExit(f"No bible for {lead_id} — run the bible stage first.")
    bible = store.load_json(bdir / f"v{bible_version}.json")
    review = None
    if bible.get('schema_version') == '2.0':
        review = bible_v2.load_review(lead_id, bible_version)
        bible, lead = bible_v2.project(bible, review)
    contracts.validate(bible, 'bible')
    loc = load_locale(lead["locale"]["key"])

    theme_dir = ROOT / "templates" / "site" / theme
    sdir = store.lead_dir(lead_id) / "site"

    # identical inputs -> identical bundle; don't spam versions
    h0 = hashlib.sha256((bdir / f"v{bible_version}.json").read_bytes())
    if review:
        h0.update(json.dumps(review, sort_keys=True).encode())
    h0.update(json.dumps({'lead': research_context(lead), 'locale': loc}, sort_keys=True).encode())
    raw = store.lead_dir(lead_id) / 'raw'
    for photo in bible.get('photos', []):
        src = raw / photo['path']
        if not src.resolve().is_relative_to(raw.resolve()):
            raise ValueError('Photo must be inside the raw asset directory')
        if src.is_file():
            h0.update(photo['path'].encode())
            h0.update(src.read_bytes())
    for tpl in sorted(theme_dir.rglob("*")):
        if tpl.is_file():
            h0.update(tpl.read_bytes())
    inputs_hash = h0.hexdigest()[:16]
    latest = store.latest_version(sdir)
    if latest:
        prior = store.load_json(sdir / f"v{latest}" / "build-manifest.json")
        if prior.get("inputs_hash") == inputs_hash and prior.get("theme") == theme:
            store.advance_status(lead_id, "built")
            store.log_event("build", "reuse_existing", "skipped", lead_id, version=latest,
                            reason="bible + theme unchanged")
            return prior

    version = store.next_version(sdir)
    sdir.mkdir(parents=True, exist_ok=True)
    out = Path(tempfile.mkdtemp(prefix='.building-', dir=sdir))
    (out / "assets" / "img").mkdir(parents=True, exist_ok=True)

    # copy referenced photos into the bundle so it is fully self-contained
    raw = store.lead_dir(lead_id) / "raw"
    photos = []
    for p in bible.get("photos", []):
        src = raw / p["path"]
        if src.exists():
            dest = out / "assets" / "img" / src.name
            shutil.copy2(src, dest)
            photos.append({**p, "path": f"assets/img/{src.name}"})
    hero = next((p for p in photos if p["use"] == "hero"), photos[0] if photos else None)

    env = Environment(loader=FileSystemLoader(theme_dir), autoescape=True)
    ctx = {"bible": bible, "lead": lead, "locale": loc, "photos": photos, "hero": hero,
           "gallery": [p for p in photos if p["use"] in ("gallery", "menu") and p is not hero]}
    files = []
    for tpl in theme_dir.glob("*.j2"):
        rendered = env.get_template(tpl.name).render(**ctx)
        target = out / tpl.name.removesuffix(".j2")
        target.write_text(rendered)
        files.append(target.name)
    static = theme_dir / "static"
    if static.exists():
        shutil.copytree(static, out / "assets", dirs_exist_ok=True)
    files += [f"assets/img/{p['path'].split('/')[-1]}" for p in photos]

    final = sdir / f'v{version}'
    manifest = {"lead_id": lead_id, "bible_version": bible_version, "theme": theme,
                "built_at": store.now(), "inputs_hash": inputs_hash,
                "output_dir": str(final.relative_to(ROOT)), "files": sorted(files),
                "site_version": version}
    contracts.validate(manifest, "build-manifest")
    store.save_json(out / "build-manifest.json", manifest)
    out.rename(final)
    store.advance_status(lead_id, "built")
    store.log_event("build", "site_built", "ok", lead_id, artifact=manifest["output_dir"],
                    version=version, bible_version=bible_version, theme=theme)
    return manifest
