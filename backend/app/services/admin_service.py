"""Daftar shipment untuk Admin (filter + flag overdue dihitung di backend)."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.config import get_settings
from app.core.exceptions import ValidationFailed
from app.db.models import Shipment, ShipmentStatus, User
from app.repositories.base import paginate
from app.schemas.admin import AdminShipmentOut
from app.schemas.common import PageParams
from app.schemas.shipment import ShipmentOut
from app.services.settings_service import get_int_setting

_BASE_FIELDS = tuple(ShipmentOut.model_fields)


def escape_like(value: str) -> str:
    """Escape wildcard LIKE agar input user diperlakukan sebagai teks biasa."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def day_bounds(d: date, tz: ZoneInfo) -> datetime:
    return datetime.combine(d, time.min, tzinfo=tz)


async def list_shipments(
    db: AsyncSession, params: PageParams, *, status: ShipmentStatus | None,
    courier_id: int | None, date_from: date | None, date_to: date | None, q: str | None,
) -> tuple[list[AdminShipmentOut], int]:
    if date_from and date_to and date_from > date_to:
        raise ValidationFailed("date_from tidak boleh lebih besar dari date_to.")

    tz = ZoneInfo(get_settings().BUSINESS_TIMEZONE)
    timeout = await get_int_setting(db, "pending_alert_timeout_minutes")
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=timeout)
    overdue = and_(Shipment.status == ShipmentStatus.PENDING, Shipment.created_at <= cutoff)

    conds = []
    if status:
        conds.append(Shipment.status == status)
    if courier_id:
        conds.append(Shipment.courier_id == courier_id)
    if date_from:
        conds.append(Shipment.created_at >= day_bounds(date_from, tz))
    if date_to:
        conds.append(Shipment.created_at < day_bounds(date_to + timedelta(days=1), tz))
    if q and q.strip():
        like = f"%{escape_like(q.strip())}%"
        conds.append(or_(
            Shipment.tracking_number.ilike(like, escape="\\"),
            Shipment.sender_name.ilike(like, escape="\\"),
            Shipment.recipient_name.ilike(like, escape="\\"),
        ))

    courier, customer = aliased(User), aliased(User)
    stmt = (
        select(
            Shipment, overdue.label("is_overdue_pending"),
            courier.name.label("courier_name"), customer.name.label("customer_name"),
        )
        .outerjoin(courier, courier.id == Shipment.courier_id)
        .outerjoin(customer, customer.id == Shipment.customer_id)
        .where(*conds)
        .order_by(overdue.desc(), Shipment.created_at.desc(), Shipment.id.desc())
    )
    count_stmt = select(func.count()).select_from(Shipment).where(*conds)
    rows, total = await paginate(db, stmt, params, scalars=False, count_stmt=count_stmt)

    items = [
        AdminShipmentOut.model_validate({
            **{f: getattr(s, f) for f in _BASE_FIELDS},
            "is_overdue_pending": bool(is_overdue),
            "courier_name": courier_name, "customer_name": customer_name,
        })
        for s, is_overdue, courier_name, customer_name in rows
    ]
    return items, total
