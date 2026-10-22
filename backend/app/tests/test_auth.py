import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from core.deps import get_current_user, require_roles
from db.models.user import UserRole
from routers.auth import login, register
from schemas.auth import LoginPayload, RegisterPayload
from services.auth import login_user_service, register_user_service


def run(awaitable):
    return asyncio.run(awaitable)


def test_register_service_creates_customer_and_commits():
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = None
    user = run(
        register_user_service(
            RegisterPayload(
                name="Customer",
                email="customer@example.com",
                phone="081234567890",
                password="Password123!",
            ),
            session,
        )
    )

    assert user.role == UserRole.CUSTOMER
    assert user.password_hash != "Password123!"
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


def test_register_service_rejects_duplicate_email():
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = SimpleNamespace(id=1)

    with pytest.raises(ValueError, match="Email already registered"):
        run(
            register_user_service(
                RegisterPayload(
                    name="Customer",
                    email="existing@example.com",
                    phone="081234567890",
                    password="Password123!",
                ),
                session,
            )
        )
    session.commit.assert_not_awaited()


def test_register_service_rolls_back_integrity_errors():
    from sqlalchemy.exc import IntegrityError

    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = None
    session.commit.side_effect = IntegrityError("insert", {}, Exception())

    with pytest.raises(ValueError, match="database constraint"):
        run(
            register_user_service(
                RegisterPayload(
                    name="Customer",
                    email="customer@example.com",
                    phone="081234567890",
                    password="Password123!",
                ),
                session,
            )
        )
    session.rollback.assert_awaited_once()


def test_login_service_rejects_invalid_password(customer):
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = customer

    with patch("services.auth.verify_password", return_value=False):
        with pytest.raises(ValueError, match="Invalid email or password"):
            run(
                login_user_service(
                    session,
                    LoginPayload(
                        email=customer.email,
                        password="WrongPassword123!",
                    ),
                )
            )


def test_login_service_returns_token_and_user(customer):
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = customer

    with patch("services.auth.verify_password", return_value=True), patch(
        "services.auth.create_access_token",
        return_value="token",
    ):
        result = run(
            login_user_service(
                session,
                LoginPayload(
                    email=customer.email,
                    password="Password123!",
                ),
            )
        )

    assert result["access_token"] == "token"
    assert result["user"]["role"] == "CUSTOMER"


def test_auth_router_maps_login_failure_to_401():
    session = AsyncMock()
    with patch(
        "routers.auth.login_user_service",
        side_effect=ValueError("Invalid email or password"),
    ):
        with pytest.raises(HTTPException) as exc:
            run(
                login(
                    session,
                    LoginPayload(
                        email="user@example.com",
                        password="Password123!",
                    ),
                )
            )
    assert exc.value.status_code == 401
    assert exc.value.detail == {
        "detail": "Invalid email or password",
        "code": "UNAUTHORIZED",
    }


def test_auth_router_maps_register_failure_to_409():
    session = AsyncMock()
    with patch(
        "routers.auth.register_user_service",
        side_effect=ValueError("Email already registered"),
    ):
        with pytest.raises(HTTPException) as exc:
            run(
                register(
                    session,
                    RegisterPayload(
                        name="User",
                        email="user@example.com",
                        phone="081234567890",
                        password="Password123!",
                    ),
                )
            )
    assert exc.value.status_code == 409
    assert exc.value.detail == {
        "detail": "Email already registered",
        "code": "DUPLICATE",
    }


def test_require_roles_rejects_wrong_role(customer):
    checker = require_roles(UserRole.ADMIN)

    with pytest.raises(HTTPException) as exc:
        run(checker(customer))
    assert exc.value.status_code == 403
    assert exc.value.detail["code"] == "FORBIDDEN"


def test_require_roles_accepts_allowed_role(admin):
    checker = require_roles(UserRole.ADMIN)
    assert run(checker(admin)) is admin


def test_get_current_user_rejects_missing_user_id():
    with patch("core.deps.jwt.decode", return_value={}):
        with pytest.raises(HTTPException) as exc:
            run(get_current_user("token", AsyncMock()))
    assert exc.value.status_code == 401
    assert exc.value.detail["code"] == "UNAUTHORIZED"


def test_get_current_user_rejects_inactive_user(customer):
    customer.is_active = False
    session = AsyncMock()
    session.get.return_value = customer
    with patch("core.deps.jwt.decode", return_value={"sub": str(customer.id)}):
        with pytest.raises(HTTPException) as exc:
            run(get_current_user("token", session))
    assert exc.value.status_code == 403
    assert exc.value.detail["code"] == "FORBIDDEN"
