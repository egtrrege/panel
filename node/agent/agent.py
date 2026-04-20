#!/usr/bin/env python3
"""
agent.py — Node agent.
Connects a VPS to the MC Panel with a persistent heartbeat loop.
Runs on the remote node, NOT on the panel host.

Usage:
    python agent.py --panel-url https://your-panel.domain --token YOUR_NODE_TOKEN
"""
import argparse
import platform
import time
import os

import requests

DEFAULT_INTERVAL = 15  # seconds between heartbeats


def collect_metadata() -> dict:
    """Gather lightweight system metadata to report to panel."""
    meta = {
        "hostname": platform.node(),
        "os": platform.system(),
        "python": platform.python_version(),
    }
    try:
        import psutil  # optional — richer stats

        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        meta.update(
            {
                "cpu_percent": cpu,
                "ram_total_mb": mem.total // (1024 * 1024),
                "ram_used_mb": mem.used // (1024 * 1024),
                "disk_total_gb": disk.total // (1024 ** 3),
                "disk_used_gb": disk.used // (1024 ** 3),
            }
        )
    except ImportError:
        pass
    return meta


def send_heartbeat(panel_url: str, token: str, session: requests.Session) -> bool:
    url = f"{panel_url.rstrip('/')}/api/node/heartbeat"
    payload = {"token": token, "meta": collect_metadata()}
    try:
        resp = session.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[WARN] Heartbeat failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="MC Panel Node Agent")
    parser.add_argument("--panel-url", required=True, help="Base URL of the MC Panel")
    parser.add_argument("--token", required=True, help="Node authentication token")
    parser.add_argument(
        "--interval",
        type=int,
        default=int(os.getenv("HEARTBEAT_INTERVAL", DEFAULT_INTERVAL)),
        help=f"Heartbeat interval in seconds (default: {DEFAULT_INTERVAL})",
    )
    args = parser.parse_args()

    print(f"[*] MC Panel Node Agent starting")
    print(f"    Panel : {args.panel_url}")
    print(f"    Interval: {args.interval}s")

    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})

    consecutive_failures = 0
    max_failures = 10

    while True:
        ok = send_heartbeat(args.panel_url, args.token, session)
        if ok:
            consecutive_failures = 0
            print(f"[✓] Heartbeat sent ({time.strftime('%H:%M:%S')})")
        else:
            consecutive_failures += 1
            if consecutive_failures >= max_failures:
                print(f"[ERROR] {max_failures} consecutive heartbeat failures — retrying in 60s")
                time.sleep(60)
                consecutive_failures = 0
                continue

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
