from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateError, UnauthorizedError
from app.core.security import (
    create_access_token, create_refresh_token, decode_token, hash_password, verify_password,
)
from app.db.models import RefreshToken, User, UserRole
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest, TokenResponse

_LOGIN_FAILED = "Email atau password salah."
_dummy_hash: str | None = None


async def _get_dummy_hash() -> str:
    """Hash dummy (dibuat sekali) agar waktu login "email tidak ada" setara "password salah"."""
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = await hash_password("dummy-password-1")
    return _dummy_hash


async def create_user(db: AsyncSession, *, name: str, email: str, phone: str,
                      password: str, role: UserRole) -> User:
    """Reusable: dipakai register (CUSTOMER) dan CRUD kurir admin (COURIER)."""
    repo = UserRepository(db)
    if await repo.email_or_phone_exists(email, phone):
        raise DuplicateError("Email atau nomor telepon sudah terdaftar.")
    user = repo.add(User(name=name, email=email, phone=phone, role=role,
                         password_hash=await hash_password(password)))
    try:
        await db.commit()
    except IntegrityError as exc:  # race condition antar request
        await db.rollback()
        raise DuplicateError("Email atau nomor telepon sudah terdaftar.") from exc
    return user


async def register_customer(db: AsyncSession, data: RegisterRequest) -> User:
    # Role SELALU CUSTOMER, tidak pernah dari payload.
    return await create_user(db, name=data.name, email=data.email, phone=data.phone,
                             password=data.password, role=UserRole.CUSTOMER)


async def _issue_tokens(db: AsyncSession, user: User) -> TokenResponse:
    access, expires_in = create_access_token(user.id, user.role.value)
    refresh, jti, expires_at = create_refresh_token(user.id)
    RefreshTokenRepository(db).add(RefreshToken(user_id=user.id, jti=jti, expires_at=expires_at))
    await db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=expires_in,
                         role=user.role, name=user.name)


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
    user = await UserRepository(db).get_by_email(email)
    ok = await verify_password(password, user.password_hash if user else await _get_dummy_hash())
    if not user or not ok or not user.is_active:
        raise UnauthorizedError(_LOGIN_FAILED)
    return await _issue_tokens(db, user)


async def refresh(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """Rotation: refresh token dipakai sekali. Pemakaian ulang token lama = indikasi
    pencurian -> semua refresh token user dicabut."""
    payload = decode_token(refresh_token, "refresh")
    repo = RefreshTokenRepository(db)
    record = await repo.get_by_jti_for_update(payload.jti)
    if record is None or record.user_id != payload.user_id:
        raise UnauthorizedError()
    if record.revoked_at is not None:
        await repo.revoke_all_for_user(record.user_id)
        await db.commit()
        raise UnauthorizedError("Refresh token sudah digunakan. Silakan login ulang.")
    user = await db.get(User, record.user_id)
    if user is None or not user.is_active:
        raise UnauthorizedError()
    record.revoked_at = datetime.now(timezone.utc)
    return await _issue_tokens(db, user)  # commit di sini mencakup revoke token lama


async def logout(db: AsyncSession, refresh_token: str) -> None:
    """Idempotent: token tidak valid/sudah dicabut tetap dianggap sukses."""
    try:
        payload = decode_token(refresh_token, "refresh")
    except UnauthorizedError:
        return
    record = await RefreshTokenRepository(db).get_by_jti_for_update(payload.jti)
    if record and record.revoked_at is None:
        record.revoked_at = datetime.now(timezone.utc)
        await db.commit()
