import asyncio
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from db.models.shipment import ShipmentStatus
from db.models.user import UserRole
from routers.admin import (
    assign_shipment,
    create_courier,
    get_courier_options,
    get_shipment_summary,
    reject_shipment,
    update_system_settings,
)
from schemas.admin import (
    AssignShipmentPayload,
    CourierCreatePayload,
    RejectShipmentPayload,
    SystemSettingsPayload,
)
from services.admin import (
    assign_shipment_service,
    get_courier_options_service,
    get_shipment_summary_service,
    reject_shipment_service,
    update_system_settings_service,
)


def run(awaitable):
    return asyncio.run(awaitable)


def make_shipment(status=ShipmentStatus.PENDING):
    return SimpleNamespace(
        id=100,
        tracking_number="TRX-20261022-0001",
        customer_id=10,
        courier_id=None,
        status=status,
        rejection_reason=None,
    )


def test_assign_shipment_service_assigns_active_courier(admin, courier):
    shipment = make_shipment()
    session = AsyncMock()
    session.add = Mock()
    session.scalar.side_effect = [shipment, courier]

    result = run(assign_shipment_service(100, courier.id, admin.id, session))

    assert result.status == ShipmentStatus.ASSIGNED
    assert result.courier_id == courier.id
    history = session.add.call_args.args[0]
    assert history.status == ShipmentStatus.ASSIGNED
    assert history.created_by == admin.id
    session.commit.assert_awaited_once()


def test_assign_shipment_service_rejects_missing_courier(admin):
    session = AsyncMock()
    session.add = Mock()
    session.scalar.side_effect = [make_shipment(), None]

    with pytest.raises(LookupError, match="Active courier"):
        run(assign_shipment_service(100, 999, admin.id, session))
    session.commit.assert_not_awaited()


@pytest.mark.parametrize(
    "current_status",
    [
        ShipmentStatus.ASSIGNED,
        ShipmentStatus.PICKED_UP,
        ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.DELIVERED,
        ShipmentStatus.COMPLETED,
        ShipmentStatus.REJECTED,
    ],
)
def test_assign_shipment_service_rejects_non_pending(admin, courier, current_status):
    session = AsyncMock()
    session.add = Mock()
    session.scalar.side_effect = [make_shipment(current_status), courier]

    with pytest.raises(ValueError, match="Only pending"):
        run(assign_shipment_service(100, courier.id, admin.id, session))


def test_reject_shipment_service_saves_reason_and_history(admin):
    shipment = make_shipment()
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = shipment

    result = run(
        reject_shipment_service(
            shipment.id,
            "  Invalid destination  ",
            admin.id,
            session,
        )
    )

    assert result.status == ShipmentStatus.REJECTED
    assert result.rejection_reason == "Invalid destination"
    history = session.add.call_args.args[0]
    assert history.status == ShipmentStatus.REJECTED
    assert history.created_by == admin.id
    session.commit.assert_awaited_once()


def test_reject_shipment_service_rejects_blank_reason(admin):
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = make_shipment()

    with pytest.raises(ValueError, match="must not be empty"):
        run(reject_shipment_service(100, "  ", admin.id, session))
    session.commit.assert_not_awaited()


def test_courier_options_service_returns_only_id_and_name():
    session = AsyncMock()
    session.add = Mock()
    session.scalars.return_value = SimpleNamespace(
        all=lambda: [
            SimpleNamespace(id=2, name="Courier A"),
            SimpleNamespace(id=1, name="Courier B"),
        ]
    )

    result = run(get_courier_options_service(session))

    assert result == [
        {"id": 2, "name": "Courier A"},
        {"id": 1, "name": "Courier B"},
    ]


def test_settings_service_upserts_both_settings():
    session = AsyncMock()
    session.add = Mock()
    session.get.return_value = None
    payload = SystemSettingsPayload(
        pending_alert_timeout_minutes=45,
        auto_complete_days=5,
    )

    result = run(update_system_settings_service(payload, session))

    assert result == {
        "pending_alert_timeout_minutes": 45,
        "auto_complete_days": 5,
    }
    assert session.add.call_count == 2
    session.commit.assert_awaited_once()


def test_summary_service_counts_statuses_and_delivered_today():
    row = SimpleNamespace(
        pending_orders=12,
        in_transit=45,
        delivered_today=28,
        rejected=3,
    )
    session = AsyncMock()
    session.add = Mock()
    session.execute.return_value = SimpleNamespace(one=lambda: row)

    result = run(get_shipment_summary_service(session))

    assert result == {
        "pending_orders": 12,
        "in_transit": 45,
        "delivered_today": 28,
        "rejected": 3,
    }


def test_admin_assignment_router_maps_missing_resource(admin):
    session = AsyncMock()
    with patch(
        "routers.admin.assign_shipment_service",
        side_effect=LookupError("Active courier not found"),
    ):
        with pytest.raises(HTTPException) as exc:
            run(
                assign_shipment(
                    100,
                    AssignShipmentPayload(courier_id=99),
                    session,
                    admin,
                )
            )
    assert exc.value.status_code == 404


def test_admin_rejection_router_maps_invalid_transition(admin):
    session = AsyncMock()
    with patch(
        "routers.admin.reject_shipment_service",
        side_effect=ValueError("Only pending shipments can be rejected"),
    ):
        with pytest.raises(HTTPException) as exc:
            run(
                reject_shipment(
                    100,
                    RejectShipmentPayload(rejection_reason="Reason"),
                    session,
                    admin,
                )
            )
    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == "INVALID_STATUS_TRANSITION"


def test_admin_settings_router_returns_saved_values(admin):
    session = AsyncMock()
    payload = SystemSettingsPayload(
        pending_alert_timeout_minutes=30,
        auto_complete_days=3,
    )
    with patch(
        "routers.admin.update_system_settings_service",
        return_value=payload.model_dump(),
    ):
        result = run(update_system_settings(payload, session, admin))
    assert result["data"] == payload.model_dump()


def test_admin_courier_create_router_maps_duplicate(admin):
    session = AsyncMock()
    payload = CourierCreatePayload(
        name="Courier",
        email="courier@example.com",
        phone="081234567890",
        password="Password123!",
    )
    with patch(
        "routers.admin.create_courier_service",
        side_effect=ValueError("Courier name or email already registered"),
    ):
        with pytest.raises(HTTPException) as exc:
            run(create_courier(payload, session, admin))
    assert exc.value.status_code == 409
    assert exc.value.detail["code"] == "DUPLICATE"


def test_admin_courier_options_router_returns_options(admin):
    session = AsyncMock()
    options = [{"id": 2, "name": "Courier"}]
    with patch(
        "routers.admin.get_courier_options_service",
        return_value=options,
    ):
        result = run(get_courier_options(session, admin))
    assert result["data"] == options


def test_admin_summary_router_returns_summary(admin):
    session = AsyncMock()
    summary = {
        "pending_orders": 1,
        "in_transit": 2,
        "delivered_today": 3,
        "rejected": 4,
    }
    with patch(
        "routers.admin.get_shipment_summary_service",
        return_value=summary,
    ):
        result = run(get_shipment_summary(session, admin))
    assert result["data"] == summary
