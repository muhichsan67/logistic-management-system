from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import DBSession, require_role
from app.db.models import ShipmentStatus, User, UserRole
from app.schemas.common import Page, PageParams, error_responses
from app.schemas.shipment import (
    ConfirmResponse, ShipmentCreate, ShipmentCreated, ShipmentDetail, ShipmentOut,
    TrackingHistoryOut, TrackResponse,
)
from app.services import shipment_service as svc

router = APIRouter(prefix="/shipments", tags=["Shipments"])
Customer = Annotated[User, Depends(require_role(UserRole.CUSTOMER))]


@router.post("", response_model=ShipmentCreated, status_code=status.HTTP_201_CREATED,
             summary="Buat Delivery Request", responses=error_responses(401, 403, 422))
async def create_shipment(data: ShipmentCreate, db: DBSession, customer: Customer) -> ShipmentCreated:
    return ShipmentCreated.model_validate(await svc.create_shipment(db, customer, data))


@router.get("/me", response_model=Page[ShipmentOut], summary="Riwayat pengiriman saya",
            responses=error_responses(401, 403))
async def my_shipments(
    db: DBSession, customer: Customer, params: Annotated[PageParams, Depends()],
    status: Annotated[ShipmentStatus | None, Query()] = None,
) -> Page[ShipmentOut]:
    rows, total = await svc.list_customer_shipments(db, customer, status, params)
    return Page.build([ShipmentOut.model_validate(r) for r in rows], total, params)


@router.get("/me/{tracking_number}", response_model=ShipmentDetail,
            summary="Detail pengiriman milik saya + riwayat",
            responses=error_responses(401, 403, 404))
async def my_shipment_detail(tracking_number: str, db: DBSession, customer: Customer) -> ShipmentDetail:
    return await svc.get_detail(db, customer, tracking_number=tracking_number)


@router.get("/{tracking_number}/track", response_model=TrackResponse, summary="Lacak paket (publik)",
            responses=error_responses(404))
async def track(tracking_number: str, db: DBSession) -> TrackResponse:
    s = await svc.get_tracking(db, tracking_number)
    return TrackResponse(
        tracking_number=s.tracking_number, status=s.status, sender_name=s.sender_name,
        recipient_name=s.recipient_name, destination_address=s.destination_address,
        history=[TrackingHistoryOut.model_validate(h) for h in s.histories],
    )


@router.put("/{id}/confirm", response_model=ConfirmResponse, summary="Konfirmasi paket diterima",
            responses=error_responses(401, 403, 404, 409))
async def confirm(id: int, db: DBSession, customer: Customer) -> ConfirmResponse:
    s = await svc.change_status(db, id, ShipmentStatus.COMPLETED, customer)
    return ConfirmResponse(current_status=s.status)
