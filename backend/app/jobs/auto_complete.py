"""Auto-complete DELIVERED -> COMPLETED setelah `auto_complete_days` hari (tiap 1 jam)."""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, InterfaceError, OperationalError

from app.core.exceptions import InvalidStatusTransition
from app.db.models import Shipment, ShipmentStatus
from app.db.session import AsyncSessionLocal
from app.services import settings_service, shipment_service

logger = logging.getLogger("app.jobs.auto_complete")
BACKOFF_SECONDS = (5, 15, 45)
_NOTES = "Pesanan otomatis diselesaikan oleh sistem karena tidak ada konfirmasi dari Customer."


async def run_once() -> int:
    async with AsyncSessionLocal() as db:
        days = await settings_service.get_int_setting(db, "auto_complete_days")
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        ids = (await db.scalars(
            select(Shipment.id).where(
                Shipment.status == ShipmentStatus.DELIVERED, Shipment.delivered_at <= cutoff
            )
        )).all()
        done = 0
        for shipment_id in ids:
            try:  # change_status mengunci baris + cek ulang status -> idempotent
                await shipment_service.change_status(
                    db, shipment_id, ShipmentStatus.COMPLETED, None, notes=_NOTES
                )
                done += 1
            except InvalidStatusTransition:
                await db.rollback()  # sudah diselesaikan pihak lain
        return done


async def auto_complete_job() -> None:
    for attempt in range(len(BACKOFF_SECONDS) + 1):
        try:
            count = await run_once()
            logger.info("auto_complete selesai: %d shipment diproses", count)
            return
        except (OperationalError, InterfaceError, DBAPIError, OSError):
            if attempt == len(BACKOFF_SECONDS):
                logger.error("auto_complete gagal total, menunggu jadwal berikutnya", exc_info=True)
                return
            delay = BACKOFF_SECONDS[attempt]
            logger.warning("auto_complete gagal (koneksi), retry dalam %ds", delay)
            await asyncio.sleep(delay)


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(auto_complete_job, "interval", hours=1, id="auto_complete",
                      max_instances=1, coalesce=True)
    return scheduler
