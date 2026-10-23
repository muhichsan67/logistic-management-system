from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from core.deps import require_roles
from db.models.shipment import ShipmentStatus
from db.models.user import User, UserRole
from db.session import SessionDep
from schemas.base import BaseResponse
from schemas.shipment import (
    ShipmentCreatePayload,
    ShipmentCreateResponse,
    ShipmentDetailResponse,
    ShipmentListResponse,
    ShipmentStatusUpdatePayload,
    ShipmentTrackingResponse,
)
from services.shipment import (
    confirm_shipment_service,
    create_shipment_service,
    get_customer_shipments_service,
    get_courier_shipments_service,
    get_shipment_detail_service,
    get_shipment_tracking_service,
    update_courier_shipment_status_service,
)

router = APIRouter(
    prefix="/shipments",
    tags=["shipments"],
)

courier_router = APIRouter(
    prefix="/courier",
    tags=["courier"],
)

@courier_router.get(
    "/shipments",
    response_model=BaseResponse[ShipmentListResponse],
)
async def get_courier_shipments(
    session: SessionDep,
    current_user: User = Depends(require_roles(UserRole.COURIER)),
    tracking_number: str | None = Query(default=None, min_length=1),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> BaseResponse[ShipmentListResponse]:
    shipments = await get_courier_shipments_service(
        courier_id=current_user.id,
        session=session,
        tracking_number=tracking_number,
        page=page,
        limit=limit,
    )

    return {
        "status": "success",
        "message": "Courier shipments retrieved successfully",
        "data": shipments,
    }


@courier_router.put(
    "/shipments/{shipment_id}/status",
    response_model=BaseResponse[ShipmentCreateResponse],
)
async def update_courier_shipment_status(
    shipment_id: int,
    payload: ShipmentStatusUpdatePayload,
    session: SessionDep,
    current_user: User = Depends(require_roles(UserRole.COURIER)),
) -> BaseResponse[ShipmentCreateResponse]:
    try:
        shipment = await update_courier_shipment_status_service(
            shipment_id=shipment_id,
            courier_id=current_user.id,
            new_status=payload.status,
            session=session,
            notes=payload.notes,
            proof_image_url=payload.proof_image_url,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(exc), "code": "NOT_FOUND"},
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": str(exc), "code": "FORBIDDEN"},
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"detail": str(exc), "code": "INVALID_STATUS_TRANSITION"},
        ) from exc

    return {
        "status": "success",
        "message": "Shipment status updated successfully",
        "data": shipment,
    }


@router.post(
    "",
    response_model=BaseResponse[ShipmentCreateResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_shipment(
    payload: ShipmentCreatePayload,
    session: SessionDep,
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
) -> BaseResponse[ShipmentCreateResponse]:
    try:
        shipment = await create_shipment_service(payload, current_user, session)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "detail": str(exc),
                "code": "VALIDATION_ERROR",
            },
        ) from exc

    return {
        "status": "success",
        "message": "Shipment created successfully",
        "data": shipment,
    }


@router.get(
    "/me",
    response_model=BaseResponse[ShipmentListResponse],
)
async def get_my_shipments(
    session: SessionDep,
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
    shipment_status: ShipmentStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> BaseResponse[ShipmentListResponse]:
    shipments = await get_customer_shipments_service(
        customer_id=current_user.id,
        session=session,
        shipment_status=shipment_status,
        page=page,
        limit=limit,
    )

    return {
        "status": "success",
        "message": "Customer shipments retrieved successfully",
        "data": shipments,
    }


@router.get(
    "/{shipment_id}/detail",
    response_model=BaseResponse[ShipmentDetailResponse],
)
async def get_shipment_detail(
    shipment_id: int,
    session: SessionDep,
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.COURIER)
    ),
) -> BaseResponse[ShipmentDetailResponse]:
    try:
        shipment = await get_shipment_detail_service(
            shipment_id=shipment_id,
            current_user=current_user,
            session=session,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"detail": str(exc), "code": "NOT_FOUND"},
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": str(exc), "code": "FORBIDDEN"},
        ) from exc

    return {
        "status": "success",
        "message": "Shipment details retrieved successfully",
        "data": shipment,
    }


@router.put(
    "/{shipment_id}/confirm",
    response_model=BaseResponse[ShipmentCreateResponse],
)
async def confirm_shipment(
    shipment_id: int,
    session: SessionDep,
    current_user: User = Depends(require_roles(UserRole.CUSTOMER)),
) -> BaseResponse[ShipmentCreateResponse]:
    try:
        shipment = await confirm_shipment_service(
            shipment_id=shipment_id,
            customer_id=current_user.id,
            session=session,
        )
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "detail": str(exc),
                "code": "NOT_FOUND",
            },
        ) from exc
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "detail": str(exc),
                "code": "FORBIDDEN",
            },
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "detail": str(exc),
                "code": "INVALID_STATUS_TRANSITION",
            },
        ) from exc

    return {
        "status": "success",
        "message": "Shipment arrival confirmed successfully",
        "data": shipment,
    }


@router.get(
    "/{tracking_number}/track",
    response_model=BaseResponse[ShipmentTrackingResponse],
)
async def track_shipment(
    tracking_number: str,
    session: SessionDep,
) -> BaseResponse[ShipmentTrackingResponse] | JSONResponse:
    try:
        shipment = await get_shipment_tracking_service(tracking_number, session)
    except LookupError as exc:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": str(exc),
                "code": "NOT_FOUND",
            },
        )

    return {
        "status": "success",
        "message": "Shipment tracking information retrieved successfully",
        "data": shipment,
    }
