"""UPSELL: deterministic pitch sheet from the bible's gap matrix + the residual ladder.
No LLM here on purpose — sell lines are vetted config, reps get consistency, cost is zero."""
from __future__ import annotations

from jinja2 import Environment, FileSystemLoader

from .. import contracts, store
from ..config import ROOT, ladder as load_ladder, locale as load_locale


def generate(lead_id: str, bible_version: int | None = None) -> dict:
    lead = store.get_lead(lead_id)
    bdir = store.lead_dir(lead_id) / "bible"
    bible_version = bible_version or store.latest_version(bdir)
    if not bible_version:
        raise SystemExit(f"No bible for {lead_id} — run the bible stage first.")
    bible = store.load_json(bdir / f"v{bible_version}.json")
    lad, loc = load_ladder(), load_locale(lead["locale"]["key"])

    open_gaps = [g for g in bible["gap_matrix"] if not g["prospect_has"]]
    gap_to_rung = {}
    for rkey, rung in lad["rungs"].items():
        for gk in rung.get("gaps", []):
            gap_to_rung.setdefault(gk, rkey)

    gap_summary = []
    for g in open_gaps:
        cfg = lad["gaps"].get(g["gap_key"])
        if not cfg:
            continue
        gap_summary.append({
            "gap_key": g["gap_key"], "label": cfg["label"],
            "sell_line": cfg["sell_line"].replace("{n}", str(g["competitors_with"])),
            "rung_key": gap_to_rung.get(g["gap_key"], "r1_foundation"),
            "competitors_with": g["competitors_with"],
        })

    open_keys = {g["gap_key"] for g in gap_summary}
    rungs = []
    for rkey, rung in lad["rungs"].items():
        price = loc["prices"][rkey]
        addressed = sorted(set(rung.get("gaps", [])) & open_keys)
        rungs.append({
            "key": rkey, "name": rung["name"], "kind": rung["kind"],
            "monthly_low": price["low"], "monthly_high": price["high"],
            "term_months": rung.get("term_months"),
            "cadence_per_year": rung.get("cadence_per_year"),
            "includes": rung["includes"], "gifts": rung.get("gifts", []),
            "gaps_addressed": addressed, "recommended": bool(addressed),
        })

    tiers = []
    best_tier, best_cover = None, -1
    for tkey, tier in lad["tiers"].items():
        keys = tier["rungs"]
        cover = len(open_keys & {gk for k in keys for gk in lad["rungs"][k].get("gaps", [])})
        low = sum(loc["prices"][k]["low"] for k in keys)
        high = sum(loc["prices"][k]["high"] for k in keys)
        tiers.append({"key": tkey, "name": tier["name"], "pitch_line": tier["pitch_line"],
                      "rung_keys": keys, "monthly_low": low, "monthly_high": high,
                      "recommended": False})
        # recommend the cheapest tier covering the most open gaps
        if cover > best_cover or (cover == best_cover and low < tiers[best_tier]["monthly_low"] if best_tier is not None else False):
            best_cover, best_tier = cover, len(tiers) - 1
    if best_tier is not None:
        tiers[best_tier]["recommended"] = True

    version = store.next_version(store.lead_dir(lead_id) / "pitch", "v*.json")
    pitch = {"lead_id": lead_id, "bible_version": bible_version, "generated_at": store.now(),
             "currency": lead["locale"]["currency"], "gap_summary": gap_summary,
             "rungs": rungs, "tiers": tiers}
    contracts.validate(pitch, "pitch")
    pdir = store.lead_dir(lead_id) / "pitch"
    store.save_json(pdir / f"v{version}.json", pitch)

    env = Environment(loader=FileSystemLoader(ROOT / "templates" / "pitch"), autoescape=True)
    html = env.get_template("pitch.html.j2").render(
        pitch=pitch, bible=bible, lead=lead, locale=loc,
        rung_by_key={r["key"]: r for r in rungs})
    (pdir / f"v{version}.html").write_text(html)
    store.set_status(lead_id, "pitched")
    store.log_event("pitch", "generated", "ok", lead_id, version=version,
                    artifact=f"data/leads/{lead_id}/pitch/v{version}.html",
                    open_gaps=sorted(open_keys))
    return pitch
