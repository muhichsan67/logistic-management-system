from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.deps import require_role
from app.db.models.user import User
from app.schemas.shipment import ShipmentCourierResponse
from app.services import courier_service

router = APIRouter(prefix="/courier", tags=["Courier"])

@router.get("/shipments", response_model=List[ShipmentCourierResponse])
async def get_courier_shipments(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("COURIER"))
):
    return await courier_service.get_assigned_shipments(
        db=db, 
        courier_id=current_user.id, 
        status_filter=status
    )