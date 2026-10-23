from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, PlainSerializer, StringConstraints


def _to_utc_z(v: datetime) -> str:
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


# Semua datetime keluar sebagai ISO 8601 UTC berakhiran "Z" (BACKEND_RULES 2.3)
UTCDateTime = Annotated[datetime, PlainSerializer(_to_utc_z, return_type=str)]


class APIModel(BaseModel):
    """Base semua schema: baca dari ORM, trim whitespace otomatis."""

    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)


# ---- Tipe validasi reusable (dipakai lintas modul) ----
NonEmptyStr = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^(\d{8,20}|\+\d{7,19})$")]
Email = Annotated[EmailStr, AfterValidator(lambda v: v.lower())]


def _check_password(v: str) -> str:
    if len(v) < 8:
        raise ValueError("Password minimal 8 karakter")
    if len(v.encode()) > 72:
        raise ValueError("Password maksimal 72 byte")
    if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
        raise ValueError("Password harus memuat huruf dan angka")
    return v


Password = Annotated[str, AfterValidator(_check_password)]
