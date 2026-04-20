"""
network.py — IP priority resolution logic.
Priority: custom_ip > tunnel_ip > node_ipv4
"""
from typing import Optional

from backend.utils.storage import load, save

_STORE = "network"


def _net() -> dict:
    return load(_STORE, {})


def _save(data: dict) -> None:
    save(_STORE, data)


# --------------------------------------------------------------------------- #
# Server-level custom IPs                                                       #
# --------------------------------------------------------------------------- #


def set_custom_ip(server_id: str, ip: str) -> None:
    data = _net()
    data.setdefault("custom_ips", {})[server_id] = ip
    _save(data)


def get_custom_ip(server_id: str) -> Optional[str]:
    return _net().get("custom_ips", {}).get(server_id)


# --------------------------------------------------------------------------- #
# Global tunnel IP (set by admin — e.g. playit.gg address)                    #
# --------------------------------------------------------------------------- #


def set_tunnel_ip(ip: str) -> None:
    data = _net()
    data["tunnel_ip"] = ip
    _save(data)


def get_tunnel_ip() -> Optional[str]:
    return _net().get("tunnel_ip")


# --------------------------------------------------------------------------- #
# Node IPv4                                                                     #
# --------------------------------------------------------------------------- #


def set_node_ipv4(node_id: str, ip: str) -> None:
    data = _net()
    data.setdefault("node_ipv4", {})[node_id] = ip
    _save(data)


def get_node_ipv4(node_id: str) -> Optional[str]:
    return _net().get("node_ipv4", {}).get(node_id)


# --------------------------------------------------------------------------- #
# Resolution                                                                    #
# --------------------------------------------------------------------------- #


def resolve_server_ip(server_id: str, node_id: Optional[str] = None) -> Optional[str]:
    """Return effective IP using priority: custom > tunnel > node_ipv4."""
    return (
        get_custom_ip(server_id)
        or get_tunnel_ip()
        or (get_node_ipv4(node_id) if node_id else None)
    )
