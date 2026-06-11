"""FIND: qualify a business (or a whole locale) — active socials, no real website,
with evidence for every claim. Programmatic interface: find_single() / find_locale()."""
from __future__ import annotations

import re
import unicodedata

from .. import contracts, store
from ..config import locale as load_locale
from ..web import overpass, search as websearch, sitecheck

PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{8,16}\d)")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-")


def _evidence(check: str, result: str, url: str | None = None) -> dict:
    return {"check": check, "result": result, "url": url, "timestamp": store.now()}


def _name_matches(name: str, text: str) -> bool:
    """Short names need every token ('away' alone matches half the web); longer
    names tolerate one miss."""
    tokens = [t for t in re.split(r"\W+", name.lower()) if len(t) > 2]
    hit = sum(1 for t in tokens if t in text.lower())
    needed = len(tokens) if len(tokens) <= 2 else len(tokens) - 1
    return hit >= max(1, needed)


_CONTENT_PATH = re.compile(r"/(p|reel|posts|photos|videos|albums|story|events)/")


def _social_rank(url: str) -> tuple[int, int]:
    """Profile roots beat content URLs; then shorter wins."""
    return (1 if _CONTENT_PATH.search(url) else 0, len(url))


def _plausibly_theirs(name: str, url: str) -> bool:
    """Directories we've never heard of slip past the blocklist constantly. Structural
    rule: their own site has their name in the domain, or is a shallow homepage URL —
    a deep path on a foreign domain is somebody's listing page, not their website."""
    domain = websearch.domain_of(url)
    tokens = [t for t in re.split(r"\W+", name.lower()) if len(t) > 2]
    if any(t in domain for t in tokens):
        return True
    path = url.split("//", 1)[-1].split("/", 1)[-1] if "/" in url.split("//", 1)[-1] else ""
    return path.strip("/").count("/") == 0 and len(path.strip("/")) < 25


def find_single(query: str, locale_key: str) -> dict:
    """Qualify one named business. query: 'Name, Town[, Country]'."""
    loc = load_locale(locale_key)
    parts = [p.strip() for p in query.split(",")]
    name, area = parts[0], ", ".join(parts[1:]) or loc["discovery"]["area_name"]
    lead_id = slugify(f"{name}-{parts[1] if len(parts) > 1 else area}")
    evidence, socials, candidates = [], {}, []
    contact = {"phone": None, "whatsapp": None, "email": None, "messenger": None}

    results = websearch.search(f'"{name}" {area}', max_results=12)
    results += websearch.search(f"{name} {area} facebook", max_results=6)
    seen = set()
    results = [r for r in results if not (r["href"] in seen or seen.add(r["href"]))]
    evidence.append(_evidence("web_search", f"{len(results)} unique results for '{name} {area}'"))

    for r in results:
        kind = websearch.classify(r["href"])
        blob = f"{r['title']} {r['body']}"
        if kind == "social" and _name_matches(name, blob + " " + r["href"]):
            platform = ("facebook" if "facebook" in r["href"]
                        else "instagram" if "instagram" in r["href"]
                        else "tiktok" if "tiktok" in r["href"] else "other")
            # prefer page roots over posts/albums/group mentions
            if platform not in socials or _social_rank(r["href"]) < _social_rank(socials[platform]):
                if "/groups/" not in r["href"]:
                    socials[platform] = r["href"]
                    evidence.append(_evidence(f"social:{platform}", f"found: {r['title'][:70]}", r["href"]))
        elif kind == "candidate_website" and _name_matches(name, blob + " " + r["href"]) \
                and _plausibly_theirs(name, r["href"]):
            candidates.append(r["href"])
        elif kind == "order_platform" and _name_matches(name, blob):
            candidates.append(r["href"])
        for m in PHONE_RE.findall(blob):
            digits = re.sub(r"\D", "", m)
            if 9 <= len(digits) <= 13 and not contact["phone"]:
                contact["phone"] = m.strip()
                evidence.append(_evidence("contact:phone", f"'{m.strip()}' from search snippet", r["href"]))
        for m in EMAIL_RE.findall(blob):
            # councils and directories leak their own addresses into snippets
            email_domain = m.split("@")[1].lower()
            if email_domain.endswith("gov.uk") or email_domain == websearch.domain_of(r["href"]):
                continue
            if not contact["email"]:
                contact["email"] = m
                evidence.append(_evidence("contact:email", m, r["href"]))

    # Judge candidate websites — worst case for us is they already have a real one.
    website = {"verdict": "none", "url": None}
    for url in candidates[:4]:
        kind = websearch.classify(url)
        if kind == "order_platform":
            verdict = {"verdict": "template", "url": url}
            evidence.append(_evidence("website_check", "white-label ordering platform page — not their own site", url))
            if website["verdict"] == "none":
                website = verdict
            continue
        chk = sitecheck.check(url)
        # the page itself must mention the business, else it's not their site at all
        if chk["verdict"] in ("real", "template", "broken") and \
                not _name_matches(name, f"{chk['title']} {chk['text_sample']} {url}"):
            evidence.append(_evidence("website_check",
                                      f"discarded {url} — page never mentions '{name}'", url))
            continue
        # their content on a domain sharing no token with their name = freebie/template
        # deployment (site-builder subdomain, borrowed domain), not a real web presence
        domain = websearch.domain_of(url)
        tokens = [t for t in re.split(r"\W+", name.lower()) if len(t) > 2]
        if chk["verdict"] == "real" and not any(t in domain for t in tokens):
            chk["verdict"] = "template"
            chk["signals"].append(f"domain '{domain}' unrelated to business name — template/freebie deployment")
        evidence.append(_evidence("website_check", f"{chk['verdict']}: {'; '.join(chk['signals'])}", url))
        if chk["verdict"] == "real":
            website = {"verdict": "real", "url": url}
            break
        if website["verdict"] in ("none",):
            website = {"verdict": chk["verdict"], "url": url}
    if not candidates:
        evidence.append(_evidence("website_check", "no candidate own-domain website in search results"))

    # DDG result variance means a re-run can miss things we already found and
    # verified — never let a rerun silently downgrade known evidence
    status, address, category = "found", None, ""
    try:
        prior = store.get_lead(lead_id)
        status = prior["status"]  # re-finding must not regress pipeline position
        address, category = prior.get("address"), prior.get("category", "")
        if website["verdict"] == "none" and prior["website"]["verdict"] != "none":
            website = prior["website"]
            evidence.append(_evidence(
                "website_check",
                f"kept prior verdict '{website['verdict']}' for {website['url']} (search variance this run)",
                website["url"]))
        for s in prior.get("socials", []):  # union socials across runs
            socials.setdefault(s["platform"], s["url"])
        for k, v in prior.get("contact", {}).items():  # never lose a found contact
            contact[k] = contact.get(k) or v
    except FileNotFoundError:
        pass

    if socials.get("facebook"):
        contact["messenger"] = socials["facebook"]
    score = 0
    score += 35 if socials.get("facebook") else 0
    score += 10 if socials.get("instagram") else 0
    score += {"none": 35, "dead": 35, "broken": 30, "template": 25, "real": 0}[website["verdict"]]
    score += 10 if (contact["phone"] or contact["email"]) else 0
    score += 10 if any(websearch.classify(r["href"]) == "aggregator" and _name_matches(name, r["title"])
                       for r in results) else 0

    lead = {
        "id": lead_id, "name": name, "category": category,
        "locale": {"key": loc["key"], "country": loc["country"], "language": loc["language"],
                   "currency": loc["currency"], "contact_channel": loc["contact_channel"]},
        "address": address, "contact": contact,
        "socials": [{"platform": p, "url": u, "active": None} for p, u in socials.items()],
        "website": website,
        "qualification": {"score": min(score, 100), "evidence": evidence},
        "status": status, "created_at": store.now(), "updated_at": store.now(),
    }
    contracts.validate(lead, "lead")
    store.upsert_lead(lead)
    store.log_event("find", "find_single", "ok", lead_id, artifact=f"data/leads/{lead_id}/lead.json",
                    score=lead["qualification"]["score"], website_verdict=website["verdict"])
    return lead


def find_locale(locale_key: str, limit: int = 25) -> list[dict]:
    """Locale sweep: OSM businesses with no website tag, qualified one by one.
    Each find_single call costs only free searches; cap with --limit."""
    loc = load_locale(locale_key)
    disc = loc["discovery"]
    biz = overpass.find_businesses(disc["area_name"], disc.get("overpass_amenities", []),
                                   disc.get("overpass_tourism"))
    store.log_event("find", "overpass_sweep", "ok", details_count=len(biz), area=disc["area_name"])
    no_site = [b for b in biz if b["name"] and not b["website_tag"]]
    leads = []
    for b in no_site[:limit]:
        lead = find_single(f"{b['name']}, {disc['area_name']}", locale_key)
        if b.get("phone") and not lead["contact"]["phone"]:
            lead["contact"]["phone"] = b["phone"]
        if b.get("address"):
            lead["address"] = b["address"]
        lead["category"] = b["category"]
        lead["qualification"]["evidence"].append(_evidence(
            "osm", f"OSM lists no website tag for this {b['category']}"))
        store.upsert_lead(lead)
        leads.append(lead)
    return leads
