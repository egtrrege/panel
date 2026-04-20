"""
servers.py — Server lifecycle management.
Docker integration for container-based Minecraft servers.
"""
import time
import uuid
from typing import Optional

import docker
from docker.errors import DockerException, NotFound

from backend.core.network import resolve_server_ip
from backend.utils.logger import get_logger
from backend.utils.storage import load, save

log = get_logger("servers")

_STORE = "servers"
MC_IMAGE = "itzg/minecraft-server"


def _try_docker():
    try:
        client = docker.from_env()
        client.ping()
        return client
    except DockerException as e:
        log.warning("Docker unavailable: %s", e)
        return None


def _servers() -> dict:
    return load(_STORE, {})


def _save(servers: dict) -> None:
    save(_STORE, servers)


# --------------------------------------------------------------------------- #
# CRUD                                                                          #
# --------------------------------------------------------------------------- #


def create_server(
    name: str,
    node_id: str,
    mc_version: str = "LATEST",
    ram_mb: int = 1024,
    cpu_limit: float = 1.0,
    port: int = 25565,
    game_mode: str = "survival",
    server_type: str = "VANILLA",
) -> dict:
    servers = _servers()
    server_id = str(uuid.uuid4())
    record = {
        "id": server_id,
        "name": name,
        "node_id": node_id,
        "mc_version": mc_version,
        "ram_mb": ram_mb,
        "cpu_limit": cpu_limit,
        "port": port,
        "game_mode": game_mode,
        "server_type": server_type,
        "status": "stopped",
        "container_id": None,
        "created_at": time.time(),
        "custom_ip": None,
    }
    servers[server_id] = record
    _save(servers)
    log.info("Server created: %s (%s)", name, server_id)
    return record


def list_servers() -> list:
    return list(_servers().values())


def get_server(server_id: str) -> Optional[dict]:
    return _servers().get(server_id)


# --------------------------------------------------------------------------- #
# Docker lifecycle                                                               #
# --------------------------------------------------------------------------- #


def start_server(server_id: str) -> dict:
    servers = _servers()
    server = servers.get(server_id)
    if not server:
        raise ValueError(f"Server {server_id} not found")

    client = _try_docker()
    if not client:
        server["status"] = "error"
        server["status_msg"] = "Docker unavailable on this host"
        _save(servers)
        return server

    # If container already exists, start it
    if server.get("container_id"):
        try:
            container = client.containers.get(server["container_id"])
            if container.status != "running":
                container.start()
            server["status"] = "running"
            _save(servers)
            log.info("Started existing container for server %s", server_id)
            return server
        except NotFound:
            log.warning("Container not found; recreating for server %s", server_id)
            server["container_id"] = None

    # Create + start a new container
    ram_str = f"{server['ram_mb']}M"
    nano_cpus = int(server["cpu_limit"] * 1e9)
    env = {
        "EULA": "TRUE",
        "VERSION": server["mc_version"],
        "MEMORY": ram_str,
        "MODE": server["game_mode"].lower(),
        "TYPE": server["server_type"].upper(),
        "ONLINE_MODE": "FALSE",
    }
    try:
        container = client.containers.run(
            MC_IMAGE,
            detach=True,
            name=f"mc-{server_id[:8]}",
            environment=env,
            ports={f"25565/tcp": server["port"]},
            mem_limit=ram_str,
            nano_cpus=nano_cpus,
            restart_policy={"Name": "unless-stopped"},
        )
        server["container_id"] = container.id
        server["status"] = "running"
        server["status_msg"] = None
        _save(servers)
        log.info("Container %s started for server %s", container.short_id, server_id)
    except DockerException as e:
        server["status"] = "error"
        server["status_msg"] = str(e)
        _save(servers)
        log.error("Docker error starting server %s: %s", server_id, e)

    return server


def stop_server(server_id: str) -> dict:
    servers = _servers()
    server = servers.get(server_id)
    if not server:
        raise ValueError(f"Server {server_id} not found")

    client = _try_docker()
    if client and server.get("container_id"):
        try:
            container = client.containers.get(server["container_id"])
            container.stop(timeout=30)
        except NotFound:
            pass
        except DockerException as e:
            log.error("Error stopping container: %s", e)

    server["status"] = "stopped"
    _save(servers)
    log.info("Server %s stopped", server_id)
    return server


def get_server_ip(server_id: str) -> Optional[str]:
    server = get_server(server_id)
    if not server:
        return None
    return resolve_server_ip(server_id, server.get("node_id"))


def set_server_custom_ip(server_id: str, ip: str) -> None:
    from backend.core.network import set_custom_ip

    servers = _servers()
    if server_id not in servers:
        raise ValueError(f"Server {server_id} not found")
    servers[server_id]["custom_ip"] = ip
    _save(servers)
    set_custom_ip(server_id, ip)
