"""
server_routes.py — /server endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from backend.app.middleware import require_admin, require_auth
from backend.core import servers as srv_core
from backend.core.network import set_tunnel_ip

router = APIRouter(prefix="/server", tags=["servers"])


class CreateServerRequest(BaseModel):
    name: str
    node_id: str
    mc_version: str = "LATEST"
    ram_mb: int = 1024
    cpu_limit: float = 1.0
    port: int = 25565
    game_mode: str = "survival"
    server_type: str = "VANILLA"


class CustomIPRequest(BaseModel):
    server_id: str
    ip: str


class TunnelIPRequest(BaseModel):
    ip: str


@router.post("/create", dependencies=[Depends(require_admin)])
def create_server(body: CreateServerRequest):
    server = srv_core.create_server(**body.dict())
    return {"server": server}


@router.post("/start/{server_id}", dependencies=[Depends(require_admin)])
def start_server(server_id: str):
    try:
        server = srv_core.start_server(server_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"server": server}


@router.post("/stop/{server_id}", dependencies=[Depends(require_admin)])
def stop_server(server_id: str):
    try:
        server = srv_core.stop_server(server_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"server": server}


@router.get("/list", dependencies=[Depends(require_auth)])
def list_servers():
    return {"servers": srv_core.list_servers()}


@router.get("/ip/{server_id}", dependencies=[Depends(require_auth)])
def get_ip(server_id: str):
    ip = srv_core.get_server_ip(server_id)
    return {"server_id": server_id, "ip": ip}


@router.post("/custom-ip", dependencies=[Depends(require_admin)])
def set_custom_ip(body: CustomIPRequest):
    try:
        srv_core.set_server_custom_ip(body.server_id, body.ip)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return {"ok": True}


@router.post("/tunnel-ip", dependencies=[Depends(require_admin)])
def set_global_tunnel_ip(body: TunnelIPRequest):
    set_tunnel_ip(body.ip)
    return {"ok": True, "tunnel_ip": body.ip}
