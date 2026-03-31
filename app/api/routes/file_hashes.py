from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.pipeline import PipelineService

router = APIRouter()

@router.get("/{file_hash}")
async def get_file_hash(file_hash: str, refresh: bool = False, db: AsyncSession = Depends(get_db)):
    pipeline = PipelineService(db)
    return await pipeline.get_file_hash(file_hash, force_refresh=refresh)
