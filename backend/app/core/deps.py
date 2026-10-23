from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import decode_token
from app.db.models import User, UserRole
from app.db.session import AsyncSessionLocal

# auto_error=False -> kita sendiri yang melempar 401 dengan format {detail, code}
bearer_scheme = HTTPBearer(auto_error=False, description="Tempel **access_token** dari /auth/login")


async def get_db() -> AsyncIterator[AsyncSession]:
    """1 request = 1 session. Commit dilakukan di service; rollback otomatis bila error."""
    async with AsyncSessionLocal() as session:
        yield session


DBSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DBSession,
) -> User:
    if creds is None:
        raise UnauthorizedError()
    payload = decode_token(creds.credentials, "access")
    user = await db.get(User, payload.user_id)
    if user is None or not user.is_active:  # akun nonaktif ditolak di SETIAP request
        raise UnauthorizedError()
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: UserRole) -> Callable[..., Coroutine[Any, Any, User]]:
    """Pakai di router: `APIRouter(dependencies=[Depends(require_role(UserRole.ADMIN))])`
    atau di parameter: `user: User = Depends(require_role(UserRole.CUSTOMER))`."""

    async def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise ForbiddenError()
        return user

    return checker
