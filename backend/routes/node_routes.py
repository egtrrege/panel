"""
node_routes.py — /node endpoints
"""
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from backend.app.middleware import require_admin, require_auth
from backend.core import nodes as node_core

router = APIRouter(prefix="/node", tags=["nodes"])


class NodeRegisterRequest(BaseModel):
    name: str
    address: str


class HeartbeatRequest(BaseModel):
    token: str
    meta: Optional[dict] = None


@router.post("/add", dependencies=[Depends(require_admin)])
def add_node(body: NodeRegisterRequest):
    token = secrets.token_hex(32)
    node = node_core.register_node(body.name, body.address, token)
    return {"node": node, "agent_token": token}


@router.post("/heartbeat")
def heartbeat(body: HeartbeatRequest):
    node = node_core.heartbeat(body.token, body.meta)
    if not node:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unknown node token")
    return {"ok": True, "node_id": node["id"]}


@router.get("/list", dependencies=[Depends(require_auth)])
def list_nodes():
    return {"nodes": node_core.list_nodes()}
