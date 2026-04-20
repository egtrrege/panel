"""
playit.py — Placeholder integration for Playit.gg tunnel.
Playit.gg handles TCP tunnelling for Minecraft (port 25565).

To use:
1. Download the playit-cli binary from https://playit.gg
2. Run: playit-cli --secret YOUR_SECRET tunnel add --proto tcp --port 25565
3. The tunnel address printed (e.g. "region.joinmc.link:PORT") is your server IP.
4. Set it in the panel via POST /api/server/custom-ip or the dashboard.
"""

PLAYIT_DOWNLOAD = "https://playit.gg/download"


def instructions() -> str:
    return (
        "Playit.gg TCP tunnel for Minecraft:\n"
        f"  1. Download playit-cli: {PLAYIT_DOWNLOAD}\n"
        "  2. playit-cli --secret <SECRET> tunnel add --proto tcp --port 25565\n"
        "  3. Copy the printed address and paste it as the server Custom IP in the panel.\n"
    )
