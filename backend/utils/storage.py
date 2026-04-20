"""
storage.py — Thread-safe JSON persistent storage helpers.
"""
import json
import threading
from pathlib import Path
from typing import Any

_lock = threading.Lock()

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def _path(name: str) -> Path:
    return DATA_DIR / f"{name}.json"


def load(name: str, default: Any = None) -> Any:
    """Load a JSON data file.  Returns *default* if file does not exist."""
    p = _path(name)
    with _lock:
        if not p.exists():
            return default if default is not None else {}
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)


def save(name: str, data: Any) -> None:
    """Atomically persist data to a JSON data file."""
    p = _path(name)
    tmp = p.with_suffix(".tmp")
    with _lock:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        tmp.replace(p)
