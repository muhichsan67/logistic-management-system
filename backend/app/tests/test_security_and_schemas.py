from decimal import Decimal

import pytest
from pydantic import ValidationError

from core.security import hash_password, verify_password
from db.models.shipment import ShipmentStatus
from schemas.admin import (
    AssignShipmentPayload,
    RejectShipmentPayload,
    SystemSettingsPayload,
)
from schemas.auth import LoginPayload, RegisterPayload
from schemas.shipment import ShipmentCreatePayload, ShipmentStatusUpdatePayload


def test_password_hash_is_verifiable_and_not_plaintext():
    password = "Password123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword123!", hashed)


def test_register_payload_accepts_required_fields():
    payload = RegisterPayload(
        name="Customer",
        email="customer@example.com",
        phone="081234567890",
        password="Password123!",
    )

    assert payload.name == "Customer"


def test_login_payload_requires_credentials():
    with pytest.raises(ValidationError):
        LoginPayload(email="customer@example.com")


def test_shipment_payload_trims_text_and_validates_weight():
    payload = ShipmentCreatePayload(
        origin_address=" Origin ",
        sender_phone="081234567890",
        recipient_name=" Recipient ",
        recipient_phone="081234567890",
        destination_address=" Destination ",
        package_description=" Package ",
        weight_kg=Decimal("1.25"),
    )

    assert payload.recipient_name == "Recipient"
    assert payload.destination_address == "Destination"


@pytest.mark.parametrize(
    "field,value",
    [
        ("recipient_name", " "),
        ("destination_address", ""),
        ("package_description", " "),
        ("recipient_phone", "not-a-phone"),
    ],
)
def test_shipment_payload_rejects_invalid_fields(field, value):
    payload = {
        "recipient_name": "Recipient",
        "origin_address": "Origin",
        "sender_phone": "081234567890",
        "recipient_phone": "081234567890",
        "destination_address": "Destination",
        "package_description": "Package",
        "weight_kg": 1,
    }
    payload[field] = value

    with pytest.raises(ValidationError):
        ShipmentCreatePayload(**payload)


@pytest.mark.parametrize("weight", [0, -1, 10000])
def test_shipment_payload_rejects_invalid_weight(weight):
    with pytest.raises(ValidationError):
        ShipmentCreatePayload(
            recipient_name="Recipient",
            origin_address="Origin",
            sender_phone="081234567890",
            recipient_phone="081234567890",
            destination_address="Destination",
            package_description="Package",
            weight_kg=weight,
        )


def test_admin_payloads_require_positive_values_and_reason():
    assert SystemSettingsPayload(
        pending_alert_timeout_minutes=30,
        auto_complete_days=3,
    )
    assert AssignShipmentPayload(courier_id=1)
    assert RejectShipmentPayload(rejection_reason="Invalid address")

    with pytest.raises(ValidationError):
        SystemSettingsPayload(
            pending_alert_timeout_minutes=0,
            auto_complete_days=3,
        )
    with pytest.raises(ValidationError):
        RejectShipmentPayload(rejection_reason="")


def test_shipment_status_enum_contains_all_lifecycle_states():
    assert {status.value for status in ShipmentStatus} == {
        "PENDING",
        "REJECTED",
        "ASSIGNED",
        "PICKED_UP",
        "IN_TRANSIT",
        "DELIVERED",
        "COMPLETED",
    }


def test_delivery_status_payload_requires_proof_image_url():
    with pytest.raises(ValidationError, match="proof_image_url"):
        ShipmentStatusUpdatePayload(status=ShipmentStatus.DELIVERED)


def test_non_delivery_status_payload_does_not_require_proof_image_url():
    payload = ShipmentStatusUpdatePayload(status=ShipmentStatus.PICKED_UP)

    assert payload.proof_image_url is None
