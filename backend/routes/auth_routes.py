"""
auth_routes.py — /auth endpoints
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.core.auth import generate_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
def login(body: LoginRequest):
    if not verify_password(body.username, body.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = generate_token(body.username)
    return {"token": token, "username": body.username}
