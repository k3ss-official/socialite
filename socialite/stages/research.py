"""RESEARCH: harvest the public web for one lead into data/leads/<id>/raw/.
Free (requests only). The raw bundle is the reproducible input to BIBLE.

Order of trust: (1) the lead's own known URLs — their site/template page, socials,
evidence pages from FIND; (2) name-matched search results; (3) competitor-survey
results (text only, never images). Pages that never mention the business are skipped.
Collection limits and source caveats are documented in docs/RESEARCH-SOURCES.md."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from uuid import uuid4

import requests
from bs4 import BeautifulSoup

from .. import store
from ..config import settings
from ..web import search as websearch
from ..web.sitecheck import UA
from .find import _name_matches, prospect_area, research_context

MAX_PAGES = 14
MAX_IMAGES = 8
MAX_IMAGE_REQUESTS = 16


def _fetch(url: str, timeout: int = 15) -> requests.Response | None:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
        return r
    except requests.RequestException:
        return None


def _image_urls(soup: BeautifulSoup, base_url: str) -> list[str]:
    urls = []
    for sel, attr in [(("meta", {"property": "og:image"}), "content"),
                      (("meta", {"name": "twitter:image"}), "content")]:
        for tag in soup.find_all(*sel):
            if tag.get(attr):
                urls.append(requests.compat.urljoin(base_url, tag[attr]))
    for img in soup.find_all("img", src=True)[:25]:
        src = requests.compat.urljoin(base_url, img["src"])
        w = img.get("width")
        if w and str(w).isdigit() and int(w) < 200:
            continue
        if any(k in src.lower() for k in ("logo", "icon", "sprite", "avatar", "badge", ".svg", ".gif")):
            continue
        urls.append(src)
    return urls


def harvest(lead_id: str, force: bool = False, check_cancel=None) -> dict:
    lead = store.get_lead(lead_id)
    raw = store.lead_dir(lead_id) / "raw"
    fingerprint = hashlib.sha256(json.dumps(research_context(lead), sort_keys=True).encode()).hexdigest()
    if (raw / "research.json").exists() and not force:
        prior = store.load_json(raw / 'research.json')
        try:
            age = (datetime.now(timezone.utc) - datetime.fromisoformat(prior['harvested_at'])).total_seconds()
        except (KeyError, TypeError, ValueError):
            age = float('inf')
        if prior.get('lead_hash') == fingerprint and 0 <= age < settings().get('research_cache_hours', 24) * 3600 and _captures_intact(raw, prior):
            store.log_event('research', 'reuse_existing', 'skipped', lead_id, reason='fresh matching bundle')
            return prior
        store.log_event('research', 'cache_invalid', lead_id=lead_id,
                        reason='Expired, changed context or missing/changed capture; collecting again')
    (raw / "pages").mkdir(parents=True, exist_ok=True)
    (raw / "images").mkdir(parents=True, exist_ok=True)
    name = lead["name"]
    area = prospect_area(lead)
    town = area.split(",")[0]

    # (1) the lead's own known URLs, highest trust
    def norm(u: str) -> str:
        return u.lower().split("//")[-1].removeprefix("www.").rstrip("/")

    own_urls: list[tuple[str, str]] = []  # (url, kind)
    own_seen: set[str] = set()
    candidates = ([(lead["website"]["url"], "own_site")] if lead["website"]["url"] else [])
    candidates += [(s["url"], f"social:{s['platform']}") for s in lead["socials"]]
    candidates += [(e["url"], "evidence_page") for e in lead["qualification"]["evidence"]
                   if e.get("url") and e["check"] in ("website_check", "contact:phone", "contact:email")]
    for u, kind in candidates:
        if norm(u) not in own_seen:
            own_seen.add(norm(u))
            own_urls.append((u, kind))

    # (2) name-matched search; (3) competitor survey
    category = lead.get('category') or 'business'
    queries = [f'"{name}" {town}', f'"{name}" {town} reviews', f'"{name}" {town} services prices opening hours']
    comp_query = f"{category} {town} competitors reviews"
    results, seen, query_outcomes = [], set(own_seen), []
    for q in queries + [comp_query]:
        if check_cancel:
            check_cancel()
        rows = websearch.search(q, max_results=8)
        query_outcomes.append({'query': q, 'outcome': getattr(rows, 'outcome', 'ok'),
                               'error': getattr(rows, 'error', None), 'result_count': len(rows)})
        for r in rows:
            if norm(r["href"]) in seen:
                continue
            seen.add(norm(r["href"]))
            is_comp = q == comp_query
            if not is_comp and not _name_matches(name, f"{r['title']} {r['body']} {r['href']}"):
                continue
            results.append({**r, "query": q, "kind": "competitor" if is_comp else websearch.classify(r["href"])})

    fetch_list = own_urls + [(r["href"], r["kind"]) for r in results]
    fetches, image_meta, img_seen, img_hashes = [], [], set(), set()
    comp_budget, blocked_domains, image_requests = 3, set(), 0
    for url, kind in fetch_list:
        if check_cancel:
            check_cancel()
        if len(fetches) >= MAX_PAGES:
            break
        if kind == "competitor":
            if comp_budget == 0:
                continue
            comp_budget -= 1
        domain = websearch.domain_of(url)
        resp = None if domain in blocked_domains else _fetch(url)
        rec = {"url": url, "kind": kind, "status": resp.status_code if resp is not None else None,
               "captured_at": store.now(), "evidence_id": 'E-' + uuid4().hex[:16],
               "outcome": 'domain_stopped' if domain in blocked_domains else 'network_unavailable',
               "text_file": None, "metadata": {}}
        if resp is not None:
            rec['outcome'] = 'ok' if resp.status_code == 200 else 'http_error'
            if resp.status_code in (403, 429):
                blocked_domains.add(domain)
                rec['outcome'] = 'access_denied' if resp.status_code == 403 else 'rate_limited'
        if resp is not None and resp.status_code == 200 and "html" in resp.headers.get("content-type", ""):
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup.find_all('meta'):
                key = tag.get('property') or tag.get('name')
                if key in ('description', 'og:title', 'og:description', 'og:image', 'twitter:description'):
                    rec['metadata'][key] = tag.get('content', '')
            for t in soup(["script", "style", "noscript"]):
                t.decompose()
            text = re.sub(r"\n{3,}", "\n\n", soup.get_text("\n", strip=True))
            text = '\n'.join(f'{k}: {v}' for k, v in rec['metadata'].items()) + '\n' + text
            about_them = _name_matches(name, text[:8000])
            if text.strip() and (about_them or kind == "competitor"):
                fname = rec['evidence_id'] + '.txt'
                capture = f"[{kind}] {url}\n\n{text[:40_000]}"
                (raw / 'pages' / fname).write_text(capture)
                rec['content_hash'] = hashlib.sha256(capture.encode()).hexdigest()
                rec["text_file"] = f"pages/{fname}"
                rec['outcome'] = 'captured'
            else:
                rec['outcome'] = 'entity_unmatched' if not about_them and kind != 'competitor' else 'empty_content'
            # images only from pages that are genuinely about the business
            if about_them and kind != "competitor" and len(image_meta) < MAX_IMAGES:
                for iu in _image_urls(soup, url):
                    if check_cancel:
                        check_cancel()
                    if len(image_meta) >= MAX_IMAGES or image_requests >= MAX_IMAGE_REQUESTS or iu in img_seen:
                        continue
                    img_seen.add(iu)
                    if websearch.domain_of(iu) in blocked_domains:
                        continue
                    image_requests += 1
                    ir = _fetch(iu)
                    if ir is not None and ir.status_code in (403, 429):
                        blocked_domains.add(websearch.domain_of(iu))
                    if ir is not None and ir.status_code == 200 and ir.headers.get("content-type", "").startswith("image/") and len(ir.content) > 15_000:
                        digest = hashlib.sha256(ir.content).hexdigest()
                        if digest in img_hashes:
                            continue
                        img_hashes.add(digest)
                        ext = ir.headers["content-type"].split("/")[-1].split(";")[0].replace("jpeg", "jpg")
                        iname = f"{digest[:16]}.{ext}"
                        (raw / "images" / iname).write_bytes(ir.content)
                        image_meta.append({"file": f"images/{iname}", "source": url, 'original_url': iu,
                                           'evidence_id': rec['evidence_id'], 'rights': 'unknown',
                                           'captured_at': rec['captured_at'], 'content_hash': digest, "bytes": len(ir.content)})
        fetches.append(rec)

    bundle = {"lead_id": lead_id, "collection_id": uuid4().hex,
              "harvested_at": store.now(), 'lead_hash': fingerprint,
              'query_outcomes': query_outcomes, "queries": queries + [comp_query],
              "results": results, "fetched": fetches, "images": image_meta}
    # Keep each collection attempt independently. A failed refresh must not erase
    # earlier receipts or silently substitute older information as fresh research.
    if (raw / 'research.json').exists():
        previous = store.load_json(raw / 'research.json')
        identity = previous.get('collection_id') or hashlib.sha256(json.dumps(previous, sort_keys=True).encode()).hexdigest()
        history = raw / 'history' / f'{identity}.json'
        if not history.exists():
            store.save_json(history, previous)
    store.save_json(raw / 'history' / (bundle['collection_id'] + '.json'), bundle)
    store.save_json(raw / "research.json", bundle)
    store.log_event("research", "harvest", "ok", lead_id, artifact=f"data/leads/{lead_id}/raw/research.json",
                    pages=len([f for f in fetches if f["text_file"]]), images=len(image_meta),
                    results=len(results))
    return bundle


def _captures_intact(raw, bundle: dict) -> bool:
    for item in bundle.get('fetched', []) + bundle.get('images', []):
        relative = item.get('text_file') or item.get('file')
        if not relative:
            if item.get('outcome') == 'captured':
                return False
            continue
        source = raw / relative
        if not source.resolve().is_relative_to(raw.resolve()) or not source.is_file():
            return False
        if not item.get('content_hash') or hashlib.sha256(source.read_bytes()).hexdigest() != item['content_hash']:
            return False
    return True
