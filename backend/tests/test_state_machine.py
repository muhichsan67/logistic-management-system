import pytest
from pydantic import ValidationError

from app.db.models import ShipmentStatus as S
from app.schemas.auth import RegisterRequest
from app.services.shipment_service import DEFAULT_NOTES, TRANSITIONS


def test_every_status_has_default_note():
    assert set(DEFAULT_NOTES) == set(S)


def test_no_backward_or_skip_transitions():
    assert (S.IN_TRANSIT, S.PICKED_UP) not in TRANSITIONS
    assert (S.PENDING, S.DELIVERED) not in TRANSITIONS
    assert not any(src in (S.REJECTED, S.COMPLETED) for src, _ in TRANSITIONS)


def test_customer_cannot_cancel():
    assert all("CUSTOMER" not in a for (_, to), a in TRANSITIONS.items() if to is S.REJECTED)


@pytest.mark.parametrize("pw", ["short1", "alllettersss", "12345678"])
def test_weak_password_rejected(pw):
    with pytest.raises(ValidationError):
        RegisterRequest(name="Eko", email="a@b.co", phone="081234567890", password=pw)


def test_register_normalizes_email():
    r = RegisterRequest(name=" Eko ", email="EKO@Mail.COM", phone="081234567890", password="Abcdefg1")
    assert r.email == "eko@mail.com" and r.name == "Eko"
