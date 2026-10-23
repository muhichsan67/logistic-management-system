import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException

from db.models.shipment import ShipmentStatus
from db.models.user import UserRole
from routers.shipment import (
    confirm_shipment,
    create_shipment,
    get_courier_shipments,
    get_my_shipments,
    get_shipment_detail,
    track_shipment,
    update_courier_shipment_status,
)
from schemas.shipment import ShipmentCreatePayload, ShipmentStatusUpdatePayload
from services.shipment import (
    confirm_shipment_service,
    create_shipment_service,
    get_courier_shipments_service,
    get_customer_shipments_service,
    get_shipment_tracking_service,
    update_courier_shipment_status_service,
)


def run(awaitable):
    return asyncio.run(awaitable)


def make_shipment(customer_id=10, status=ShipmentStatus.DELIVERED):
    return SimpleNamespace(
        id=100,
        tracking_number="TRX-20261022-0001",
        customer_id=customer_id,
        courier_id=20,
        status=status,
        delivered_at=datetime.now(timezone.utc),
    )


def test_create_shipment_service_adds_shipment_and_initial_history(customer):
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = None

    async def flush():
        session.add.call_args_list[0].args[0].id = 100

    session.flush.side_effect = flush
    session.refresh.side_effect = lambda value: None

    with patch("services.shipment.datetime") as datetime_mock:
        datetime_mock.now.return_value = SimpleNamespace(
            strftime=lambda format_string: "20261022"
        )
        result = run(
            create_shipment_service(
                ShipmentCreatePayload(
                    origin_address="Origin",
                    sender_phone="081234567890",
                    recipient_name="Recipient",
                    recipient_phone="081234567893",
                    destination_address="Destination",
                    package_description="Package",
                    weight_kg=2.5,
                ),
                customer,
                session,
            )
        )

    assert result.customer_id == customer.id
    assert result.status == ShipmentStatus.PENDING
    assert session.add.call_count == 2
    session.commit.assert_awaited_once()


def test_confirm_shipment_service_changes_delivered_to_completed(customer):
    shipment = make_shipment(customer.id)
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = shipment

    result = run(confirm_shipment_service(shipment.id, customer.id, session))

    assert result.status == ShipmentStatus.COMPLETED
    session.add.assert_called_once()
    history = session.add.call_args.args[0]
    assert history.status == ShipmentStatus.COMPLETED
    assert history.created_by == customer.id
    session.commit.assert_awaited_once()


def test_confirm_shipment_service_rejects_other_customer(customer):
    shipment = make_shipment(customer_id=999)
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = shipment

    with pytest.raises(PermissionError):
        run(confirm_shipment_service(shipment.id, customer.id, session))
    session.commit.assert_not_awaited()


@pytest.mark.parametrize(
    "current_status",
    [
        ShipmentStatus.PENDING,
        ShipmentStatus.ASSIGNED,
        ShipmentStatus.PICKED_UP,
        ShipmentStatus.IN_TRANSIT,
        ShipmentStatus.COMPLETED,
        ShipmentStatus.REJECTED,
    ],
)
def test_confirm_shipment_service_rejects_non_delivered_status(
    customer,
    current_status,
):
    shipment = make_shipment(customer.id, current_status)
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = shipment

    with pytest.raises(ValueError, match="Only delivered"):
        run(confirm_shipment_service(shipment.id, customer.id, session))
    session.commit.assert_not_awaited()


def test_customer_shipments_service_scopes_to_customer_and_paginates():
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = 2
    result = SimpleNamespace(all=lambda: ["shipment-1", "shipment-2"])
    session.scalars.return_value = result

    response = run(
        get_customer_shipments_service(
            customer_id=10,
            session=session,
            shipment_status=ShipmentStatus.IN_TRANSIT,
            page=2,
            limit=10,
        )
    )

    assert response == {
        "items": ["shipment-1", "shipment-2"],
        "total": 2,
        "page": 2,
        "limit": 10,
    }
    session.scalars.assert_awaited_once()


def test_courier_shipments_service_scopes_to_courier_and_searches_tracking_number():
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = 1
    session.scalars.return_value = SimpleNamespace(
        all=lambda: ["assigned-shipment"]
    )

    response = run(
        get_courier_shipments_service(
            courier_id=20,
            session=session,
            tracking_number="TRX-20261023",
            page=2,
            limit=10,
        )
    )

    assert response == {
        "items": ["assigned-shipment"],
        "total": 1,
        "page": 2,
        "limit": 10,
    }
    session.scalar.assert_awaited_once()
    session.scalars.assert_awaited_once()


@pytest.mark.parametrize(
    ("current_status", "next_status"),
    [
        (ShipmentStatus.ASSIGNED, ShipmentStatus.PICKED_UP),
        (ShipmentStatus.PICKED_UP, ShipmentStatus.IN_TRANSIT),
    ],
)
def test_courier_status_service_advances_sequentially(
    courier,
    current_status,
    next_status,
):
    shipment = make_shipment(status=current_status)
    shipment.courier_id = courier.id
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = shipment

    result = run(
        update_courier_shipment_status_service(
            shipment.id,
            courier.id,
            next_status,
            session,
        )
    )

    assert result.status == next_status
    history = session.add.call_args.args[0]
    assert history.status == next_status
    assert history.created_by == courier.id
    session.commit.assert_awaited_once()


def test_courier_status_service_requires_proof_for_delivery(courier):
    shipment = make_shipment(status=ShipmentStatus.IN_TRANSIT)
    shipment.courier_id = courier.id
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = shipment

    with pytest.raises(ValueError, match="proof_image_url"):
        run(
            update_courier_shipment_status_service(
                shipment.id,
                courier.id,
                ShipmentStatus.DELIVERED,
                session,
            )
        )

    session.commit.assert_not_awaited()
    session.add.assert_not_called()


def test_courier_status_service_saves_delivery_proof(courier):
    shipment = make_shipment(status=ShipmentStatus.IN_TRANSIT)
    shipment.courier_id = courier.id
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = shipment

    result = run(
        update_courier_shipment_status_service(
            shipment.id,
            courier.id,
            ShipmentStatus.DELIVERED,
            session,
            proof_image_url="https://example.com/proof.jpg",
        )
    )

    assert result.status == ShipmentStatus.DELIVERED
    assert result.proof_image_url == "https://example.com/proof.jpg"
    assert result.delivered_at is not None
    history = session.add.call_args.args[0]
    assert history.status == ShipmentStatus.DELIVERED
    session.commit.assert_awaited_once()


def test_courier_status_service_rejects_unassigned_courier(courier):
    shipment = make_shipment(status=ShipmentStatus.ASSIGNED)
    shipment.courier_id = 999
    session = AsyncMock()
    session.add = Mock()
    session.scalar.return_value = shipment

    with pytest.raises(PermissionError, match="not assigned"):
        run(
            update_courier_shipment_status_service(
                shipment.id,
                courier.id,
                ShipmentStatus.PICKED_UP,
                session,
            )
        )

    session.commit.assert_not_awaited()


def test_tracking_service_returns_customer_and_courier_objects(customer, courier):
    shipment = SimpleNamespace(
        id=100,
        tracking_number="TRX-20261023-0001",
        status=ShipmentStatus.IN_TRANSIT,
        sender_name=customer.name,
        sender_phone="081234567890",
        origin_address="Origin",
        recipient_name="Recipient",
        recipient_phone="081234567893",
        destination_address="Destination",
        package_description="Package",
        weight_kg=2.5,
        rejection_reason=None,
        proof_image_url=None,
        delivered_at=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    session = AsyncMock()
    session.execute.return_value = SimpleNamespace(
        one_or_none=lambda: (shipment, customer, courier)
    )
    session.scalars.return_value = SimpleNamespace(all=lambda: [])

    response = run(
        get_shipment_tracking_service(
            shipment.tracking_number,
            session,
        )
    )

    assert response["customer"] == {
        "id": customer.id,
        "name": customer.name,
    }
    assert response["courier"] == {
        "id": courier.id,
        "name": courier.name,
    }
    assert response["tracking_history"] == []


def test_courier_shipments_router_passes_authenticated_courier(courier):
    session = AsyncMock()
    response = {"items": [], "total": 0, "page": 1, "limit": 20}
    with patch(
        "routers.shipment.get_courier_shipments_service",
        return_value=response,
    ) as service:
        result = run(get_courier_shipments(session, courier, None, 1, 20))

    service.assert_called_once_with(
        courier_id=courier.id,
        session=session,
        tracking_number=None,
        page=1,
        limit=20,
    )
    assert result["data"] == response


def test_courier_status_router_passes_delivery_proof(courier):
    session = AsyncMock()
    shipment = make_shipment(status=ShipmentStatus.DELIVERED)
    payload = ShipmentStatusUpdatePayload(
        status=ShipmentStatus.DELIVERED,
        proof_image_url="https://example.com/proof.jpg",
    )
    with patch(
        "routers.shipment.update_courier_shipment_status_service",
        return_value=shipment,
    ) as service:
        result = run(
            update_courier_shipment_status(
                shipment.id,
                payload,
                session,
                courier,
            )
        )

    service.assert_called_once_with(
        shipment_id=shipment.id,
        courier_id=courier.id,
        new_status=ShipmentStatus.DELIVERED,
        session=session,
        notes=None,
        proof_image_url="https://example.com/proof.jpg",
    )
    assert result["data"] == shipment


def test_create_shipment_router_maps_service_validation_error(customer):
    session = AsyncMock()
    session.add = Mock()
    payload = ShipmentCreatePayload(
        origin_address="Origin",
        sender_phone="081234567890",
        recipient_name="Recipient",
        recipient_phone="081234567893",
        destination_address="Destination",
        package_description="Package",
        weight_kg=2.5,
    )
    with patch(
        "routers.shipment.create_shipment_service",
        side_effect=ValueError("Default origin address is not configured"),
    ):
        with pytest.raises(HTTPException) as exc:
            run(create_shipment(payload, session, customer))
    assert exc.value.status_code == 400
    assert exc.value.detail["code"] == "VALIDATION_ERROR"


def test_confirm_shipment_router_maps_not_found(customer):
    session = AsyncMock()
    session.add = Mock()
    with patch(
        "routers.shipment.confirm_shipment_service",
        side_effect=LookupError("Shipment not found"),
    ):
        with pytest.raises(HTTPException) as exc:
            run(confirm_shipment(100, session, customer))
    assert exc.value.status_code == 404


def test_get_my_shipments_router_passes_authenticated_customer(customer):
    session = AsyncMock()
    session.add = Mock()
    response = {"items": [], "total": 0, "page": 1, "limit": 20}
    with patch(
        "routers.shipment.get_customer_shipments_service",
        return_value=response,
    ) as service:
        result = run(get_my_shipments(session, customer, None, 1, 20))

    service.assert_called_once_with(
        customer_id=customer.id,
        session=session,
        shipment_status=None,
        page=1,
        limit=20,
    )
    assert result["data"] == response


def test_detail_router_maps_forbidden():
    courier = SimpleNamespace(id=20, role=UserRole.COURIER)
    session = AsyncMock()
    session.add = Mock()
    with patch(
        "routers.shipment.get_shipment_detail_service",
        side_effect=PermissionError("You are not assigned"),
    ):
        with pytest.raises(HTTPException) as exc:
            run(get_shipment_detail(100, session, courier))
    assert exc.value.status_code == 403


def test_public_tracking_router_returns_not_found_response():
    session = AsyncMock()
    session.add = Mock()
    with patch(
        "routers.shipment.get_shipment_tracking_service",
        side_effect=LookupError("Shipment not found"),
    ):
        response = run(track_shipment("TRX-UNKNOWN", session))
    assert response.status_code == 404
