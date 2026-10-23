"""Hash password (Bcrypt) + JWT access/refresh. Semua fungsi berat dijalankan di thread."""
import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import uuid4

import bcrypt
import jwt

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError

TokenType = Literal["access", "refresh"]


# ---------- Password ----------
async def hash_password(plain: str) -> str:
    rounds = get_settings().BCRYPT_ROUNDS
    hashed = await asyncio.to_thread(bcrypt.hashpw, plain.encode(), bcrypt.gensalt(rounds))
    return hashed.decode()


async def verify_password(plain: str, hashed: str) -> bool:
    try:
        return await asyncio.to_thread(bcrypt.checkpw, plain.encode(), hashed.encode())
    except ValueError:  # hash rusak / password >72 byte
        return False


# ---------- JWT ----------
@dataclass(frozen=True)
class TokenPayload:
    user_id: int
    type: TokenType
    jti: str
    role: str | None
    expires_at: datetime


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _encode(claims: dict) -> str:
    s = get_settings()
    return jwt.encode(claims, s.JWT_SECRET_KEY, algorithm=s.JWT_ALGORITHM)


def create_access_token(user_id: int, role: str) -> tuple[str, int]:
    """Return (token, expires_in_seconds)."""
    s = get_settings()
    expires = timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = _now()
    token = _encode(
        {"sub": str(user_id), "role": role, "type": "access", "jti": uuid4().hex,
         "iat": now, "exp": now + expires}
    )
    return token, int(expires.total_seconds())


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    """Return (token, jti, expires_at). jti disimpan di DB untuk rotation/revoke."""
    s = get_settings()
    now = _now()
    expires_at = now + timedelta(days=s.REFRESH_TOKEN_EXPIRE_DAYS)
    jti = uuid4().hex
    token = _encode(
        {"sub": str(user_id), "type": "refresh", "jti": jti, "iat": now, "exp": expires_at}
    )
    return token, jti, expires_at


def decode_token(token: str, expected: TokenType) -> TokenPayload:
    s = get_settings()
    try:
        data = jwt.decode(
            token, s.JWT_SECRET_KEY, algorithms=[s.JWT_ALGORITHM],
            options={"require": ["exp", "sub", "jti", "type"]},
        )
        if data["type"] != expected:
            raise UnauthorizedError()
        return TokenPayload(
            user_id=int(data["sub"]), type=data["type"], jti=data["jti"],
            role=data.get("role"), expires_at=datetime.fromtimestamp(data["exp"], timezone.utc),
        )
    except (jwt.PyJWTError, ValueError, KeyError) as exc:
        raise UnauthorizedError() from exc
