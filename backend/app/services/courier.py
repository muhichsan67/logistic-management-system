from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from app.db.models.shipment import Shipment

async def get_assigned_shipments(
    db: AsyncSession, 
    courier_id: int, 
    status_filter: Optional[str] = None
) -> List[Shipment]:
    # Query database: hanya mengembalikan shipment dengan courier_id kurir yang login
    query = select(Shipment).where(Shipment.courier_id == courier_id)
    
    if status_filter:
        query = query.where(Shipment.status == status_filter)
        
    query = query.order_by(Shipment.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()