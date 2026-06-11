"""RESEARCH: harvest the public web for one lead into data/leads/<id>/raw/.
Free (requests only). The raw bundle is the reproducible input to BIBLE."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .. import store
from ..web import search as websearch
from ..web.sitecheck import UA

MAX_PAGES = 10
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
    for img in soup.find_all("img", src=True)[:20]:
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
    name, area = lead["name"], lead.get("address") or ""
    area = area or next((e["result"] for e in lead["qualification"]["evidence"] if e["check"] == "web_search"), "")
    # area best-effort from the original query is in the slug; use locale area for queries
    from ..config import locale as load_locale
    area = load_locale(lead["locale"]["key"])["discovery"]["area_name"]

    queries = [f'"{name}" {area}', f"{name} {area} reviews", f"{name} {area} menu prices",
               f"best rated {area.split(',')[0]} food competitors {name}"]
    results, seen = [], set()
    for q in queries:
        for r in websearch.search(q, max_results=8):
            if r["href"] not in seen:
                seen.add(r["href"])
                results.append({**r, "query": q, "kind": websearch.classify(r["href"])})

    fetches, image_meta = [], []
    img_seen = set()
    for r in results:
        if len(fetches) >= MAX_PAGES:
            break
        resp = _fetch(r["href"])
        rec = {"url": r["href"], "kind": r["kind"], "status": resp.status_code if resp else None,
               "text_file": None, "title": r["title"]}
        if resp and "html" in resp.headers.get("content-type", ""):
            soup = BeautifulSoup(resp.text, "html.parser")
            for t in soup(["script", "style", "noscript"]):
                t.decompose()
            text = re.sub(r"\n{3,}", "\n\n", soup.get_text("\n", strip=True))
            if len(text) > 300:
                fname = f"{len(fetches):02d}-{websearch.domain_of(r['href']).replace('.', '_')}.txt"
                (raw / "pages" / fname).write_text(text[:40_000])
                rec["text_file"] = f"pages/{fname}"
            if len(image_meta) < MAX_IMAGES:
                for iu in _image_urls(soup, r["href"]):
                    if len(image_meta) >= MAX_IMAGES or iu in img_seen:
                        continue
                    img_seen.add(iu)
                    ir = _fetch(iu)
                    if ir and ir.headers.get("content-type", "").startswith("image/") and len(ir.content) > 15_000:
                        ext = ir.headers["content-type"].split("/")[-1].split(";")[0].replace("jpeg", "jpg")
                        iname = f"img{len(image_meta):02d}.{ext}"
                        (raw / "images" / iname).write_bytes(ir.content)
                        image_meta.append({"file": f"images/{iname}", "source": r["href"],
                                           "bytes": len(ir.content)})
        fetches.append(rec)

    bundle = {"lead_id": lead_id, "harvested_at": store.now(), "queries": queries,
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
