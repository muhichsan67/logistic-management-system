from datetime import datetime, timezone
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.exceptions import (
    ForbiddenError,
    InvalidStatusTransition,
    NotFoundError,
    ValidationFailed,
)
from app.db.models import ShipmentStatus as S
from app.schemas.common import PageParams
from app.schemas.shipment import ShipmentCreate
from app.services.shipment_service import (
    change_status,
    create_shipment,
    get_detail,
    get_tracking,
    list_courier_shipments,
    list_customer_shipments,
)


def make_shipment(*, customer_id=10, courier_id=None, status=S.DELIVERED, **extra):
    data = dict(
        id=100,
        tracking_number="TRX-20261022-0001",
        customer_id=customer_id,
        courier_id=courier_id,
        status=status,
        sender_name="Sender",
        sender_phone="081234567890",
        origin_address="Origin",
        recipient_name="Recipient",
        recipient_phone="081234567893",
        destination_address="Destination",
        package_description="Package",
        weight_kg=Decimal("2.5"),
        rejection_reason=None,
        proof_image_url=None,
        delivered_at=None,
        created_at=datetime(2026, 10, 22, tzinfo=timezone.utc),
        updated_at=datetime(2026, 10, 22, tzinfo=timezone.utc),
        histories=[],
    )
    data.update(extra)
    return SimpleNamespace(**data)


async def test_create_shipment_adds_shipment_and_initial_history(customer):
    db = AsyncMock()
    db.add = Mock()

    def flush():
        db.add.call_args_list[0].args[0].id = 100

    db.flush.side_effect = flush
    db.refresh.return_value = None

    with patch(
        "app.services.shipment_service.generate_tracking_number",
        new=AsyncMock(return_value="TRX-20261022-0001"),
    ):
        result = await create_shipment(
            db,
            customer,
            ShipmentCreate(
                sender_name="Sender",
                sender_phone="081234567890",
                origin_address="Origin",
                recipient_name="Recipient",
                recipient_phone="081234567893",
                destination_address="Destination",
                package_description="Package",
                weight_kg=2.5,
            ),
        )

    assert result.customer_id == customer.id
    assert result.status == S.PENDING
    assert db.add.call_count == 2
    db.commit.assert_awaited_once()


async def test_confirm_shipment_changes_delivered_to_completed(customer):
    shipment = make_shipment(customer_id=customer.id, status=S.DELIVERED)
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment

    result = await change_status(db, shipment.id, S.COMPLETED, customer)

    assert result.status == S.COMPLETED
    db.add.assert_called_once()
    history = db.add.call_args.args[0]
    assert history.status == S.COMPLETED
    assert history.created_by == customer.id
    db.commit.assert_awaited_once()


async def test_confirm_shipment_rejects_other_customer(customer):
    shipment = make_shipment(customer_id=999, status=S.DELIVERED)
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment

    with pytest.raises(ForbiddenError):
        await change_status(db, shipment.id, S.COMPLETED, customer)
    db.commit.assert_not_awaited()


@pytest.mark.parametrize(
    "current_status",
    [S.PENDING, S.ASSIGNED, S.PICKED_UP, S.IN_TRANSIT, S.COMPLETED, S.REJECTED],
)
async def test_confirm_shipment_rejects_non_delivered(customer, current_status):
    shipment = make_shipment(customer_id=customer.id, status=current_status)
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment

    with pytest.raises(InvalidStatusTransition):
        await change_status(db, shipment.id, S.COMPLETED, customer)
    db.commit.assert_not_awaited()


async def test_list_customer_shipments_scopes_and_paginates(customer):
    db = AsyncMock()
    db.scalar.return_value = 2
    db.scalars.return_value = SimpleNamespace(all=lambda: ["shipment-1", "shipment-2"])

    rows, total = await list_customer_shipments(
        db, customer, S.IN_TRANSIT, PageParams(page=2, limit=10)
    )

    assert rows == ["shipment-1", "shipment-2"]
    assert total == 2
    db.scalars.assert_awaited_once()


async def test_list_courier_shipments_scopes_and_paginates(courier):
    db = AsyncMock()
    db.scalar.return_value = 1
    db.scalars.return_value = SimpleNamespace(all=lambda: ["assigned-shipment"])

    rows, total = await list_courier_shipments(
        db, courier, S.ASSIGNED, PageParams(page=2, limit=10)
    )

    assert rows == ["assigned-shipment"]
    assert total == 1
    db.scalars.assert_awaited_once()


@pytest.mark.parametrize(
    ("current_status", "next_status"),
    [(S.ASSIGNED, S.PICKED_UP), (S.PICKED_UP, S.IN_TRANSIT)],
)
async def test_courier_status_advances_sequentially(courier, current_status, next_status):
    shipment = make_shipment(courier_id=courier.id, status=current_status)
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment

    result = await change_status(db, shipment.id, next_status, courier)

    assert result.status == next_status
    history = db.add.call_args.args[0]
    assert history.status == next_status
    assert history.created_by == courier.id
    db.commit.assert_awaited_once()


async def test_courier_status_requires_proof_for_delivery(courier):
    shipment = make_shipment(courier_id=courier.id, status=S.IN_TRANSIT)
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment

    with pytest.raises(ValidationFailed, match="proof_image_url"):
        await change_status(db, shipment.id, S.DELIVERED, courier)
    db.commit.assert_not_awaited()
    db.add.assert_not_called()


async def test_courier_status_saves_delivery_proof(courier):
    shipment = make_shipment(courier_id=courier.id, status=S.IN_TRANSIT)
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment

    result = await change_status(
        db, shipment.id, S.DELIVERED, courier, proof_image_url="/static/proof.jpg"
    )

    assert result.status == S.DELIVERED
    assert result.proof_image_url == "/static/proof.jpg"
    assert result.delivered_at is not None
    history = db.add.call_args.args[0]
    assert history.status == S.DELIVERED
    db.commit.assert_awaited_once()


async def test_courier_status_rejects_unassigned_courier(courier):
    shipment = make_shipment(courier_id=999, status=S.ASSIGNED)
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment

    with pytest.raises(ForbiddenError, match="tidak ditugaskan"):
        await change_status(db, shipment.id, S.PICKED_UP, courier)
    db.commit.assert_not_awaited()


async def test_get_tracking_returns_shipment():
    shipment = make_shipment(status=S.IN_TRANSIT)
    db = AsyncMock()
    db.scalar.return_value = shipment

    result = await get_tracking(db, "trx-20261022-0001")

    assert result is shipment


async def test_get_tracking_raises_not_found():
    db = AsyncMock()
    db.scalar.return_value = None

    with pytest.raises(NotFoundError):
        await get_tracking(db, "TRX-UNKNOWN")


async def test_get_detail_returns_customer_and_courier_names(customer, courier):
    shipment = make_shipment(
        customer_id=customer.id,
        courier_id=courier.id,
        status=S.IN_TRANSIT,
    )
    db = AsyncMock()
    db.scalar.return_value = shipment
    db.scalars.return_value = SimpleNamespace(all=lambda: [customer, courier])

    result = await get_detail(db, customer, shipment_id=shipment.id)

    assert result.customer_name == customer.name
    assert result.courier_name == courier.name
    assert result.courier_phone == courier.phone
    assert result.history == []

