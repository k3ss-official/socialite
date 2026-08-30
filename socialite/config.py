"""Config loading. Settings are global; locale packs carry everything market-specific."""
from __future__ import annotations

import functools
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = ROOT / "config"


@functools.lru_cache
def settings() -> dict:
    return yaml.safe_load((CONFIG_DIR / "settings.yaml").read_text())


@functools.lru_cache
def locale(key: str) -> dict:
    path = CONFIG_DIR / "locales" / f"{key}.yaml"
    if not path.exists():
        available = sorted(p.stem for p in (CONFIG_DIR / "locales").glob("*.yaml"))
        raise SystemExit(f"Unknown locale '{key}'. Available: {', '.join(available)}")
    return yaml.safe_load(path.read_text())


@functools.lru_cache
def ladder() -> dict:
    return yaml.safe_load((CONFIG_DIR / "ladder.yaml").read_text())


def data_dir() -> Path:
    d = ROOT / settings()["data_dir"]
    d.mkdir(parents=True, exist_ok=True)
    return d
