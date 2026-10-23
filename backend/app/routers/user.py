from fastapi import APIRouter, HTTPException, status

from core.deps import CurrentUser
from core.errors import error_payload
from db.session import SessionDep
from schemas.base import BaseResponse
from schemas.user import UserResponse, UserUpdatePayload
from services.user import update_current_user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me",
    response_model=BaseResponse[UserResponse],
)
async def get_current_user_profile(
    current_user: CurrentUser,
) -> BaseResponse[UserResponse]:
    return {
        "status": "success",
        "message": "Current user retrieved successfully",
        "data": current_user,
    }


@router.put(
    "/me",
    response_model=BaseResponse[UserResponse],
)
async def update_current_user_profile(
    payload: UserUpdatePayload,
    session: SessionDep,
    current_user: CurrentUser,
) -> BaseResponse[UserResponse]:
    try:
        user = await update_current_user_service(payload, current_user, session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=error_payload(
                str(exc),
                status.HTTP_409_CONFLICT,
                "DUPLICATE",
            ),
        ) from exc

    return {
        "status": "success",
        "message": "Current user updated successfully",
        "data": user,
    }
