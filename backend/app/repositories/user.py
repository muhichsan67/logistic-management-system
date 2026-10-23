from sqlalchemy import or_, select

from app.db.models import User, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        return await self.db.scalar(select(User).where(User.email == email))

    async def email_or_phone_exists(self, email: str, phone: str) -> bool:
        stmt = select(User.id).where(or_(User.email == email, User.phone == phone)).limit(1)
        return await self.db.scalar(stmt) is not None

    async def get_courier(self, user_id: int) -> User | None:
        user = await self.db.get(User, user_id)
        return user if user and user.role is UserRole.COURIER else None
