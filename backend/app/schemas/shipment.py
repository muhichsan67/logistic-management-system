from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from db.models.shipment import ShipmentStatus


class ShipmentCreatePayload(BaseModel):
    origin_address: str = Field(min_length=1)
    sender_phone: str = Field(min_length=8, max_length=20)
    recipient_name: str = Field(min_length=1, max_length=100)
    recipient_phone: str = Field(min_length=8, max_length=20)
    destination_address: str = Field(min_length=1)
    package_description: str = Field(min_length=1)
    weight_kg: Decimal = Field(gt=0, le=9999.99)

    @field_validator(
        "origin_address",
        "sender_phone",
        "recipient_name",
        "recipient_phone",
        "destination_address",
        "package_description",
    )
    @classmethod
    def trim_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Field must not be empty")
        return value

    @field_validator("sender_phone", "recipient_phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.lstrip("+").isdigit():
            raise ValueError("Phone must contain only digits and may start with +")
        return value


class ShipmentCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tracking_number: str
    status: ShipmentStatus
    created_at: datetime


class ShipmentStatusUpdatePayload(BaseModel):
    status: ShipmentStatus
    notes: str | None = Field(default=None, max_length=500)
    proof_image_url: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("notes", "proof_image_url")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def require_delivery_proof(self) -> "ShipmentStatusUpdatePayload":
        if self.status == ShipmentStatus.DELIVERED and not self.proof_image_url:
            raise ValueError(
                "proof_image_url is required when changing status to DELIVERED"
            )
        return self


class ShipmentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tracking_number: str
    status: ShipmentStatus
    recipient_name: str
    destination_address: str
    package_description: str
    weight_kg: Decimal
    created_at: datetime
    updated_at: datetime


class ShipmentListResponse(BaseModel):
    items: list[ShipmentListItem]
    total: int
    page: int
    limit: int


class ShipmentUserResponse(BaseModel):
    id: int
    name: str


class TrackingHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: ShipmentStatus
    notes: str
    created_at: datetime


class ShipmentDetailResponse(BaseModel):
    id: int
    tracking_number: str
    customer: ShipmentUserResponse
    courier: ShipmentUserResponse | None
    sender_name: str
    sender_phone: str
    origin_address: str
    recipient_name: str
    recipient_phone: str
    destination_address: str
    package_description: str
    weight_kg: Decimal
    status: ShipmentStatus
    rejection_reason: str | None
    proof_image_url: str | None
    delivered_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tracking_history: list[TrackingHistoryResponse]


class ShipmentTrackingResponse(BaseModel):
    id: int
    tracking_number: str
    customer: ShipmentUserResponse
    courier: ShipmentUserResponse | None
    status: ShipmentStatus
    sender_name: str
    sender_phone: str
    origin_address: str
    recipient_name: str
    recipient_phone: str
    destination_address: str
    package_description: str
    weight_kg: Decimal
    rejection_reason: str | None
    proof_image_url: str | None
    delivered_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tracking_history: list[TrackingHistoryResponse]
