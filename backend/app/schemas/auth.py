from pydantic import Field

from app.db.models import UserRole
from app.schemas.base import APIModel, Email, Name, Password, Phone, UTCDateTime


class RegisterRequest(APIModel):
    name: Name
    email: Email
    phone: Phone
    password: Password

    model_config = APIModel.model_config | {
        "json_schema_extra": {"example": {
            "name": "Eko Customer", "email": "eko@gmail.com",
            "phone": "081234567892", "password": "Password123!"}}
    }


class RegisterResponse(APIModel):
    message: str = "Registrasi berhasil"
    user_id: int


class LoginRequest(APIModel):
    email: Email
    password: str = Field(min_length=1, max_length=128)  # tanpa aturan kekuatan saat login


class RefreshRequest(APIModel):
    refresh_token: str = Field(min_length=10)


class TokenResponse(APIModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Masa berlaku access token (detik)")
    role: UserRole
    name: str


class UserOut(APIModel):
    id: int
    name: str
    email: str
    phone: str
    role: UserRole
    is_active: bool
    created_at: UTCDateTime
