from fastapi import APIRouter, Depends, Response, status

from app.core.deps import CurrentUser, DBSession
from app.core.rate_limit import rate_limit
from app.schemas.auth import (
    LoginRequest, RefreshRequest, RegisterRequest, RegisterResponse, TokenResponse, UserOut,
)
from app.schemas.common import error_responses
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED,
             summary="Registrasi Customer",
             dependencies=[Depends(rate_limit())], responses=error_responses(409, 422, 429))
async def register(data: RegisterRequest, db: DBSession) -> RegisterResponse:
    user = await auth_service.register_customer(db, data)
    return RegisterResponse(user_id=user.id)


@router.post("/login", response_model=TokenResponse, summary="Login (email + password)",
             dependencies=[Depends(rate_limit())], responses=error_responses(401, 422, 429))
async def login(data: LoginRequest, db: DBSession) -> TokenResponse:
    return await auth_service.login(db, data.email, data.password)


@router.post("/refresh", response_model=TokenResponse, summary="Tukar refresh token (rotation)",
             dependencies=[Depends(rate_limit())], responses=error_responses(401, 422, 429))
async def refresh(data: RefreshRequest, db: DBSession) -> TokenResponse:
    return await auth_service.refresh(db, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="Cabut refresh token",
             responses=error_responses(422))
async def logout(data: RefreshRequest, db: DBSession) -> Response:
    await auth_service.logout(db, data.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserOut, summary="Profil user yang sedang login",
            responses=error_responses(401))
async def me(user: CurrentUser) -> UserOut:
    return UserOut.model_validate(user)
