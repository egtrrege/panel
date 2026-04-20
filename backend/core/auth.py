"""
auth.py — Token-based authentication core.
Passwords are stored as bcrypt hashes.
JWT tokens are signed with HS256.
"""
import secrets
import time
from typing import Optional

import bcrypt
import jwt

from backend.utils.logger import get_logger
from backend.utils.storage import load, save

log = get_logger("auth")

_STORE = "users"
_SECRET_KEY_STORE = "jwt_secret"

# --------------------------------------------------------------------------- #
# JWT secret — generated once, persisted                                       #
# --------------------------------------------------------------------------- #


def _get_jwt_secret() -> str:
    data = load(_SECRET_KEY_STORE, {})
    if "secret" not in data:
        data["secret"] = secrets.token_hex(32)
        save(_SECRET_KEY_STORE, data)
    return data["secret"]


JWT_SECRET = _get_jwt_secret()
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_SECONDS = 86400  # 24 h


# --------------------------------------------------------------------------- #
# User management                                                               #
# --------------------------------------------------------------------------- #


def _users() -> dict:
    return load(_STORE, {})


def _save_users(users: dict) -> None:
    save(_STORE, users)


def create_user(username: str, password: str, role: str = "admin") -> bool:
    """Create a new user.  Returns False if username already exists."""
    users = _users()
    if username in users:
        log.warning("Attempted to create duplicate user: %s", username)
        return False
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    users[username] = {"password_hash": hashed, "role": role}
    _save_users(users)
    log.info("Created user '%s' with role '%s'", username, role)
    return True


def verify_password(username: str, password: str) -> bool:
    users = _users()
    if username not in users:
        return False
    stored = users[username]["password_hash"].encode()
    return bcrypt.checkpw(password.encode(), stored)


def get_user_role(username: str) -> Optional[str]:
    return _users().get(username, {}).get("role")


# --------------------------------------------------------------------------- #
# Token helpers                                                                 #
# --------------------------------------------------------------------------- #


def generate_token(username: str) -> str:
    payload = {
        "sub": username,
        "role": get_user_role(username),
        "iat": int(time.time()),
        "exp": int(time.time()) + JWT_EXPIRY_SECONDS,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        log.debug("Token expired")
    except jwt.InvalidTokenError as e:
        log.debug("Invalid token: %s", e)
    return None


def user_exists(username: str) -> bool:
    return username in _users()
