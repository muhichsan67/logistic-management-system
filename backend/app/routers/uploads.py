from fastapi import APIRouter, Depends, UploadFile, File, status
from pydantic import BaseModel

from app.core.deps import require_role
from app.db.models.user import User
from app.services import upload_service

router = APIRouter(prefix="/uploads", tags=["Uploads"])

class UploadProofResponse(BaseModel):
    url: str

@router.post("/proof", response_model=UploadProofResponse, status_code=status.HTTP_201_CREATED)
async def upload_proof(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("COURIER"))
):
    file_url = await upload_service.save_proof_image(file)
    return UploadProofResponse(url=file_url)