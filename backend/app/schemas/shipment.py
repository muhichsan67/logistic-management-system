from decimal import Decimal
from typing import Annotated

from pydantic import Field

from app.db.models import ShipmentStatus
from app.schemas.base import APIModel, Name, NonEmptyStr, Phone, UTCDateTime

Weight = Annotated[Decimal, Field(gt=0, max_digits=6, decimal_places=2, examples=[0.5])]


class ShipmentCreate(APIModel):
    sender_name: Name
    sender_phone: Phone
    origin_address: NonEmptyStr
    recipient_name: Name
    recipient_phone: Phone
    destination_address: NonEmptyStr
    package_description: NonEmptyStr
    weight_kg: Weight


class ShipmentCreated(APIModel):
    id: int
    tracking_number: str
    status: ShipmentStatus
    created_at: UTCDateTime


class ShipmentOut(APIModel):
    id: int
    tracking_number: str
    status: ShipmentStatus
    sender_name: str
    sender_phone: str
    origin_address: str
    recipient_name: str
    recipient_phone: str
    destination_address: str
    package_description: str
    weight_kg: Decimal
    courier_id: int | None
    rejection_reason: str | None
    proof_image_url: str | None
    delivered_at: UTCDateTime | None
    created_at: UTCDateTime


class TrackingHistoryOut(APIModel):
    status: ShipmentStatus
    notes: str
    created_at: UTCDateTime


class TrackResponse(APIModel):
    tracking_number: str
    status: ShipmentStatus
    sender_name: str
    recipient_name: str
    destination_address: str
    history: list[TrackingHistoryOut]  # terlama -> terbaru


class HistoryDetailOut(TrackingHistoryOut):
    created_by_name: str | None = None  # hanya diisi untuk Admin


class ShipmentDetail(ShipmentOut):
    """Detail 1 shipment + riwayat. Dipakai Customer (by resi), Kurir & Admin (by id)."""

    customer_id: int
    customer_name: str | None = None
    courier_name: str | None = None
    courier_phone: str | None = None
    history: list[HistoryDetailOut]  # terlama -> terbaru


class ConfirmResponse(APIModel):
    message: str = "Pesanan dikonfirmasi selesai"
    current_status: ShipmentStatus


class StatusUpdateResponse(APIModel):
    message: str = "Status berhasil diperbarui"
    current_status: ShipmentStatus


class CourierStatusUpdate(APIModel):
    status: ShipmentStatus
    notes: NonEmptyStr | None = None
    proof_image_url: Annotated[str, Field(max_length=255)] | None = None


class AssignRequest(APIModel):
    courier_id: int = Field(gt=0)
    notes: NonEmptyStr | None = None


class AssignResponse(APIModel):
    message: str = "Kurir berhasil ditugaskan"
    shipment_id: int
    status: ShipmentStatus


class RejectRequest(APIModel):
    rejection_reason: NonEmptyStr


class RejectResponse(APIModel):
    message: str = "Delivery request ditolak"
    shipment_id: int
    status: ShipmentStatus


class UploadResponse(APIModel):
    url: str
