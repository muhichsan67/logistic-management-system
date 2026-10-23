import os
from types import SimpleNamespace

import pytest

# Harus di-set SEBELUM modul app di-import.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-test-secret-test-secret-123")
os.environ.setdefault("BCRYPT_ROUNDS", "4")

from app.db.models import UserRole  # noqa: E402


@pytest.fixture
def customer():
    return SimpleNamespace(
        id=10,
        name="Customer One",
        email="customer@example.com",
        phone="081234567890",
        password_hash="hashed-password",
        role=UserRole.CUSTOMER,
        is_active=True,
    )


@pytest.fixture
def admin():
    return SimpleNamespace(
        id=1,
        name="Admin",
        email="admin@example.com",
        phone="081234567891",
        password_hash="hashed-password",
        role=UserRole.ADMIN,
        is_active=True,
    )


@pytest.fixture
def courier():
    return SimpleNamespace(
        id=20,
        name="Courier One",
        email="courier@example.com",
        phone="081234567892",
        password_hash="hashed-password",
        role=UserRole.COURIER,
        is_active=True,
    )
