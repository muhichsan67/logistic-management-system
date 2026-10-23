"""Logika bisnis shipment. SEMUA perubahan status wajib lewat change_status()."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.core.exceptions import (
    ForbiddenError, InvalidStatusTransition, NotFoundError, ValidationFailed,
)
from app.db.models import Shipment, ShipmentStatus as S, TrackingHistory, User, UserRole
from app.repositories.base import paginate
from app.schemas.common import PageParams
from app.schemas.shipment import ShipmentCreate, ShipmentDetail, ShipmentOut

SYSTEM = "SYSTEM"
A, C, CU = UserRole.ADMIN.value, UserRole.COURIER.value, UserRole.CUSTOMER.value

# (dari, ke) -> aktor yang diizinkan. Sumber kebenaran tunggal (BACKEND_RULES 4.1).
TRANSITIONS: dict[tuple[S, S], frozenset[str]] = {
    (S.PENDING, S.ASSIGNED): frozenset({A}),
    (S.PENDING, S.REJECTED): frozenset({A}),
    (S.ASSIGNED, S.PICKED_UP): frozenset({C}),
    (S.PICKED_UP, S.IN_TRANSIT): frozenset({C}),
    (S.IN_TRANSIT, S.DELIVERED): frozenset({C}),
    (S.DELIVERED, S.COMPLETED): frozenset({CU, SYSTEM}),
}

DEFAULT_NOTES: dict[S, str] = {
    S.PENDING: "Delivery request berhasil dibuat oleh Customer.",
    S.ASSIGNED: "Pesanan disetujui Admin dan kurir telah ditugaskan.",
    S.REJECTED: "Delivery request ditolak oleh Admin.",
    S.PICKED_UP: "Paket telah diambil oleh kurir dari lokasi pengirim.",
    S.IN_TRANSIT: "Paket dalam perjalanan menuju alamat tujuan.",
    S.DELIVERED: "Paket telah diterima di alamat tujuan.",
    S.COMPLETED: "Pesanan selesai.",
}

_LOCK_NAMESPACE = 1001  # namespace advisory lock nomor resi


async def generate_tracking_number(db: AsyncSession) -> str:
    """TRX-YYYYMMDD-NNNN, reset harian (zona waktu bisnis). Aman terhadap request bersamaan:
    advisory lock per-hari ditahan sampai transaksi pemanggil commit/rollback."""
    today = datetime.now(ZoneInfo(get_settings().BUSINESS_TIMEZONE)).date()
    prefix = f"TRX-{today:%Y%m%d}-"
    await db.execute(
        text("SELECT pg_advisory_xact_lock(:ns, :day)"),
        {"ns": _LOCK_NAMESPACE, "day": int(f"{today:%Y%m%d}")},
    )
    last = await db.scalar(
        select(Shipment.tracking_number)
        .where(Shipment.tracking_number.like(f"{prefix}%"))
        .order_by(func.length(Shipment.tracking_number).desc(), Shipment.tracking_number.desc())
        .limit(1)
    )
    seq = int(last.rsplit("-", 1)[1]) + 1 if last else 1
    return f"{prefix}{seq:04d}"


def _add_history(db: AsyncSession, shipment_id: int, status: S, notes: str | None,
                 actor: User | None) -> None:
    db.add(TrackingHistory(
        shipment_id=shipment_id, status=status,
        notes=(notes or "").strip() or DEFAULT_NOTES[status],
        created_by=actor.id if actor else None,
    ))


async def create_shipment(db: AsyncSession, customer: User, data: ShipmentCreate) -> Shipment:
    shipment = Shipment(
        tracking_number=await generate_tracking_number(db),
        customer_id=customer.id, status=S.PENDING, **data.model_dump(),
    )
    db.add(shipment)
    await db.flush()
    _add_history(db, shipment.id, S.PENDING, None, customer)
    await db.commit()  # shipment + riwayat awal + lock resi: satu transaksi
    await db.refresh(shipment)
    return shipment


async def change_status(
    db: AsyncSession, shipment_id: int, to_status: S, actor: User | None, *,
    notes: str | None = None, courier_id: int | None = None,
    rejection_reason: str | None = None, proof_image_url: str | None = None,
) -> Shipment:
    """Satu-satunya pintu perubahan status. actor=None berarti sistem (cron)."""
    shipment = await db.scalar(
        select(Shipment).where(Shipment.id == shipment_id)
        .with_for_update().execution_options(populate_existing=True)
    )
    if shipment is None:
        raise NotFoundError("Shipment tidak ditemukan.")

    role = actor.role.value if actor else SYSTEM
    # 1) kepemilikan (dicek dulu agar tidak membocorkan status milik orang lain)
    if role == CU and shipment.customer_id != actor.id:  # type: ignore[union-attr]
        raise ForbiddenError("Anda bukan pemilik shipment ini.")
    if role == C and shipment.courier_id != actor.id:  # type: ignore[union-attr]
        raise ForbiddenError("Shipment ini tidak ditugaskan kepada Anda.")

    # 2) transisi + hak aktor
    allowed = TRANSITIONS.get((shipment.status, to_status))
    if allowed is None:
        raise InvalidStatusTransition(
            f"Status tidak dapat diubah dari {shipment.status.value} ke {to_status.value}."
        )
    if role not in allowed:
        raise ForbiddenError("Role Anda tidak berhak melakukan perubahan status ini.")

    # 3) syarat per status tujuan
    if to_status is S.ASSIGNED:
        courier = await db.get(User, courier_id) if courier_id else None
        if courier is None:
            raise NotFoundError("Kurir tidak ditemukan.")
        if courier.role is not UserRole.COURIER or not courier.is_active:
            raise ValidationFailed("Kurir harus berrole COURIER dan berstatus aktif.")
        shipment.courier_id = courier.id
        notes = notes or f"Pesanan disetujui Admin dan ditugaskan ke Kurir {courier.name}."
    elif to_status is S.REJECTED:
        if not (rejection_reason and rejection_reason.strip()):
            raise ValidationFailed("Alasan penolakan wajib diisi.")
        shipment.rejection_reason = rejection_reason.strip()
        notes = notes or f"Delivery request ditolak: {shipment.rejection_reason}"
    elif to_status is S.DELIVERED:
        prefix = get_settings().UPLOAD_URL_PREFIX
        if not proof_image_url or not proof_image_url.startswith(prefix):
            raise ValidationFailed("proof_image_url wajib berupa URL hasil POST /uploads/proof.")
        shipment.proof_image_url = proof_image_url
        shipment.delivered_at = datetime.now(timezone.utc)

    shipment.status = to_status
    _add_history(db, shipment.id, to_status, notes, actor)
    await db.commit()  # update shipments + insert tracking_histories: satu transaksi
    return shipment


async def list_customer_shipments(
    db: AsyncSession, customer: User, status: S | None, params: PageParams
) -> tuple[list[Shipment], int]:
    stmt = select(Shipment).where(Shipment.customer_id == customer.id)
    if status:
        stmt = stmt.where(Shipment.status == status)
    return await paginate(db, stmt.order_by(Shipment.created_at.desc(), Shipment.id.desc()), params)


async def list_courier_shipments(
    db: AsyncSession, courier: User, status: S | None, params: PageParams
) -> tuple[list[Shipment], int]:
    stmt = select(Shipment).where(Shipment.courier_id == courier.id)
    if status:
        stmt = stmt.where(Shipment.status == status)
    return await paginate(db, stmt.order_by(Shipment.created_at.desc(), Shipment.id.desc()), params)


async def get_tracking(db: AsyncSession, tracking_number: str) -> Shipment:
    shipment = await db.scalar(
        select(Shipment).where(Shipment.tracking_number == tracking_number.strip().upper())
        .options(selectinload(Shipment.histories))
    )
    if shipment is None:
        raise NotFoundError("Nomor resi tidak ditemukan.")
    return shipment


_BASE_FIELDS = tuple(ShipmentOut.model_fields)


async def get_detail(
    db: AsyncSession, actor: User, *, shipment_id: int | None = None,
    tracking_number: str | None = None,
) -> ShipmentDetail:
    """Detail shipment + riwayat untuk pemilik (Customer), kurir yang ditugaskan, atau Admin."""
    stmt = select(Shipment).options(selectinload(Shipment.histories))
    if shipment_id is not None:
        stmt = stmt.where(Shipment.id == shipment_id)
    else:
        stmt = stmt.where(Shipment.tracking_number == (tracking_number or "").strip().upper())
    s = await db.scalar(stmt)
    if s is None:
        raise NotFoundError("Shipment tidak ditemukan.")
    if actor.role is UserRole.CUSTOMER and s.customer_id != actor.id:
        raise ForbiddenError("Anda bukan pemilik shipment ini.")
    if actor.role is UserRole.COURIER and s.courier_id != actor.id:
        raise ForbiddenError("Shipment ini tidak ditugaskan kepada Anda.")

    ids = {s.customer_id, s.courier_id, *(h.created_by for h in s.histories)} - {None}
    users = {u.id: u for u in (await db.scalars(select(User).where(User.id.in_(ids)))).all()}
    is_admin = actor.role is UserRole.ADMIN
    courier, customer = users.get(s.courier_id), users.get(s.customer_id)
    return ShipmentDetail.model_validate({
        **{f: getattr(s, f) for f in _BASE_FIELDS},
        "customer_id": s.customer_id,
        "customer_name": customer.name if customer else None,
        "courier_name": courier.name if courier else None,
        "courier_phone": courier.phone if courier else None,
        "history": [
            {"status": h.status, "notes": h.notes, "created_at": h.created_at,
             "created_by_name": (users[h.created_by].name if is_admin and h.created_by in users
                                 else ("Sistem" if is_admin else None))}
            for h in s.histories
        ],
    })
