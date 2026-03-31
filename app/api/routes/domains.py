from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.pipeline import PipelineService

router = APIRouter()

@router.get("/{domain}")
async def get_domain(domain: str, refresh: bool = False, db: AsyncSession = Depends(get_db)):
    pipeline = PipelineService(db)
    return await pipeline.get_domain(domain, force_refresh=refresh)
