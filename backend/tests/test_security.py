import pytest

from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token, create_refresh_token, decode_token, hash_password, verify_password,
)


async def test_password_roundtrip():
    h = await hash_password("Password123!")
    assert await verify_password("Password123!", h)
    assert not await verify_password("salah", h)


def test_access_token_roundtrip():
    token, expires_in = create_access_token(7, "ADMIN")
    p = decode_token(token, "access")
    assert (p.user_id, p.role, p.type) == (7, "ADMIN", "access")
    assert expires_in > 0


def test_token_type_is_enforced():
    refresh, _, _ = create_refresh_token(1)
    access, _ = create_access_token(1, "CUSTOMER")
    with pytest.raises(UnauthorizedError):
        decode_token(refresh, "access")  # refresh tidak boleh dipakai sebagai access
    with pytest.raises(UnauthorizedError):
        decode_token(access, "refresh")


def test_garbage_token_rejected():
    with pytest.raises(UnauthorizedError):
        decode_token("bukan.token.valid", "access")
