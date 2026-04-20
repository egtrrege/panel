#!/usr/bin/env python3
"""
start.py — Panel entry point.
Loads config, bootstraps admin if needed, then launches uvicorn.
"""
import json
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "backend" / "config" / "runtime.json"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        print("[ERROR] No runtime config found.  Run `python setup.py` first.")
        sys.exit(1)
    with open(CONFIG_PATH) as f:
        return json.load(f)


def bootstrap_user(config: dict) -> None:
    """If setup couldn't create the admin user, try now."""
    pwd = config.pop("_bootstrap_password", None)
    if not pwd:
        return
    try:
        from backend.core.auth import create_user, user_exists

        username = config.get("admin_username", "admin")
        if not user_exists(username):
            create_user(username, pwd, role="admin")
            print(f"[✓] Admin user '{username}' bootstrapped.")
        # Remove the password from persisted config
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[!] Bootstrap error: {e}")


def main():
    config = load_config()
    bootstrap_user(config)

    host = config.get("host", "0.0.0.0")
    port = config.get("port", 8000)

    print(f"[✓] Starting MC Panel on http://{host}:{port}")
    if config.get("cloudflare_tunnel"):
        print(f"    Tip: expose via  cloudflared tunnel --url http://localhost:{port}")

    try:
        import uvicorn
    except ImportError:
        print("[ERROR] uvicorn not installed.  Run: pip install -r requirements.txt")
        sys.exit(1)

    uvicorn.run(
        "backend.app.main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
