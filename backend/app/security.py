"""Password hashing (argon2id) and JWT access/refresh tokens."""
from datetime import datetime, timedelta, timezone

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import User

_ph = PasswordHasher()


def hash_password(pw: str) -> str:
    return _ph.hash(pw)


def verify_password(pw: str, hashed: str) -> bool:
    """Constant-behavior verify: mismatches AND malformed/empty stored hashes return
    False instead of raising (a deleted account's hash is cleared to "" — that must
    surface as a 401, never a 500)."""
    try:
        return _ph.verify(hashed, pw)
    except (VerificationError, InvalidHashError):
        return False


def _make_token(sub: str, tenant_id: str, role: str, kind: str, minutes: int,
                token_version: int) -> str:
    s = get_settings()
    payload = {
        "sub": sub, "tid": tenant_id, "role": role, "kind": kind,
        "tv": token_version,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, s.jwt_secret, algorithm="HS256")


def make_access_token(user: User) -> str:
    return _make_token(user.id, user.tenant_id, user.role, "access",
                       get_settings().access_token_minutes, user.token_version or 0)


def make_refresh_token(user: User) -> str:
    return _make_token(user.id, user.tenant_id, user.role, "refresh",
                       get_settings().refresh_token_days * 24 * 60, user.token_version or 0)


def check_token_version(payload: dict, user: User) -> None:
    """Reject any token minted before the user's current token generation.
    Bumping User.token_version (password change, account deletion) revokes every
    outstanding access AND refresh token without server-side session storage."""
    if int(payload.get("tv", 0)) != int(user.token_version or 0):
        raise HTTPException(401, "Token has been revoked")


def decode_token(token: str, expected_kind: str) -> dict:
    s = get_settings()
    try:
        payload = jwt.decode(token, s.jwt_secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
    if payload.get("kind") != expected_kind:
        raise HTTPException(401, "Wrong token type")
    return payload


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    payload = decode_token(auth[7:], "access")
    user = db.get(User, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or deactivated")
    check_token_version(payload, user)
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(403, "Admin role required")
    return user
