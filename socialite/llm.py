"""Synthesis engine: shells out to the local `claude` CLI in print mode.
Why: already installed, billed to the existing plan, no extra SaaS, and
`--output-format json` reports total_cost_usd so the per-lead cap is enforceable.
"""
from __future__ import annotations

import json
import os
import re
import subprocess

from . import contracts, store
from .config import settings

# When the pipeline runs nested inside a Claude Code session, harness env vars
# (proxy base URL, session creds) leak in and 401 the CLI. Scrub them.
_SCRUB_ENV = ("ANTHROPIC_BASE_URL", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
              "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_CODE_SESSION_ID")


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model reply (handles ``` fences and prose)."""
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        return json.loads(fence.group(1))
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON object in LLM reply: {text[:300]}")
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])
    raise ValueError("Unbalanced JSON in LLM reply")


def _call(prompt: str, timeout: int = 600) -> tuple[str, float]:
    cfg = settings()["llm"]
    cmd = [cfg["cli"], "-p", "--output-format", "json", "--model", cfg["model"]]
    env = {k: v for k, v in os.environ.items() if k not in _SCRUB_ENV}
    proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                          timeout=timeout, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"claude CLI failed (rc={proc.returncode}): {proc.stderr[:500]}")
    envelope = json.loads(proc.stdout)
    if envelope.get("is_error"):
        raise RuntimeError(f"claude CLI error: {str(envelope.get('result'))[:300]}")
    return envelope.get("result", ""), float(envelope.get("total_cost_usd") or 0.05)


def generate_json(prompt: str, schema_name: str, lead_id: str, stage: str,
                  estimated_cost_usd: float = 0.30) -> dict:
    """One schema-validated LLM call with cost-cap check, cost logging, and one repair retry."""
    store.ensure_budget(lead_id, estimated_cost_usd)
    text, cost = _call(prompt)
    store.log_event(stage, "llm_call", "ok", lead_id, cost_usd=cost, schema=schema_name)
    try:
        obj = _extract_json(text)
        errs = contracts.errors(obj, schema_name)
    except (ValueError, json.JSONDecodeError) as e:
        obj, errs = None, [str(e)]
    if not errs:
        return obj
    # one repair pass: feed the errors back
    store.ensure_budget(lead_id, estimated_cost_usd)
    repair = (f"{prompt}\n\nYour previous reply had these schema violations:\n- "
              + "\n- ".join(errs[:20])
              + f"\n\nPrevious reply:\n{text[:8000]}\n\nReturn the corrected JSON object only.")
    text, cost = _call(repair)
    store.log_event(stage, "llm_repair_call", "ok", lead_id, cost_usd=cost, schema=schema_name)
    obj = _extract_json(text)
    contracts.validate(obj, schema_name)
    return obj
