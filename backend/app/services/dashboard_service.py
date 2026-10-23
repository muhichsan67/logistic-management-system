from datetime import date, datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from sqlalchemy import Date, cast, func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.models import Shipment, ShipmentStatus as S
from app.schemas.admin import DashboardSummary, DashboardTotals, Period, VolumePoint

ACTIVE = (S.ASSIGNED, S.PICKED_UP, S.IN_TRANSIT)
Granularity = Literal["day", "month"]


def period_start(period: Period, today: date) -> tuple[date, Granularity]:
    """7d/30d -> per hari (termasuk hari ini). 12m -> per bulan, 12 bulan termasuk bulan ini."""
    if period == "7d":
        return today - timedelta(days=6), "day"
    if period == "30d":
        return today - timedelta(days=29), "day"
    months = today.year * 12 + (today.month - 1) - 11
    return date(months // 12, months % 12 + 1, 1), "month"


def build_buckets(start: date, end: date, granularity: Granularity) -> list[date]:
    buckets, cur = [], start
    while cur <= end:
        buckets.append(cur)
        if granularity == "day":
            cur += timedelta(days=1)
        else:
            cur = date(cur.year + (cur.month == 12), cur.month % 12 + 1, 1)
    return buckets


def fill_zero(buckets: list[date], counts: dict[date, int]) -> list[VolumePoint]:
    """Bucket tanpa data tetap dikembalikan dengan count 0 (grafik tidak bolong)."""
    return [VolumePoint(date=b, count=counts.get(b, 0)) for b in buckets]


async def get_summary(db: AsyncSession, period: Period) -> DashboardSummary:
    tz_name = get_settings().BUSINESS_TIMEZONE
    tz = ZoneInfo(tz_name)  # juga memvalidasi nama zona sebelum dipakai sebagai literal SQL
    now = datetime.now(tz)
    today = now.date()
    start_date, granularity = period_start(period, today)
    start_dt = datetime.combine(start_date, datetime.min.time(), tzinfo=tz)
    today_start = datetime.combine(today, datetime.min.time(), tzinfo=tz)

    totals_row = (await db.execute(
        select(
            func.count().filter(Shipment.status.in_(ACTIVE)),
            func.count().filter(Shipment.status == S.PENDING),
            func.count().filter(Shipment.delivered_at >= today_start),
            func.count().filter(Shipment.status == S.COMPLETED),
        )
    )).one()

    # Zona & granularitas ditulis sebagai literal (bukan bind param) supaya ekspresi di SELECT
    # dan GROUP BY identik -> PostgreSQL tidak menolak "must appear in GROUP BY".
    tz_lit = literal_column("'" + tz_name.replace("'", "") + "'")
    local_created = func.timezone(tz_lit, Shipment.created_at)
    bucket = cast(func.date_trunc(literal_column(f"'{granularity}'"), local_created), Date)
    volume_rows = (await db.execute(
        select(bucket, func.count()).where(Shipment.created_at >= start_dt).group_by(bucket)
    )).all()

    status_rows = (await db.execute(
        select(Shipment.status, func.count())
        .where(Shipment.created_at >= start_dt).group_by(Shipment.status)
    )).all()
    by_status = {s.value: 0 for s in S}
    by_status.update({status.value: n for status, n in status_rows})

    return DashboardSummary(
        totals=DashboardTotals(
            active=totals_row[0], pending=totals_row[1],
            delivered_today=totals_row[2], completed=totals_row[3],
        ),
        volume_per_day=fill_zero(
            build_buckets(start_date, today, granularity), {d: n for d, n in volume_rows}
        ),
        by_status=by_status,
    )
