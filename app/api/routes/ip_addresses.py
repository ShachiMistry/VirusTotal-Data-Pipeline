from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.pipeline import PipelineService

router = APIRouter()

@router.get("/{ip_address}")
async def get_ip(ip_address: str, refresh: bool = False, db: AsyncSession = Depends(get_db)):
    pipeline = PipelineService(db)
    return await pipeline.get_ip(ip_address, force_refresh=refresh)
