from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from db.models.user import UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    phone: str | None
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserUpdatePayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    phone: str | None = Field(default=None, min_length=8, max_length=20)

    @field_validator("name", "email", "phone")
    @classmethod
    def trim_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Field must not be empty")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if "@" not in value or value.startswith("@") or value.endswith("@"):
            raise ValueError("Invalid email address")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None and not value.lstrip("+").isdigit():
            raise ValueError("Phone must contain only digits and may start with +")
        return value
