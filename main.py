from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db, engine, Base
import models
from virustotal_client import fetch_vt_data
import datetime
from cachetools import TTLCache
import re
from typing import Optional
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="VirusTotal Data Pipeline",
    description="API to ingest and expose VirusTotal data for Domains, IPs, and Hashes with dual caching (Memory + SQLite)."
)

# Initialize database
models.Base.metadata.create_all(bind=engine)

# In-Memory Cache: Stores up to 100 recent fetch results for 60 seconds.
memory_cache = TTLCache(maxsize=100, ttl=60)

# Database Cache TTL in hours
DB_CACHE_TTL_HOURS = 24

@app.get("/", include_in_schema=False)
def read_root():
    """
    Redirect the root URL to the interactive API documentation.
    """
    return RedirectResponse(url="/docs")

def get_type_by_identifier(identifier: str) -> str:
    """
    Super basic heuristic to distinguish IP, Hash, Domain.
    """
    # IP Address
    if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", identifier):
        return "ip"
    # File Hash (MD5, SHA-1, SHA-256)
    elif len(identifier) in (32, 40, 64) and re.match(r"^[a-fA-F0-9]+$", identifier):
        return "hash"
    # Assume domain otherwise
    else:
        return "domain"

@app.get("/api/v1/report/{identifier}")
async def get_report(identifier: str, force_refresh: bool = Query(False, description="Bypass cache and fetch directly from VirusTotal"), db: Session = Depends(get_db)):
    """
    Fetches VirusTotal data for an identifier (IP, Hash, or Domain).
    Caching Strategy:
    1. Check Memory Cache (fastest, TTL 60s)
    2. Check Database Cache (fast, TTL 24h)
    3. Fetch from VirusTotal API (slow, rate-limited)
    """
    # 1. Check in-memory cache
    if not force_refresh and identifier in memory_cache:
        val = memory_cache[identifier]
        val["source"] = "memory_cache"
        return val

    # 2. Check Database Cache
    db_record = db.query(models.VTRecord).filter(models.VTRecord.identifier == identifier).first()
    
    if db_record and not force_refresh:
        now = datetime.datetime.utcnow()
        if (now - db_record.last_updated).total_seconds() < DB_CACHE_TTL_HOURS * 3600:
            result = {
                "identifier": db_record.identifier,
                "type": db_record.type,
                "data": db_record.data,
                "last_updated": db_record.last_updated.isoformat(),
                "source": "database_cache"
            }
            # Update memory cache
            memory_cache[identifier] = result
            return result

    # 3. Not in cache, stale, or force refresh -> Fetch from VirusTotal
    id_type = get_type_by_identifier(identifier)
    
    vt_data = await fetch_vt_data(identifier, id_type)

    # 4. Save/Update in Database
    if db_record:
        db_record.data = vt_data
        db_record.last_updated = datetime.datetime.utcnow()
    else:
        db_record = models.VTRecord(
            identifier=identifier,
            type=id_type,
            data=vt_data
        )
        db.add(db_record)
    
    db.commit()
    db.refresh(db_record)
    
    result = {
        "identifier": db_record.identifier,
        "type": db_record.type,
        "data": db_record.data,
        "last_updated": db_record.last_updated.isoformat(),
        "source": "virustotal_api"
    }
    
    # 5. Update memory cache
    memory_cache[identifier] = result
    
    return result

@app.post("/api/v1/report/{identifier}/refresh")
async def refresh_report(identifier: str, db: Session = Depends(get_db)):
    """
    Explicit endpoint to re-ingest data for an identifier, bypassing cache.
    """
    return await get_report(identifier=identifier, force_refresh=True, db=db)
