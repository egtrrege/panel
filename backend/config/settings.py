"""
settings.py — Loads runtime configuration from config/runtime.json
"""
import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "runtime.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(
            f"Runtime config not found at {CONFIG_PATH}. "
            "Run `python setup.py` to initialise the panel."
        )
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(data: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)


# Singleton — loaded once at import time (after setup has run)
try:
    CONFIG = load_config()
except FileNotFoundError:
    CONFIG = {}
