"""
frp.py — Placeholder integration for Fast Reverse Proxy (FRP).
FRP allows TCP tunnelling for Minecraft from a VPS with a public IP.

Server-side frps.ini (on your VPS):
------------------------------------
[common]
bind_port = 7000

Client-side frpc.ini (on the node running Minecraft):
------------------------------------------------------
[common]
server_addr = YOUR_VPS_IP
server_port = 7000

[minecraft]
type = tcp
local_ip = 127.0.0.1
local_port = 25565
remote_port = 25565

Then players connect to: YOUR_VPS_IP:25565
Set this as the Custom IP in the panel.
"""

FRP_REPO = "https://github.com/fatedier/frp/releases"


def instructions() -> str:
    return (
        "FRP (Fast Reverse Proxy) TCP tunnel for Minecraft:\n"
        f"  1. Download frp binaries: {FRP_REPO}\n"
        "  2. Configure frps.ini on your public VPS and run frps.\n"
        "  3. Configure frpc.ini on the Minecraft node and run frpc.\n"
        "  4. Use YOUR_VPS_IP:25565 as the Custom IP in the panel.\n"
    )
