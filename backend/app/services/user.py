from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.user import User
from schemas.user import UserUpdatePayload


async def update_current_user_service(
    payload: UserUpdatePayload,
    current_user: User,
    session: AsyncSession,
) -> User:
    duplicate_user = await session.scalar(
        select(User).where(
            User.id != current_user.id,
            (User.email == payload.email) | (User.name == payload.name),
        )
    )
    if duplicate_user is not None:
        if duplicate_user.email == payload.email:
            raise ValueError("Email is already registered")
        raise ValueError("Name is already registered")

    current_user.name = payload.name
    current_user.email = payload.email
    current_user.phone = payload.phone

    try:
        await session.commit()
        await session.refresh(current_user)
    except IntegrityError as exc:
        await session.rollback()
        raise ValueError("Could not update user due to a database constraint") from exc

    return current_user
