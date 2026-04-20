#!/usr/bin/env python3
"""
setup.py — First-run interactive terminal setup wizard.
Run this before starting the panel for the first time.
"""
import json
import sys
from pathlib import Path
import getpass

CONFIG_DIR = Path(__file__).parent / "backend" / "config"
CONFIG_PATH = CONFIG_DIR / "runtime.json"


def prompt(msg: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"{msg}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nSetup cancelled.")
        sys.exit(1)
    return val or default


def prompt_secret(msg: str) -> str:
    try:
        val = getpass.getpass(f"{msg}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nSetup cancelled.")
        sys.exit(1)
    if not val:
        print("Password cannot be empty.")
        return prompt_secret(msg)
    return val


def yn(msg: str, default: bool = False) -> bool:
    default_str = "Y/n" if default else "y/N"
    raw = prompt(f"{msg} ({default_str})", "")
    if not raw:
        return default
    return raw.lower().startswith("y")


def main():
    print("=" * 60)
    print("  MC Panel — First-Run Setup Wizard")
    print("=" * 60)
    print()

    if CONFIG_PATH.exists():
        overwrite = yn("Config already exists. Overwrite?", default=False)
        if not overwrite:
            print("Setup aborted — existing config preserved.")
            sys.exit(0)

    host = prompt("Panel host/IP (0.0.0.0 to bind all interfaces)", "0.0.0.0")
    port = prompt("Panel port", "8000")
    try:
        port = int(port)
    except ValueError:
        print("Invalid port number.")
        sys.exit(1)

    admin_user = prompt("Admin username", "admin")
    admin_pass = prompt_secret("Admin password")

    has_ipv4 = yn("Does this machine have a public IPv4?", default=False)
    public_ipv4 = ""
    if has_ipv4:
        public_ipv4 = prompt("Enter public IPv4 address")

    print()
    print("Tunnel type for Minecraft server access:")
    print("  1) playit  — Playit.gg tunnel")
    print("  2) frp     — Fast Reverse Proxy")
    print("  3) manual  — Enter IP manually later")
    tunnel_choice = prompt("Choose tunnel type", "3")
    tunnel_map = {"1": "playit", "2": "frp", "3": "manual"}
    tunnel_type = tunnel_map.get(tunnel_choice, "manual")

    config = {
        "host": host,
        "port": port,
        "admin_username": admin_user,
        "has_ipv4": has_ipv4,
        "public_ipv4": public_ipv4,
        "tunnel_type": tunnel_type,
        "cloudflare_tunnel": True,
    }

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    print()
    print("[✓] Configuration saved to", CONFIG_PATH)

    # Bootstrap admin user
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from backend.core.auth import create_user, user_exists
        if not user_exists(admin_user):
            create_user(admin_user, admin_pass, role="admin")
            print(f"[✓] Admin user '{admin_user}' created.")
        else:
            print(f"[!] User '{admin_user}' already exists — password NOT changed.")
    except Exception as e:
        print(f"[!] Could not create user (run after installing deps): {e}")
        print(f"    Credentials are saved in config; user will be bootstrapped on first start.")
        # Save credentials temporarily so start.py can create user
        config["_bootstrap_password"] = admin_pass
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=2)

    print()
    print("=" * 60)
    print("  Setup complete!  Next steps:")
    print()
    print("  1. Install deps:  pip install -r requirements.txt")
    print("  2. Start panel:   python start.py")
    print("  3. (Optional) Start Cloudflare Tunnel:")
    print("     cloudflared tunnel --url http://localhost:" + str(port))
    print("=" * 60)


if __name__ == "__main__":
    main()
