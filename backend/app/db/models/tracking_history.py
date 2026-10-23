from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.enums import ShipmentStatus


class TrackingHistory(Base):
    """Append-only. Tidak ada endpoint untuk ubah/hapus."""

    __tablename__ = "tracking_histories"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    shipment_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("shipments.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[ShipmentStatus] = mapped_column(
        Enum(ShipmentStatus, name="shipment_status", create_type=False), nullable=False
    )
    notes: Mapped[str] = mapped_column(Text, nullable=False)
    created_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )  # NULL = sistem/cron
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    shipment: Mapped["Shipment"] = relationship(back_populates="histories", lazy="raise")  # noqa: F821
