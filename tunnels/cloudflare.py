"""
cloudflare.py — Cloudflare Tunnel helper for panel HTTP access.
Cloudflare Tunnel does NOT support TCP (Minecraft port 25565).
Use it ONLY for the web panel (HTTP/HTTPS).

Quick start (no account needed — dev mode):
    cloudflared tunnel --url http://localhost:8000

With a named tunnel (production):
    1. cloudflared login
    2. cloudflared tunnel create mc-panel
    3. cloudflared tunnel route dns mc-panel panel.yourdomain.com
    4. cloudflared tunnel run mc-panel
"""

CLOUDFLARED_DOWNLOAD = "https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/"


def quick_start_command(port: int = 8000) -> str:
    return f"cloudflared tunnel --url http://localhost:{port}"


def instructions(port: int = 8000) -> str:
    return (
        "Cloudflare Tunnel (panel access only — NOT for Minecraft TCP):\n"
        f"  Dev:   {quick_start_command(port)}\n"
        "  Prod:  cloudflared tunnel create mc-panel\n"
        "         cloudflared tunnel route dns mc-panel panel.yourdomain.com\n"
        "         cloudflared tunnel run mc-panel\n"
        f"  Download: {CLOUDFLARED_DOWNLOAD}\n"
    )
