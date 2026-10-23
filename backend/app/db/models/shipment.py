from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, CheckConstraint, DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin
from app.db.models.enums import ShipmentStatus


class Shipment(TimestampMixin, Base):
    __tablename__ = "shipments"
    __table_args__ = (CheckConstraint("weight_kg > 0", name="check_weight_positive"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tracking_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    courier_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL")
    )

    sender_name: Mapped[str] = mapped_column(String(100), nullable=False)
    sender_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    origin_address: Mapped[str] = mapped_column(Text, nullable=False)

    recipient_name: Mapped[str] = mapped_column(String(100), nullable=False)
    recipient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    destination_address: Mapped[str] = mapped_column(Text, nullable=False)

    package_description: Mapped[str] = mapped_column(Text, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)

    status: Mapped[ShipmentStatus] = mapped_column(
        Enum(ShipmentStatus, name="shipment_status", create_type=False),
        default=ShipmentStatus.PENDING, server_default="PENDING", nullable=False,
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    proof_image_url: Mapped[str | None] = mapped_column(String(255))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # lazy="raise": paksa eksplisit selectinload() -> cegah N+1 & MissingGreenlet di async.
    histories: Mapped[list["TrackingHistory"]] = relationship(  # noqa: F821
        back_populates="shipment", order_by="TrackingHistory.created_at, TrackingHistory.id",
        lazy="raise",
    )
