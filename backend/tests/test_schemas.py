from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.db.models import ShipmentStatus
from app.schemas.admin import SystemSettingsUpdate
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.shipment import AssignRequest, CourierStatusUpdate, RejectRequest, ShipmentCreate


def test_register_payload_accepts_required_fields():
    payload = RegisterRequest(
        name="Customer",
        email="customer@example.com",
        phone="081234567890",
        password="Password123!",
    )
    assert payload.name == "Customer"
    assert payload.email == "customer@example.com"


def test_login_payload_requires_password():
    with pytest.raises(ValidationError):
        LoginRequest(email="customer@example.com")


def test_shipment_payload_trims_text_and_validates_weight():
    payload = ShipmentCreate(
        sender_name=" Sender ",
        sender_phone="081234567890",
        origin_address=" Origin ",
        recipient_name=" Recipient ",
        recipient_phone="081234567890",
        destination_address=" Destination ",
        package_description=" Package ",
        weight_kg=Decimal("1.25"),
    )
    assert payload.sender_name == "Sender"
    assert payload.recipient_name == "Recipient"
    assert payload.destination_address == "Destination"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("recipient_name", " "),
        ("destination_address", ""),
        ("package_description", " "),
        ("recipient_phone", "not-a-phone"),
    ],
)
def test_shipment_payload_rejects_invalid_fields(field, value):
    payload = {
        "sender_name": "Sender",
        "sender_phone": "081234567890",
        "origin_address": "Origin",
        "recipient_name": "Recipient",
        "recipient_phone": "081234567890",
        "destination_address": "Destination",
        "package_description": "Package",
        "weight_kg": 1,
    }
    payload[field] = value
    with pytest.raises(ValidationError):
        ShipmentCreate(**payload)


@pytest.mark.parametrize("weight", [0, -1, 10000])
def test_shipment_payload_rejects_invalid_weight(weight):
    with pytest.raises(ValidationError):
        ShipmentCreate(
            sender_name="Sender",
            sender_phone="081234567890",
            origin_address="Origin",
            recipient_name="Recipient",
            recipient_phone="081234567890",
            destination_address="Destination",
            package_description="Package",
            weight_kg=weight,
        )


def test_admin_payloads_require_positive_values_and_reason():
    assert AssignRequest(courier_id=1)
    assert RejectRequest(rejection_reason="Invalid address")
    assert SystemSettingsUpdate(pending_alert_timeout_minutes=30)

    with pytest.raises(ValidationError):
        AssignRequest(courier_id=0)
    with pytest.raises(ValidationError):
        RejectRequest(rejection_reason="")


def test_shipment_status_enum_contains_all_lifecycle_states():
    assert {s.value for s in ShipmentStatus} == {
        "PENDING",
        "REJECTED",
        "ASSIGNED",
        "PICKED_UP",
        "IN_TRANSIT",
        "DELIVERED",
        "COMPLETED",
    }


def test_delivery_status_allows_proof_url_to_be_optional_in_schema():
    # Di struktur baru, syarat proof_image_url untuk DELIVERED ditegakkan di
    # shipment_service.change_status (bukan di schema).
    payload = CourierStatusUpdate(status=ShipmentStatus.DELIVERED)
    assert payload.proof_image_url is None


def test_non_delivery_status_does_not_require_proof_image_url():
    payload = CourierStatusUpdate(status=ShipmentStatus.PICKED_UP)
    assert payload.proof_image_url is None
