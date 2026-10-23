from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.core.exceptions import InvalidStatusTransition, NotFoundError, ValidationFailed
from app.db.models import ShipmentStatus as S
from app.schemas.common import PageParams
from app.services import courier_service, dashboard_service, settings_service
from app.services.shipment_service import change_status


def make_shipment(status=S.PENDING, customer_id=10, courier_id=None):
    return SimpleNamespace(
        id=100,
        tracking_number="TRX-20261022-0001",
        customer_id=customer_id,
        courier_id=courier_id,
        status=status,
        rejection_reason=None,
        proof_image_url=None,
        delivered_at=None,
    )


async def test_assign_shipment_assigns_active_courier(admin, courier):
    shipment = make_shipment()
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment
    db.get.return_value = courier

    result = await change_status(db, shipment.id, S.ASSIGNED, admin, courier_id=courier.id)

    assert result.status == S.ASSIGNED
    assert result.courier_id == courier.id
    history = db.add.call_args.args[0]
    assert history.status == S.ASSIGNED
    assert history.created_by == admin.id
    db.commit.assert_awaited_once()


async def test_assign_shipment_rejects_missing_courier(admin):
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = make_shipment()
    db.get.return_value = None

    with pytest.raises(NotFoundError, match="Kurir tidak ditemukan"):
        await change_status(db, 100, S.ASSIGNED, admin, courier_id=999)
    db.commit.assert_not_awaited()


@pytest.mark.parametrize(
    "current_status",
    [
        S.ASSIGNED,
        S.PICKED_UP,
        S.IN_TRANSIT,
        S.DELIVERED,
        S.COMPLETED,
        S.REJECTED,
    ],
)
async def test_assign_shipment_rejects_non_pending(admin, courier, current_status):
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = make_shipment(current_status)
    db.get.return_value = courier

    with pytest.raises(InvalidStatusTransition):
        await change_status(db, 100, S.ASSIGNED, admin, courier_id=courier.id)


async def test_reject_shipment_saves_reason_and_history(admin):
    shipment = make_shipment()
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = shipment

    result = await change_status(
        db, shipment.id, S.REJECTED, admin, rejection_reason="  Invalid destination  "
    )

    assert result.status == S.REJECTED
    assert result.rejection_reason == "Invalid destination"
    history = db.add.call_args.args[0]
    assert history.status == S.REJECTED
    assert history.created_by == admin.id
    db.commit.assert_awaited_once()


async def test_reject_shipment_rejects_blank_reason(admin):
    db = AsyncMock()
    db.add = Mock()
    db.scalar.return_value = make_shipment()

    with pytest.raises(ValidationFailed, match="Alasan penolakan"):
        await change_status(db, 100, S.REJECTED, admin, rejection_reason="  ")
    db.commit.assert_not_awaited()


async def test_list_couriers_scopes_to_active_couriers():
    db = AsyncMock()
    db.scalar.return_value = 2
    db.scalars.return_value = SimpleNamespace(
        all=lambda: [
            SimpleNamespace(id=2, name="Courier A"),
            SimpleNamespace(id=1, name="Courier B"),
        ]
    )

    rows, total = await courier_service.list_couriers(
        db, PageParams(page=1, limit=20), is_active=True, q=None
    )

    assert total == 2
    assert [r.id for r in rows] == [2, 1]


async def test_update_settings_upserts_whitelisted_keys():
    db = AsyncMock()
    db.add = Mock()
    db.get.return_value = None

    await settings_service.update_settings(
        db, {"pending_alert_timeout_minutes": "45", "auto_complete_days": "5"}
    )

    assert db.add.call_count == 2
    db.commit.assert_awaited_once()


async def test_get_all_settings_returns_fallbacks():
    db = AsyncMock()
    db.scalars.return_value = SimpleNamespace(all=lambda: [])

    result = await settings_service.get_all_settings(db)

    assert result == {"pending_alert_timeout_minutes": "30", "auto_complete_days": "3"}


async def test_dashboard_summary_returns_totals_and_buckets():
    db = AsyncMock()
    db.execute.side_effect = [
        SimpleNamespace(one=lambda: (5, 2, 1, 3)),
        SimpleNamespace(all=lambda: []),
        SimpleNamespace(all=lambda: []),
    ]

    result = await dashboard_service.get_summary(db, "7d")

    assert result.totals.active == 5
    assert result.totals.pending == 2
    assert result.totals.delivered_today == 1
    assert result.totals.completed == 3
    assert len(result.volume_per_day) == 7
    assert result.by_status["PENDING"] == 0
