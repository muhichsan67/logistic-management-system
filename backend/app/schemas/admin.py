from datetime import date
from typing import Annotated, Any, Literal

from pydantic import BeforeValidator, StringConstraints, model_validator

from app.schemas.base import APIModel, Email, Name, Password, Phone
from app.schemas.shipment import ShipmentOut

Period = Literal["7d", "30d", "12m"]


class AdminShipmentOut(ShipmentOut):
    is_overdue_pending: bool
    customer_name: str | None = None
    courier_name: str | None = None


# ---- Dashboard ----
class DashboardTotals(APIModel):
    active: int
    pending: int
    delivered_today: int
    completed: int


class VolumePoint(APIModel):
    date: date
    count: int


class DashboardSummary(APIModel):
    totals: DashboardTotals
    volume_per_day: list[VolumePoint]
    by_status: dict[str, int]


# ---- Kurir ----
class CourierCreate(APIModel):
    name: Name
    email: Email
    phone: Phone
    password: Password


class CourierUpdate(APIModel):
    name: Name | None = None
    email: Email | None = None
    phone: Phone | None = None
    password: Password | None = None

    @model_validator(mode="after")
    def _at_least_one(self) -> "CourierUpdate":
        if all(getattr(self, f) is None for f in ("name", "email", "phone", "password")):
            raise ValueError("Minimal satu field harus diisi")
        return self


# ---- Settings (nilai berupa string integer positif, sesuai kontrak) ----
PositiveIntStr = Annotated[
    str,
    BeforeValidator(lambda v: str(v) if isinstance(v, int) and not isinstance(v, bool) else v),
    StringConstraints(strip_whitespace=True, pattern=r"^[1-9]\d{0,5}$"),
]


class SystemSettingsOut(APIModel):
    pending_alert_timeout_minutes: str
    auto_complete_days: str


class SystemSettingsUpdate(APIModel):
    pending_alert_timeout_minutes: PositiveIntStr | None = None
    auto_complete_days: PositiveIntStr | None = None

    @model_validator(mode="after")
    def _at_least_one(self) -> "SystemSettingsUpdate":
        if self.pending_alert_timeout_minutes is None and self.auto_complete_days is None:
            raise ValueError("Minimal satu pengaturan harus diisi")
        return self

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump(exclude_none=True)
