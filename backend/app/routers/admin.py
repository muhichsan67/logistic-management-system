from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.core.deps import DBSession, require_role
from app.db.models import ShipmentStatus, User, UserRole
from app.schemas.admin import (
    AdminShipmentOut, CourierCreate, CourierUpdate, DashboardSummary, Period,
    SystemSettingsOut, SystemSettingsUpdate,
)
from app.schemas.auth import UserOut
from app.schemas.common import MessageResponse, Page, PageParams, error_responses
from app.schemas.shipment import (
    AssignRequest, AssignResponse, RejectRequest, RejectResponse, ShipmentDetail,
)
from app.services import (
    admin_service, courier_service, dashboard_service, settings_service,
    shipment_service as svc,
)

router = APIRouter(prefix="/admin", tags=["Admin"],
                   dependencies=[Depends(require_role(UserRole.ADMIN))])
Admin = Annotated[User, Depends(require_role(UserRole.ADMIN))]
Pagination = Annotated[PageParams, Depends()]


# ---------------- Shipments ----------------
@router.get("/shipments", response_model=Page[AdminShipmentOut],
            summary="Daftar semua pengiriman (PENDING terlambat di atas)",
            responses=error_responses(401, 403, 422))
async def list_shipments(
    db: DBSession, params: Pagination,
    status: Annotated[ShipmentStatus | None, Query()] = None,
    courier_id: Annotated[int | None, Query(gt=0)] = None,
    date_from: Annotated[date | None, Query(description="YYYY-MM-DD (zona waktu bisnis)")] = None,
    date_to: Annotated[date | None, Query(description="YYYY-MM-DD, inklusif")] = None,
    q: Annotated[str | None, Query(max_length=100, description="No. resi / nama pengirim / penerima")] = None,
) -> Page[AdminShipmentOut]:
    items, total = await admin_service.list_shipments(
        db, params, status=status, courier_id=courier_id,
        date_from=date_from, date_to=date_to, q=q,
    )
    return Page.build(items, total, params)


@router.get("/shipments/{id}", response_model=ShipmentDetail,
            summary="Detail pengiriman + log riwayat (dengan nama pelaku)",
            responses=error_responses(401, 403, 404))
async def shipment_detail(id: int, db: DBSession, admin: Admin) -> ShipmentDetail:
    return await svc.get_detail(db, admin, shipment_id=id)


@router.put("/shipments/{id}/assign", response_model=AssignResponse, summary="Tugaskan kurir",
            responses=error_responses(401, 403, 404, 409, 422))
async def assign(id: int, data: AssignRequest, db: DBSession, admin: Admin) -> AssignResponse:
    s = await svc.change_status(db, id, ShipmentStatus.ASSIGNED, admin,
                                courier_id=data.courier_id, notes=data.notes)
    return AssignResponse(shipment_id=s.id, status=s.status)


@router.put("/shipments/{id}/reject", response_model=RejectResponse, summary="Tolak DR",
            responses=error_responses(401, 403, 404, 409, 422))
async def reject(id: int, data: RejectRequest, db: DBSession, admin: Admin) -> RejectResponse:
    s = await svc.change_status(db, id, ShipmentStatus.REJECTED, admin,
                                rejection_reason=data.rejection_reason)
    return RejectResponse(shipment_id=s.id, status=s.status)


# ---------------- Dashboard ----------------
@router.get("/dashboard/summary", response_model=DashboardSummary, summary="Ringkasan dashboard",
            description=(
                "`7d`/`30d`: `volume_per_day` per hari. `12m`: per bulan (`date` = tanggal 1 bulan itu). "
                "`by_status` dihitung dari shipment yang dibuat dalam periode. "
                "`active` = ASSIGNED + PICKED_UP + IN_TRANSIT."),
            responses=error_responses(401, 403, 422))
async def dashboard_summary(db: DBSession, period: Period = "7d") -> DashboardSummary:
    return await dashboard_service.get_summary(db, period)


# ---------------- Couriers ----------------
@router.get("/couriers", response_model=Page[UserOut], summary="Daftar kurir",
            responses=error_responses(401, 403))
async def list_couriers(
    db: DBSession, params: Pagination,
    is_active: Annotated[bool | None, Query()] = None,
    q: Annotated[str | None, Query(max_length=100, description="Nama / email")] = None,
) -> Page[UserOut]:
    rows, total = await courier_service.list_couriers(db, params, is_active=is_active, q=q)
    return Page.build([UserOut.model_validate(u) for u in rows], total, params)


@router.post("/couriers", response_model=UserOut, status_code=status.HTTP_201_CREATED,
             summary="Buat akun kurir", responses=error_responses(401, 403, 409, 422))
async def create_courier(data: CourierCreate, db: DBSession) -> UserOut:
    return UserOut.model_validate(await courier_service.create_courier(db, data))


@router.put("/couriers/{id}", response_model=UserOut, summary="Ubah data kurir",
            responses=error_responses(401, 403, 404, 409, 422))
async def update_courier(id: int, data: CourierUpdate, db: DBSession) -> UserOut:
    return UserOut.model_validate(await courier_service.update_courier(db, id, data))


@router.patch("/couriers/{id}/deactivate", response_model=UserOut,
              summary="Nonaktifkan kurir (bukan DELETE)",
              responses=error_responses(401, 403, 404))
async def deactivate_courier(id: int, db: DBSession) -> UserOut:
    return UserOut.model_validate(await courier_service.deactivate_courier(db, id))


# ---------------- Settings ----------------
@router.get("/settings", response_model=SystemSettingsOut, summary="Ambil pengaturan sistem",
            responses=error_responses(401, 403))
async def get_settings_(db: DBSession) -> SystemSettingsOut:
    return SystemSettingsOut(**await settings_service.get_all_settings(db))


@router.put("/settings", response_model=MessageResponse, summary="Simpan pengaturan sistem",
            responses=error_responses(401, 403, 422))
async def update_settings(data: SystemSettingsUpdate, db: DBSession) -> MessageResponse:
    await settings_service.update_settings(db, data.to_dict())
    return MessageResponse(message="Pengaturan sistem berhasil disimpan")
