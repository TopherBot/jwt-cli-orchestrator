from __future__ import annotations

import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict

import jwt
import keyring

# Settings – in a real project these would be configurable
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 60
KEYRING_SERVICE = "jwt-cli-orchestrator"


def _secret_key() -> str:
    """Retrieve the secret key from the OS keyring; generate a random one if missing."""
    key = keyring.get_password(KEYRING_SERVICE, "secret_key")
    if not key:
        # Generate a 256‑bit random key
        import secrets
        key = secrets.token_urlsafe(32)
        keyring.set_password(KEYRING_SERVICE, "secret_key", key)
    return key


def create_token(username: str, role: str, expires_delta: timedelta | None = None) -> str:
    now = datetime.utcnow()
    exp = now + (expires_delta or timedelta(minutes=TOKEN_EXPIRY_MINUTES))
    payload: Dict[str, Any] = {
        "sub": username,
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    token = jwt.encode(payload, _secret_key(), algorithm=ALGORITHM)
    # Store the token for quick reuse
    keyring.set_password(KEYRING_SERVICE, username, token)
    return token


def verify_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise PermissionError("Token has expired")
    except jwt.InvalidTokenError as exc:
        raise PermissionError(f"Invalid token: {exc}")


def get_stored_token(username: str) -> str | None:
    return keyring.get_password(KEYRING_SERVICE, username)
