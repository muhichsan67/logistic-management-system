from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.core.deps import require_role
from app.db.models import UserRole
from app.schemas.common import error_responses
from app.schemas.shipment import UploadResponse
from app.services import upload_service

router = APIRouter(prefix="/uploads", tags=["Uploads"],
                   dependencies=[Depends(require_role(UserRole.COURIER))])


@router.post("/proof", response_model=UploadResponse, status_code=status.HTTP_201_CREATED,
             summary="Upload bukti pengiriman (JPG/PNG, maks 5 MB)",
             responses=error_responses(401, 403, 422))
async def upload_proof(file: Annotated[UploadFile, File(description="JPG/PNG")]) -> UploadResponse:
    return UploadResponse(url=await upload_service.save_proof_image(file))
