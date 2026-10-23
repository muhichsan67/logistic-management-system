from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DuplicateError, NotFoundError
from app.core.security import hash_password
from app.db.models import User, UserRole
from app.repositories.base import paginate
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.admin import CourierCreate, CourierUpdate
from app.schemas.common import PageParams
from app.services import auth_service
from app.services.admin_service import escape_like


async def _get_courier(db: AsyncSession, courier_id: int) -> User:
    user = await UserRepository(db).get_courier(courier_id)
    if user is None:
        raise NotFoundError("Kurir tidak ditemukan.")
    return user


async def list_couriers(
    db: AsyncSession, params: PageParams, *, is_active: bool | None, q: str | None
) -> tuple[list[User], int]:
    conds = [User.role == UserRole.COURIER]
    if is_active is not None:
        conds.append(User.is_active == is_active)
    if q and q.strip():
        like = f"%{escape_like(q.strip())}%"
        conds.append(or_(User.name.ilike(like, escape="\\"), User.email.ilike(like, escape="\\")))
    stmt = select(User).where(*conds).order_by(User.created_at.desc(), User.id.desc())
    count_stmt = select(func.count()).select_from(User).where(*conds)
    return await paginate(db, stmt, params, count_stmt=count_stmt)


async def create_courier(db: AsyncSession, data: CourierCreate) -> User:
    return await auth_service.create_user(
        db, name=data.name, email=data.email, phone=data.phone,
        password=data.password, role=UserRole.COURIER,
    )


async def update_courier(db: AsyncSession, courier_id: int, data: CourierUpdate) -> User:
    user = await _get_courier(db, courier_id)

    clash = []
    if data.email and data.email != user.email:
        clash.append(User.email == data.email)
    if data.phone and data.phone != user.phone:
        clash.append(User.phone == data.phone)
    if clash and await db.scalar(
        select(User.id).where(User.id != user.id, or_(*clash)).limit(1)
    ):
        raise DuplicateError("Email atau nomor telepon sudah dipakai akun lain.")

    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email
    if data.phone:
        user.phone = data.phone
    if data.password:
        user.password_hash = await hash_password(data.password)
        await RefreshTokenRepository(db).revoke_all_for_user(user.id)  # paksa login ulang
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise DuplicateError("Email atau nomor telepon sudah dipakai akun lain.") from exc
    return user


async def deactivate_courier(db: AsyncSession, courier_id: int) -> User:
    """Soft delete: is_active=false (riwayat tetap utuh). Idempotent."""
    user = await _get_courier(db, courier_id)
    if user.is_active:
        user.is_active = False
        await RefreshTokenRepository(db).revoke_all_for_user(user.id)
        await db.commit()
    return user
