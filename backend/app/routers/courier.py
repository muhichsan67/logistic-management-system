from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.deps import DBSession, require_role
from app.db.models import ShipmentStatus, User, UserRole
from app.schemas.common import Page, PageParams, error_responses
from app.schemas.shipment import (
    CourierStatusUpdate, ShipmentDetail, ShipmentOut, StatusUpdateResponse,
)
from app.services import shipment_service as svc

router = APIRouter(prefix="/courier", tags=["Courier"])
Courier = Annotated[User, Depends(require_role(UserRole.COURIER))]


@router.get("/shipments", response_model=Page[ShipmentOut], summary="Daftar tugas saya",
            responses=error_responses(401, 403))
async def my_tasks(
    db: DBSession, courier: Courier, params: Annotated[PageParams, Depends()],
    status: Annotated[ShipmentStatus | None, Query()] = None,
) -> Page[ShipmentOut]:
    rows, total = await svc.list_courier_shipments(db, courier, status, params)
    return Page.build([ShipmentOut.model_validate(r) for r in rows], total, params)


@router.get("/shipments/{id}", response_model=ShipmentDetail, summary="Detail tugas + riwayat",
            responses=error_responses(401, 403, 404))
async def task_detail(id: int, db: DBSession, courier: Courier) -> ShipmentDetail:
    return await svc.get_detail(db, courier, shipment_id=id)


@router.put("/shipments/{id}/status", response_model=StatusUpdateResponse,
            summary="Update status (PICKED_UP / IN_TRANSIT / DELIVERED)",
            responses=error_responses(401, 403, 404, 409, 422))
async def update_status(id: int, data: CourierStatusUpdate, db: DBSession,
                        courier: Courier) -> StatusUpdateResponse:
    s = await svc.change_status(db, id, data.status, courier, notes=data.notes,
                                proof_image_url=data.proof_image_url)
    return StatusUpdateResponse(current_status=s.status)
