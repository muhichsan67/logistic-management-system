from types import SimpleNamespace

import pytest

from db.models.shipment import ShipmentStatus
from db.models.user import UserRole


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


@pytest.fixture
def shipment(customer):
    return SimpleNamespace(
        id=100,
        tracking_number="TRX-20261022-0001",
        customer_id=customer.id,
        courier_id=20,
        sender_name=customer.name,
        sender_phone=customer.phone,
        origin_address="Origin",
        recipient_name="Recipient",
        recipient_phone="081234567893",
        destination_address="Destination",
        package_description="Package",
        weight_kg=2.5,
        status=ShipmentStatus.PENDING,
        rejection_reason=None,
        proof_image_url=None,
        delivered_at=None,
        created_at=SimpleNamespace(),
        updated_at=SimpleNamespace(),
    )
