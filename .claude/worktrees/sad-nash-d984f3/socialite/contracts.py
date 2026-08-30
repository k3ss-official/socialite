"""Validation against the pinned stage contracts in schemas/."""
from __future__ import annotations

import functools
import json

import jsonschema

from .config import ROOT

SCHEMA_DIR = ROOT / "schemas"


@functools.lru_cache
def schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text())


def validate(obj: dict, name: str) -> dict:
    """Validate obj against schemas/<name>.schema.json. Returns obj for chaining."""
    jsonschema.validate(obj, schema(name))
    return obj


def errors(obj: dict, name: str) -> list[str]:
    """All validation errors as readable strings (for LLM retry feedback)."""
    v = jsonschema.Draft202012Validator(schema(name))
    return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}" for e in v.iter_errors(obj)]
