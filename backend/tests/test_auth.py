from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.deps import get_current_user, require_role
from app.core.exceptions import DuplicateError, ForbiddenError, UnauthorizedError
from app.db.models import UserRole
from app.schemas.auth import RegisterRequest
from app.services.auth_service import login, register_customer


def _register_data(**overrides):
    payload = dict(
        name="Customer",
        email="customer@example.com",
        phone="081234567890",
        password="Password123!",
    )
    payload.update(overrides)
    return RegisterRequest(**payload)


async def test_register_customer_creates_customer_and_commits():
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = None

    with patch("app.services.auth_service.hash_password", new=AsyncMock(return_value="hashed")):
        user = await register_customer(db, _register_data())

    assert user.role == UserRole.CUSTOMER
    assert user.password_hash == "hashed"
    db.add.assert_called_once()
    db.commit.assert_awaited_once()


async def test_register_customer_rejects_duplicate_email():
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = SimpleNamespace(id=1)

    with pytest.raises(DuplicateError, match="sudah terdaftar"):
        await register_customer(db, _register_data(email="existing@example.com"))
    db.commit.assert_not_awaited()


async def test_register_customer_rolls_back_integrity_errors():
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = None
    db.commit.side_effect = IntegrityError("insert", {}, Exception())

    with patch("app.services.auth_service.hash_password", new=AsyncMock(return_value="hashed")):
        with pytest.raises(DuplicateError, match="sudah terdaftar"):
            await register_customer(db, _register_data())
    db.rollback.assert_awaited_once()


async def test_login_rejects_invalid_password(customer):
    db = AsyncMock()
    db.scalar.return_value = customer

    with patch("app.services.auth_service.verify_password", new=AsyncMock(return_value=False)):
        with pytest.raises(UnauthorizedError, match="Email atau password salah"):
            await login(db, customer.email, "WrongPassword123!")


async def test_login_returns_token_and_user(customer):
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = customer

    with (
        patch("app.services.auth_service.verify_password", new=AsyncMock(return_value=True)),
        patch("app.services.auth_service.create_access_token", return_value=("token", 3600)),
        patch(
            "app.services.auth_service.create_refresh_token",
            return_value=("refresh", "jti", datetime(2026, 1, 1, tzinfo=timezone.utc)),
        ),
    ):
        result = await login(db, customer.email, "Password123!")

    assert result.access_token == "token"
    assert result.role == UserRole.CUSTOMER
    assert result.name == customer.name
    db.commit.assert_awaited_once()


async def test_require_role_rejects_wrong_role(customer):
    checker = require_role(UserRole.ADMIN)

    with pytest.raises(ForbiddenError) as exc:
        await checker(customer)
    assert exc.value.status_code == 403
    assert exc.value.code == "FORBIDDEN"


async def test_require_role_accepts_allowed_role(admin):
    checker = require_role(UserRole.ADMIN)
    assert await checker(admin) is admin


async def test_get_current_user_rejects_missing_credentials():
    with pytest.raises(UnauthorizedError):
        await get_current_user(None, AsyncMock())


async def test_get_current_user_rejects_invalid_token():
    creds = SimpleNamespace(credentials="bukan.token.valid")
    with patch("app.core.deps.decode_token", side_effect=UnauthorizedError()):
        with pytest.raises(UnauthorizedError):
            await get_current_user(creds, AsyncMock())


async def test_get_current_user_rejects_inactive_user(customer):
    customer.is_active = False
    db = AsyncMock()
    db.get.return_value = customer
    creds = SimpleNamespace(credentials="token")

    with patch(
        "app.core.deps.decode_token",
        return_value=SimpleNamespace(user_id=customer.id),
    ):
        with pytest.raises(UnauthorizedError):
            await get_current_user(creds, db)
