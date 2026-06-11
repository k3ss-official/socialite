"""RESEARCH: harvest the public web for one lead into data/leads/<id>/raw/.
Free (requests only). The raw bundle is the reproducible input to BIBLE.

Order of trust: (1) the lead's own known URLs — their site/template page, socials,
evidence pages from FIND; (2) name-matched search results; (3) competitor-survey
results (text only, never images). Pages that never mention the business are skipped —
'scran' taught us that lesson, see notes/SCRAPING.md."""
from __future__ import annotations

import hashlib
import re

import requests
from bs4 import BeautifulSoup

from .. import store
from ..config import locale as load_locale
from ..web import search as websearch
from ..web.sitecheck import UA
from .find import _name_matches

MAX_PAGES = 14
MAX_IMAGES = 8


def _fetch(url: str, timeout: int = 15) -> requests.Response | None:
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
        return r if r.status_code == 200 else None
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


def harvest(lead_id: str) -> dict:
    lead = store.get_lead(lead_id)
    raw = store.lead_dir(lead_id) / "raw"
    (raw / "pages").mkdir(parents=True, exist_ok=True)
    (raw / "images").mkdir(parents=True, exist_ok=True)
    name = lead["name"]
    area = load_locale(lead["locale"]["key"])["discovery"]["area_name"]
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
    queries = [f'"{name}" {town}', f'"{name}" {town} reviews', f'"{name}" {town} menu']
    comp_query = f"best rated takeaway street food {town} reviews"
    results, seen = [], set(own_seen)
    for q in queries + [comp_query]:
        for r in websearch.search(q, max_results=8):
            if norm(r["href"]) in seen:
                continue
            seen.add(norm(r["href"]))
            is_comp = q == comp_query
            if not is_comp and not _name_matches(name, f"{r['title']} {r['body']} {r['href']}"):
                continue
            results.append({**r, "query": q, "kind": "competitor" if is_comp else websearch.classify(r["href"])})

    fetch_list = own_urls + [(r["href"], r["kind"]) for r in results]
    fetches, image_meta, img_seen, img_hashes = [], [], set(), set()
    comp_budget = 3
    for url, kind in fetch_list:
        if len(fetches) >= MAX_PAGES:
            break
        if kind == "competitor":
            if comp_budget == 0:
                continue
            comp_budget -= 1
        resp = _fetch(url)
        rec = {"url": url, "kind": kind, "status": resp.status_code if resp else None,
               "text_file": None}
        if resp and "html" in resp.headers.get("content-type", ""):
            soup = BeautifulSoup(resp.text, "html.parser")
            for t in soup(["script", "style", "noscript"]):
                t.decompose()
            text = re.sub(r"\n{3,}", "\n\n", soup.get_text("\n", strip=True))
            about_them = _name_matches(name, text[:8000]) or kind.startswith(("own_", "social:"))
            if len(text) > 300 and (about_them or kind == "competitor"):
                fname = f"{len(fetches):02d}-{websearch.domain_of(url).replace('.', '_')}.txt"
                (raw / "pages" / fname).write_text(f"[{kind}] {url}\n\n{text[:40_000]}")
                rec["text_file"] = f"pages/{fname}"
            # images only from pages that are genuinely about the business
            if about_them and kind != "competitor" and len(image_meta) < MAX_IMAGES:
                for iu in _image_urls(soup, url):
                    if len(image_meta) >= MAX_IMAGES or iu in img_seen:
                        continue
                    img_seen.add(iu)
                    ir = _fetch(iu)
                    if ir and ir.headers.get("content-type", "").startswith("image/") and len(ir.content) > 15_000:
                        digest = hashlib.sha256(ir.content).hexdigest()
                        if digest in img_hashes:
                            continue
                        img_hashes.add(digest)
                        ext = ir.headers["content-type"].split("/")[-1].split(";")[0].replace("jpeg", "jpg")
                        iname = f"img{len(image_meta):02d}.{ext}"
                        (raw / "images" / iname).write_bytes(ir.content)
                        image_meta.append({"file": f"images/{iname}", "source": url,
                                           "bytes": len(ir.content)})
        fetches.append(rec)

    bundle = {"lead_id": lead_id, "harvested_at": store.now(), "queries": queries + [comp_query],
              "results": results, "fetched": fetches, "images": image_meta}
    store.save_json(raw / "research.json", bundle)
    store.log_event("research", "harvest", "ok", lead_id, artifact=f"data/leads/{lead_id}/raw/research.json",
                    pages=len([f for f in fetches if f["text_file"]]), images=len(image_meta),
                    results=len(results))
    return bundle


def bundle_hash(lead_id: str, extra: str = "") -> str:
    """sha256 over the raw bundle — the reproducibility anchor for BIBLE versions."""
    raw = store.lead_dir(lead_id) / "raw"
    h = hashlib.sha256(extra.encode())
    for p in sorted(raw.rglob("*")):
        if p.is_file() and p.suffix in (".json", ".txt"):
            h.update(p.name.encode())
            h.update(p.read_bytes())
    return h.hexdigest()[:16]
