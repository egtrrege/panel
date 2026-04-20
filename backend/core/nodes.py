"""
nodes.py — Node registration and heartbeat management.
"""
import time
import uuid
from typing import Optional

from backend.utils.logger import get_logger
from backend.utils.storage import load, save

log = get_logger("nodes")

_STORE = "nodes"
HEARTBEAT_TIMEOUT = 60  # seconds


def _nodes() -> dict:
    return load(_STORE, {})


def _save(nodes: dict) -> None:
    save(_STORE, nodes)


def register_node(name: str, address: str, token: str) -> dict:
    """Register or update a node.  Returns the node record."""
    nodes = _nodes()
    node_id = _find_by_token(nodes, token) or str(uuid.uuid4())
    nodes[node_id] = {
        "id": node_id,
        "name": name,
        "address": address,
        "token": token,
        "registered_at": nodes.get(node_id, {}).get("registered_at", time.time()),
        "last_heartbeat": time.time(),
        "online": True,
        "ipv4": None,
    }
    _save(nodes)
    log.info("Node registered/updated: %s (%s)", name, node_id)
    return nodes[node_id]


def heartbeat(token: str, metadata: Optional[dict] = None) -> Optional[dict]:
    nodes = _nodes()
    node_id = _find_by_token(nodes, token)
    if not node_id:
        return None
    nodes[node_id]["last_heartbeat"] = time.time()
    nodes[node_id]["online"] = True
    if metadata:
        nodes[node_id].setdefault("meta", {}).update(metadata)
    _save(nodes)
    return nodes[node_id]


def list_nodes() -> list:
    nodes = _nodes()
    now = time.time()
    result = []
    changed = False
    for node in nodes.values():
        age = now - node.get("last_heartbeat", 0)
        online = age < HEARTBEAT_TIMEOUT
        if node.get("online") != online:
            node["online"] = online
            changed = True
        result.append(node)
    if changed:
        _save(nodes)
    return result


def get_node(node_id: str) -> Optional[dict]:
    return _nodes().get(node_id)


def _find_by_token(nodes: dict, token: str) -> Optional[str]:
    for nid, node in nodes.items():
        if node.get("token") == token:
            return nid
    return None
