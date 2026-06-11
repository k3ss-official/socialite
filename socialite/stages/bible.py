"""BIBLE: synthesize the raw research bundle into one versioned, reproducible
research document per prospect. Idempotent: same inputs_hash -> reuse, no LLM spend."""
from __future__ import annotations

import json

from .. import contracts, llm, store
from ..config import ROOT, ladder, locale as load_locale
from . import research

PROMPT_VERSION = "1"


def _build_prompt(lead: dict, bundle: dict) -> str:
    loc = load_locale(lead["locale"]["key"])
    raw = store.lead_dir(lead["id"]) / "raw"
    texts = []
    for f in bundle["fetched"]:
        if f["text_file"]:
            body = (raw / f["text_file"]).read_text()[:6000]
            texts.append(f"--- SOURCE: {f['url']} ({f['kind']})\n{body}")
    snippets = "\n".join(f"[{r['kind']}] {r['title']} — {r['body']} ({r['href']})"
                         for r in bundle["results"])
    from ..config import settings
    bundle_text = (f"SEARCH SNIPPETS\n{snippets}\n\nFETCHED PAGES\n" + "\n\n".join(texts)
                   )[:settings()["llm"]["max_input_chars"]]
    template = (ROOT / "prompts" / "bible.md").read_text()
    return template.format(
        name=lead["name"], area=loc["discovery"]["area_name"],
        language=lead["locale"]["language"], currency=lead["locale"]["currency"],
        contact_channel=lead["locale"]["contact_channel"],
        contact=json.dumps(lead["contact"]), socials=json.dumps(lead["socials"]),
        images=json.dumps([i["file"] for i in bundle.get("images", [])]),
        gap_keys=json.dumps(list(ladder()["gaps"].keys())),
        website_verdict=lead["website"]["verdict"],
        schema=json.dumps(contracts.schema("bible")),
        bundle=bundle_text)


def generate(lead_id: str, force: bool = False) -> dict:
    lead = store.get_lead(lead_id)
    raw = store.lead_dir(lead_id) / "raw"
    if not (raw / "research.json").exists():
        research.harvest(lead_id)
    bundle = store.load_json(raw / "research.json")
    inputs_hash = research.bundle_hash(lead_id, extra=PROMPT_VERSION)

    bdir = store.lead_dir(lead_id) / "bible"
    latest = store.latest_version(bdir)
    if latest and not force:
        existing = store.load_json(bdir / f"v{latest}.json")
        if existing.get("inputs_hash") == inputs_hash:
            store.advance_status(lead_id, "bible")
            store.log_event("bible", "reuse_existing", "skipped", lead_id, version=latest,
                            reason="inputs unchanged")
            return existing

    prompt = _build_prompt(lead, bundle)
    try:
        obj = llm.generate_json(prompt, "bible", lead_id, "bible", estimated_cost_usd=0.30)
    except RuntimeError as e:
        store.log_event("bible", "llm_call", "error", lead_id, error=str(e)[:300])
        raise SystemExit(
            f"BIBLE stage failed: {e}\n"
            "If this is an auth error, run `claude /login` in a terminal and retry. "
            "An existing bible version (if any) is untouched.")
    version = store.next_version(bdir)
    obj.update({"lead_id": lead_id, "version": version, "generated_at": store.now(),
                "inputs_hash": inputs_hash})
    # keep only photos that actually exist on disk
    obj["photos"] = [p for p in obj.get("photos", []) if (raw / p["path"]).exists()]
    contracts.validate(obj, "bible")
    path = store.save_json(bdir / f"v{version}.json", obj)
    store.advance_status(lead_id, "bible")
    store.log_event("bible", "generated", "ok", lead_id, artifact=str(path.relative_to(ROOT)),
                    version=version, inputs_hash=inputs_hash)
    return obj
