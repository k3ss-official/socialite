"""Is this URL a *real* website? Verdicts: none|dead|broken|template|real.
The evidence string this produces goes straight into the lead's qualification record."""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")

PARKED_MARKERS = ("domain is for sale", "buy this domain", "sedoparking", "parked free",
                  "godaddy.com/forsale", "this domain has expired", "hugedomains")
# our own demo builds carry this credit — finding one means the prospect was
# already pitched and went cold: a re-engagement lead, not a competitor site
OUR_MARKERS = ("socialite.design", "socialite design")
TEMPLATE_GENERATORS = ("wix.com", "weebly", "site123", "godaddy website builder",
                       "jimdo", "webnode", "mobirise", "duda")


def check(url: str, timeout: int = 12) -> dict:
    """Fetch and judge. Never raises — network failure is itself a verdict."""
    if not url.startswith("http"):
        url = "https://" + url
    out = {"url": url, "status": None, "verdict": "none", "signals": [], "title": "", "text_sample": ""}
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout, allow_redirects=True)
    except requests.RequestException as e:
        out["verdict"] = "dead"
        out["signals"].append(f"unreachable: {type(e).__name__}")
        return out
    out["status"] = r.status_code
    if r.status_code >= 400:
        out["verdict"] = "dead"
        out["signals"].append(f"HTTP {r.status_code}")
        return out
    html = r.text[:400_000]
    low = html.lower()
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)
    title = (soup.title.string or "").strip() if soup.title else ""
    out["title"] = title
    out["text_sample"] = text[:1500]
    out["signals"].append(f"title: {title[:80]}")

    for m in OUR_MARKERS:
        if m in low:
            out["verdict"] = "template"
            out["signals"].append("OUR OWN DEMO BUILD (Socialite credit in page) — prior pitch went cold; re-engagement lead")
            return out
    for m in PARKED_MARKERS:
        if m in low:
            out["verdict"] = "dead"
            out["signals"].append(f"parked-domain marker: '{m}'")
            return out
    gen = soup.find("meta", attrs={"name": "generator"})
    gen_content = (gen.get("content") or "").lower() if gen else ""
    for t in TEMPLATE_GENERATORS:
        if t in gen_content or t in low[:5000]:
            out["verdict"] = "template"
            out["signals"].append(f"site-builder marker: '{t}'")
            return out
    if len(text) < 400:
        out["verdict"] = "broken"
        out["signals"].append(f"near-empty page ({len(text)} chars of text)")
        return out
    out["verdict"] = "real"
    out["signals"].append(f"substantive page ({len(text)} chars of text)")
    return out
